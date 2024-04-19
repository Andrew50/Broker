package tasks

import (
    "api/data"
    "time"
    "encoding/json"
    "fmt"
    "github.com/jackc/pgx/v4"
    "context"
)

type GetJournalsArgs struct {
    T time.Time `json:"a1"`
}
func GetJournals(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a GetJournalsArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("NewJournal invalid args: %v", err)
    }

    var rows pgx.Rows;
    var err error;
    if a.T.IsZero() {
        rows, err = conn.DB.Query(context.Background(),"SELECT t, completed, journal_id FROM journals WHERE user_id = $1 ORDER BY t DESC", user_id)
    } else {
        rows, err = conn.DB.Query(context.Background(),"SELECT t, completed, journal_id FROM journals WHERE user_id = $1 AND t < $2 ORDER BY t DESC", user_id, a.T) 
    }
    if err != nil {
        return nil, fmt.Errorf("GetJournals failed: %v", err)
    }
    defer rows.Close()
    var journals [][]interface{}
    var t time.Time
    var completed bool
    var journal_id int
    for rows.Next() {
        err = rows.Scan(&t, &completed, &journal_id)
        if err != nil {
            return nil, fmt.Errorf("GetJournals: %v", err)
        }
        journals = append(journals, []interface{}{t,completed, journal_id})
    }
    if err = rows.Err(); err != nil {
        return nil, fmt.Errorf("GetJournals: %v", err)
    }
    return journals, nil
}

type SetJournalArgs struct {
    Journal_id int `json:"a1"`
    Entry string `json:"a2"`
}
func SetJournal(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var args SetJournalArgs
    if err := json.Unmarshal(rawArgs, &args); err != nil {
        return nil, fmt.Errorf("SetJournal invalid args: %v", err)
    }

    if args.Journal_id == 0 {
        return nil, fmt.Errorf("SetJournal requires a valid journal_id")
    }

    //you need user id to make sure someone isnt able to just choose any journal id, it has to be theirs
    cmdTag, err := conn.DB.Exec(context.Background(), "UPDATE journals SET entry = $1, completed = true WHERE journal_id = $2 AND user_id = $3", args.Entry, args.Journal_id, user_id)
    if err != nil {
        return nil, fmt.Errorf("SetJournal execution failed: %v", err)
    }

    if cmdTag.RowsAffected() == 0 {
        return nil, fmt.Errorf("SetJournal no journal found with the provided journal_id and user_id")
    }
    return "success", nil
}

type GetJournalEntryArgs struct {
    Journal_id int `json:"a1"`
}
func GetJournalEntry(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a GetJournalEntryArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("GetJournalEntry invalid args: %v", err)
    }
    var entry string
    err := conn.DB.QueryRow(context.Background(), `SELECT entry FROM journals WHERE journal_id = $1`, a.Journal_id).Scan(&entry)
    if err != nil {
        if err == pgx.ErrNoRows {
            return nil, fmt.Errorf("GetJournalEntry: no entry found for given ID")
        }
        return nil, fmt.Errorf("GetJournalEntry: %v", err)
    }
    return entry, nil
}
