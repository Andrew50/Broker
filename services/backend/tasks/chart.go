package tasks

import (
    "encoding/json"
    "github.com/jackc/pgx/v4"
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
    if i_num == "1" {
        aggregate = false
    }else{
        aggregate = true
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
    var sqlQuery string
    var rows pgx.Rows
    fmt.Println(a.T)
    fmt.Println(aggregate)
    if a.T.IsZero() {
        if aggregate {
            sqlQuery = fmt.Sprintf(`
                SELECT * FROM (
                    SELECT t.bucket, first(t.open, t.t), max(t.high), min(t.low), last(t.close, t.t), sum(t.volume)
                    FROM (
                        SELECT
                            time_bucket('%s', q.t) AS bucket, q.t, q.open, q.high, q.low, q.close, q.volume
                        FROM %s AS q
                        INNER JOIN tickers AS ti ON ti.ticker_id = q.ticker_id
                        WHERE ti.ticker = $1
                    ) AS t
                    GROUP BY t.bucket
                    ORDER BY t.bucket DESC
                    LIMIT $2
                ) AS f
                ORDER BY f.bucket ASC
                `, bucket, table)
        }else{
            sqlQuery = fmt.Sprintf(`
                SELECT * FROM (
                    SELECT q.t, q.open, q.high, q.low, q.close, q.volume
                    FROM %s AS q
                    INNER JOIN tickers AS ti ON ti.ticker_id = q.ticker_id
                    WHERE ti.ticker = $1
                    ORDER BY q.t DESC
                    LIMIT $2
                ) AS f
                ORDER BY f.t ASC
                `, table)
        }
        rows, err = conn.DB.Query(context.Background(), sqlQuery, a.Ticker, a.N)
    }else{
        if aggregate {
            sqlQuery = fmt.Sprintf(`
                SELECT * FROM (
                    SELECT t.bucket, first(t.open, t.t), max(t.high), min(t.low), last(t.close, t.t), sum(t.volume)
                    FROM (
                        SELECT 
                            time_bucket('%s', q.t) AS t, q.t, q.open, q.high, q.low, q.close, q.volume
                        FROM %s AS q
                        INNER JOIN tickers AS ti ON ti.ticker_id = q.ticker_id
                        WHERE ti.ticker = $1 AND q.t <= $2
                    ) AS f
                    GROUP BY f.t
                    ORDER BY f.t DESC
                    LIMIT $3
                ) AS f
                ORDER BY f.bucket ASC
                `, bucket, table)
        }else{
            sqlQuery = fmt.Sprintf(`
                SELECT * FROM (
                    SELECT q.t, q.open, q.high, q.low, q.close, q.volume
                    FROM %s AS q
                    INNER JOIN tickers AS ti ON ti.ticker_id = q.ticker_id
                    WHERE ti.ticker = $1 AND q.t <= $2
                    ORDER BY q.t DESC
                    LIMIT $3
                ) AS f
                ORDER BY f.t ASC
                `, table)
        }
        rows, err = conn.DB.Query(context.Background(), sqlQuery, a.Ticker, a.T, a.N)
    }
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
