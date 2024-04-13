package data

import (
    "context"
    "encoding/json"
    "github.com/google/uuid"
)

type QueueArgs struct {
    ID string `json:"id"`
    Func string `json:"func"`
    Args []interface{} `json:"args"`
}

func Queue (conn *Conn, funcName string, args []interface{}) (string, error) {
    id := uuid.New().String()
    taskArgs := QueueArgs{
        ID: id,
        Func: funcName,
        Args: args,
    }
    serializedTask, err := json.Marshal(taskArgs)
    if err != nil {
        return "", err
    }

    if err := conn.Cache.LPush(context.Background(), "task_queue_1", serializedTask).Err(); err != nil {
        return "", err
    }

    //long polling
    return "", nil
}

func Poll (conn *Conn, taskID string) (interface{}, error) {
    var result interface{}
    for true {
        result = conn.Cache.Get(context.Background(), taskID).Val()
        if result != nil {
            break
        }
    }
    return result, nil
}
