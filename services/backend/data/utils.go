package data

import (
    "context"
    "time"
    "encoding/json"
    "github.com/google/uuid"
    "fmt"
)

type QueueArgs struct {
    ID string `json:"id"`
    Func string `json:"func"`
    Args []interface{} `json:"args"`
}

func Queue (conn *Conn, queueNum int, funcName string, args []interface{}) (string, error) {
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

    queue := fmt.Sprintf("task_queue_%d", queueNum)
    if err := conn.Cache.LPush(context.Background(), queue, serializedTask).Err(); err != nil {
        return "", err
    }

    return id, nil
}

func Poll (conn *Conn, taskID string) (interface{}, error) {
    var result interface{}
    start := time.Now()
    for time.Now().Sub(start) < 100 * time.Second{
        result = conn.Cache.Get(context.Background(), taskID).Val()
        if result != nil {
            conn.Cache.Del(context.Background(), taskID)
            return result, nil
        }
        time.Sleep(300 * time.Millisecond)
    }
    return nil, fmt.Errorf("timeout")
}
