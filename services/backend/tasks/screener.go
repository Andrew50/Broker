package tasks

import (
    "api/data"
    "errors"
    "encoding/json"
    "context"
    "fmt"
    "net/http"
    "bytes"
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
        var tensor json.RawMessage
        err = conn.Cache.Get(context.Background(), fmt.Sprintf("%s_screener",interval)).Scan(&tensor)
        if err != nil {
            return nil, err
        }
        //assuming tensor is already json
        requestBody, err := json.Marshal(map[string]interface{}{
            "instances": []map[string]interface{}{{"input_tensor": tensor}},
        })
        url := fmt.Sprintf("http://tf:8501/v1/models/%s:predict",setupID)
        response, err := http.Post(url, "application/json", bytes.NewBuffer(requestBody))
        if err != nil {
            return nil, err
        }
        defer response.Body.Close()
        var result struct {
            Predictions [][]float64 `json:"predictions"`
        }
        if err := json.NewDecoder(response.Body).Decode(&result); err != nil {
            return nil, err
        }
        thresholdFloat := float64(threshold) / 100
        for i, row := range result.Predictions {
            score := row[0]
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
