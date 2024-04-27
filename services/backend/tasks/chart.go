package tasks

import (
    "encoding/json"
    "time"
    "context"
    "api/data"
    "fmt"
    "regexp"
)

func parseInterval(i string) (string, string, error) {
    re := regexp.MustCompile(`(\d+)([a-zA-Z]*)`)
    match := re.FindStringSubmatch(i)
    if len(match) == 0 {
        return "", "", fmt.Errorf("invalid interval")
    }
    return match[1], match[2], nil
}


func getQuery(i_num string, i_base string, pm bool) (table string, bucket string, aggregate bool, err error) {
    switch i_base {
        case "":
            bucket = fmt.Sprintf("%s minute", i_num)
            table = "quotes_1_extended"
        case "h":
            bucket = fmt.Sprintf("%s hour", i_num)
            if pm{
                table = "quotes_h_pm"
            }else{
                table = "quotes_h"
            }
        case "d":
            bucket = fmt.Sprintf("%s day", i_num)
            table = "quotes_d"
        case "w":
            bucket = fmt.Sprintf("%s week", i_num)
            table = "quotes_w"
        case "m":
            bucket = fmt.Sprintf("%s month", i_num)
            table = "quotes_w" //possbile change once we have quotes_m
        case "y":
            bucket = fmt.Sprintf("%s year", i_num)
            table = "quotes_w" //possbile change once we have quotes_y
        default:
            err = fmt.Errorf("invalid interval base: %s", i_base)
    }
    if i_num != "1" || i_base == "m" || i_base == "y"{ 
        aggregate = true
    }else{
        aggregate = false
    }
    return
}

type GetChartArgs struct {
    Ticker string `json:"a1"`
    I string `json:"a2"`
    T time.Time `json:"a3"`
    N int `json:"a4"`
    PM bool `json:"a5"`
}

func GetChart(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a GetChartArgs
    err := json.Unmarshal(rawArgs, &a)
    if err != nil{
        return nil, fmt.Errorf("invalid arguments")
    }
    i_num, i_base, err := parseInterval(a.I)
    if err != nil {
        return nil, err
    }
    table, bucket, aggregate, err := getQuery(i_num, i_base, a.PM)
    if err != nil {
        return nil, err
    }
    var tickerID int
    err = conn.DB.QueryRow(context.Background(),"SELECT ticker_id FROM tickers WHERE ticker = $1 ",a.Ticker).Scan(&tickerID)
    if err != nil {
        return nil, err
    }

    var query string
    var args []interface{}
    if aggregate {
       query += fmt.Sprintf("SELECT time_bucket('%s', t) AS bucket, first(open, t), max(high), min(low), last(close, t), sum(volume) ",bucket)
    }else{
       query += "SELECT t as bucket, open, high, low, close, volume "
    }
    query += fmt.Sprintf("FROM %s WHERE ticker_id = $1 ",table)
    args = append(args, tickerID)
    if !a.T.IsZero() {
        query += " AND bucket <= $2 "
        args = append(args, a.T)
    }
    if !a.PM && i_base == "" {
        query += "AND extended_hours = true "
    }
    if aggregate {
        query += "GROUP BY bucket "
    }
    query += fmt.Sprintf(`ORDER BY bucket DESC
            LIMIT $%d`, len(args) + 1)
    args = append(args, a.N)

    rows, err := conn.DB.Query(context.Background(), query, args...)
    if err != nil {
        return nil, fmt.Errorf("query execution error: %v", err)
    }
    defer rows.Close()
    var results [][]interface{}
    for rows.Next() {
        var bucket time.Time
        var open, high, low, close, volume float64
        if err := rows.Scan(&bucket, &open, &high, &low, &close, &volume); err != nil {
            return nil, fmt.Errorf("error scanning row: %v", err)
        }
        results = append(results, []interface{}{bucket, open, high, low, close, volume})
    }

    return results, nil
}
