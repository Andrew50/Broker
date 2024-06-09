package tasks

import (
    "api/data"
    "encoding/json"
)

func Update(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    data.Queue(conn, 1, "update-update", []interface{}{1})
    return nil, nil
}
