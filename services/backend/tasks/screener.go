package tasks

import (
    "api/data"
    "encoding/json"
    //"github.com/google/uuid"
)

type GetScreenerArgs struct {
    Setups []string `json:"a1"`
}

func GetScreener(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var args GetScreenerArgs
    err := json.Unmarshal(rawArgs, &args)
    if err != nil {
        return nil, err
    }
    return nil, nil
    /*var scores []float32
    for _, setup := range args.Setups {
        id := uuid.New().String()
        _, err = conn.AI.ModelExecute(setup, "1d_screener", id)
        if err != nil {
            return nil, err
        }
        result, err := conn.AI.TensorGet(id)
        if err != nil {
            return nil, err
        }
        scores = append(scores, result)
    }
    var results []string
    for _, score := range scores {
        if score > threshold {
            results = append(results, ticker)
        }
    }



    return result, nil
    */
}
