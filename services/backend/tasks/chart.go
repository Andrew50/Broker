package tasks

import (
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

func getQuery(i_num string, i_base string, pm string) (table string, bucket string, aggregate bool, err error) {
    switch i_base {
        case "":
            bucket = fmt.Sprintf("%s minute", i_num)
            table = "quotes_1_extended"
        case "h":
            bucket = fmt.Sprintf("%s hour", i_num)
            if pm == "true" {
                table = "quotes_h_pm"
            }else if pm == "false" {
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


func GetChart(conn *data.Conn, user_id int, args []string) (interface{}, error) {


    //args = ticker, i(interval), t(datetime/timestamp), n(bars), pm(pre market)
    //interval bases : none(minute), h(hour), d(day), w(week), m(month), y(year)
    if len(args) != 5 {
        return nil, fmt.Errorf("expected 5 arguments, got %d", len(args))
    }
    ticker, i, t, n, pm := args[0], args[1], args[2], args[3], args[4]
    i_num, i_base, err := parseInterval(i)
    if err != nil {
        return nil, err
    }
    table, bucket, aggregate, err := getQuery(i_num, i_base, pm)
    if err != nil {
        return nil, err
    }
    var sqlQuery string
    var rows pgx.Rows
    if t != "" {
        if aggregate {
            sqlQuery = fmt.Sprintf(`
                SELECT t.bucket, first(t.open, t.t), max(t.high), min(t.low), last(t.close, t.t), sum(t.volume)
                FROM (
                    SELECT 
                        time_bucket('%s', q.t) AS bucket, q.t, q.open, q.high, q.low, q.close, q.volume
                    FROM %s AS q
                    INNER JOIN tickers AS ti ON ti.ticker_id = q.ticker_id
                    WHERE ti.ticker = $1 AND q.t <= $2
                ) AS t
                GROUP BY t.bucket
                ORDER BY t.bucket
                LIMIT $3`, bucket, table)
        }else{
            sqlQuery = fmt.Sprintf(`
                SELECT q.t, q.open, q.high, q.low, q.close, q.volume
                FROM %s AS q
                INNER JOIN tickers AS ti ON ti.ticker_id = q.ticker_id
                WHERE ti.ticker = $1 AND q.t <= $2
                ORDER BY q.t DESC
                LIMIT $3`, table)
        }
        rows, err = conn.DB.Query(context.Background(), sqlQuery, ticker, t, n)
    }else{
        if aggregate {
            sqlQuery = fmt.Sprintf(`
                SELECT t.bucket, first(t.open, t.t), max(t.high), min(t.low), last(t.close, t.t), sum(t.volume)
                FROM (
                    SELECT
                        time_bucket('%s', q.t) AS bucket, q.t, q.open, q.high, q.low, q.close, q.volume
                    FROM %s AS q
                    INNER JOIN tickers AS ti ON ti.ticker_id = q.ticker_id
                    WHERE ti.ticker = $1
                ) AS t
                GROUP BY t.bucket
                ORDER BY t.bucket
                LIMIT $2`, bucket, table)
        }else{
            sqlQuery = fmt.Sprintf(`
                SELECT q.t, q.open, q.high, q.low, q.close, q.volume
                FROM %s AS q
                INNER JOIN tickers AS ti ON ti.ticker_id = q.ticker_id
                WHERE ti.ticker = $1
                ORDER BY q.t DESC
                LIMIT $2`, table)
        }
        rows, err = conn.DB.Query(context.Background(), sqlQuery, ticker, n)
    }
    if err != nil {
        return nil, fmt.Errorf("query execution error: %v", err)
    }
    defer rows.Close()
    var results [][]float64
    for rows.Next() {
        var bucket time.Time
        var open, high, low, close, volume float64
        if err := rows.Scan(&bucket, &open, &high, &low, &close, &volume); err != nil {
            return nil, fmt.Errorf("error scanning row: %v", err)
        }
        results = append(results, []float64{float64(bucket.Unix()), open, high, low, close, volume})
    }

    return results, nil
}
