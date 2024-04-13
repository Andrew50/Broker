package tasks

import (
    "api/data"
    "fmt"
    "context"
    "encoding/json"
    "github.com/jackc/pgx/v4"
    "time"
)

type GetAnnotationsArgs struct {
    T time.Time `json:"a1"`
    N int `json:"a2"`
}
func GetAnnotations(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a GetAnnotationsArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("GetAnnotations invalid args: %v", err)
    }

    var rows pgx.Rows;
    var err error;
    if a.T.IsZero() {
        rows, err = conn.DB.Query(context.Background(),
            `SELECT a.t,  t.ticker, s.setup_name, a.completed, a.annotation_id
            FROM annotations AS a
            INNER JOIN setups AS s ON a.setup_id = s.setup_id
            INNER JOIN tickers AS t ON a.ticker_id = t.ticker_id
            WHERE a.user_id = $1
            ORDER BY a.t DESC 
            LIMIT $2`, user_id, a.N)
    } else {
        rows, err = conn.DB.Query(context.Background(),
            `SELECT a.t,  t.ticker, s.setup_name, a.completed, a.annotation_id
            FROM annotations AS a
            INNER JOIN setups AS s ON a.setup_id = s.setup_id
            INNER JOIN tickers AS t ON a.ticker_id = t.ticker_id
            WHERE a.user_id = $1 AND a.t < $2
            ORDER BY a.t DESC 
            LIMIT $3`, user_id, a.T, a.N)
    }
    if err != nil {
        return nil, fmt.Errorf("GetAnnotations: %v", err)
    }
    defer rows.Close()
    var annotations [][]interface{}
    for rows.Next() {
        var annotation_id, ticker_id, t, completed,setup_name interface{}
        err = rows.Scan(&annotation_id, &ticker_id, &t,&completed, &setup_name)
        if err != nil {
            return nil, fmt.Errorf("GetAnnotations: %v", err)
        }
        annotations = append(annotations, []interface{}{annotation_id, ticker_id, t,completed, setup_name})
    }
    if err = rows.Err(); err != nil {
        return nil, fmt.Errorf("GetAnnotations: %v", err)
    }
    return annotations, nil
}

type DelAnnotationArgs struct {
    Annotation_id int `json:"a1"`
}
func DelAnnotation(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a DelAnnotationArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("DelAnnotation invalid args: %v", err)
    }

    // Check if the annotation_id is provided
    if a.Annotation_id == 0 {
        return nil, fmt.Errorf("DelAnnotation requires a valid annotation_id")
    }

    // Prepare and execute the delete statement
    cmdTag, err := conn.DB.Exec(context.Background(), "DELETE FROM annotations WHERE annotation_id = $1 AND user_id = $2", a.Annotation_id, user_id)
    if err != nil {
        return nil, fmt.Errorf("DelAnnotation execution failed: %v", err)
    }

    // Check if any rows were affected to ensure the annotation_id existed and was deleted
    if cmdTag.RowsAffected() == 0 {
        return nil, fmt.Errorf("DelAnnotation no annotation found with the provided annotation_id and user_id")
    }

    return "success", nil
}

type SetAnnotationArgs struct {
    Annotation_id int `json:"a1"`
    Entry string `json:"a2"`
}
func SetAnnotation(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var args SetAnnotationArgs
    if err := json.Unmarshal(rawArgs, &args); err != nil {
        return nil, fmt.Errorf("SetAnnotation invalid args: %v", err)
    }

    if args.Annotation_id == 0 {
        // Handle case where annotation_id is not provided if necessary
        return nil, fmt.Errorf("SetAnnotation requires a valid annotation_id")
    }

    // Execute the update statement directly without preparing it
    cmdTag, err := conn.DB.Exec(context.Background(), "UPDATE annotations SET entry = $1, completed = true WHERE annotation_id = $2 AND user_id = $3", args.Entry, args.Annotation_id, user_id)
    if err != nil {
        return nil, fmt.Errorf("SetAnnotation execution failed: %v", err)
    }

    // Check if any rows were affected, this ensures the annotation_id existed
    if cmdTag.RowsAffected() == 0 {
        return nil, fmt.Errorf("SetAnnotation no annotation found with the provided annotation_id and user_id")
    }

    return "success", nil
}


type NewAnnotationArgs struct {
    Ticker string `json:"a1"`
    SetupID int `json:"a2"`
    T time.Time `json:"a3"`
}
func NewAnnotation(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a NewAnnotationArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("NewAnnotation invalid args: %v", err)
    }
    _, err := conn.DB.Exec(context.Background(), `
        INSERT INTO annotations (user_id, setup_id, ticker_id, t)
        SELECT $1, $2, tickers.ticker_id, $3
        FROM tickers WHERE ticker = $4`, user_id, a.SetupID, a.T, a.Ticker)
    if err != nil {
        return nil, fmt.Errorf("NewAnnotation: %v", err)
    }
    return "succes" , nil
}

type GetAnnotationEntryArgs struct {
    Annotation_id int `json:"a1"`
}
func GetAnnotationEntry(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a GetAnnotationEntryArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("GetAnnotationEntry invalid args: %v", err)
    }
    var entry string
    err := conn.DB.QueryRow(context.Background(), `SELECT entry FROM annotations WHERE annotation_id = $1`, a.Annotation_id).Scan(&entry)
    if err != nil {
        if err == pgx.ErrNoRows {
            return nil, fmt.Errorf("GetAnnotationEntry: no entry found for given ID")
        }
        return nil, fmt.Errorf("GetAnnotationEntry: %v", err)
    }
    return entry, nil
}
