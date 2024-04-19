package tasks

import (
    "api/data"
    "errors"
    "encoding/json"
    "github.com/google/uuid"
    "context"
)

type GetScreenerArgs struct {
    Setups []int `json:"a1"`
}

func GetScreener(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var args GetScreenerArgs
    err := json.Unmarshal(rawArgs, &args)
    if err != nil {
        return nil, err
    }

    var keys [][]interface{}
    cmd := conn.Cache.Get(context.Background(),"1d_screener_key")
    if cmd.Err() != nil {
        return nil, cmd.Err()
    }
    val, err := cmd.Bytes()
    if err != nil {
        return nil, err
    }
    if err := json.Unmarshal(val, &keys); err != nil {
        return nil, err
    }

    var setups [][]interface{}
    for _, setupID := range args.Setups {
        var threshold int
        var interval string
        err := conn.DB.QueryRow(context.Background(), "SELECT threshold, interval FROM setups WHERE setup_id = $1", setupID).Scan(&threshold, &interval)
        if err != nil {
            return nil, err
        }
        thresholdFloat := float64(threshold) / 100.0
        
        modelKey := string(setupID)
        inputTensorKey := interval + "_screener"
        outputTensorKey := uuid.New().String() 

        err = conn.AI.ModelRun(modelKey, []string{inputTensorKey}, []string{outputTensorKey})
        if err != nil {
            return nil, err
        }
        dt, shape, rawResult, err := conn.AI.TensorGetValues(outputTensorKey)
        if err != nil {
            return nil, err
        }
        if dt != "float32" || len(shape) != 1 {
            err = errors.New("unexpected tensor shape or data type")
            return nil, err
        }

        result, ok := rawResult.([]float32)
        if !ok {
            err = errors.New("bad conversion to float32 slice")
            return nil, err
        }
        

        for i, score := range result {
            if float64(score) >= thresholdFloat { 
                if i < len(keys) {
                    setups = append(setups, keys[i])
                }else{
                    err = errors.New("index out of range")
                    return nil, err
                }
            }
        }
    }
    return setups, nil
}
