package tasks

import (
    "api/data"
    "encoding/json"
    "context"
    "fmt"
    "log"
    "net/http"
    "bytes"
)

type GetScreenerArgs struct {
    Setups []int `json:"a1"`
}

type PredictRequest struct { 
    Instances []map[string]interface{} `json:"instances"`
}

type PredictResponse struct {
    Scores [][][]float64 `json:"predictions"`
}

func GetScreener(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var args GetScreenerArgs
    err := json.Unmarshal(rawArgs, &args)
    if err != nil {
        log.Printf("Error unmarshaling rawArgs: %v\n", err)
        return nil, err
    }

    var setups [][]interface{}
    for _, setupID := range args.Setups {
        var threshold int
        var interval string
        err := conn.DB.QueryRow(context.Background(), "SELECT threshold, i FROM setups WHERE setup_id = $1", setupID).Scan(&threshold, &interval)
        if err != nil {
            log.Printf("Error querying setup info for setupID %d: %v\n", setupID, err)
            return nil, err
        }
        tensorJson, err := conn.Cache.Get(context.Background(), fmt.Sprintf("%s_screener", interval)).Result()
        if err != nil {
            log.Printf("Error getting cache for interval %s: %v\n", interval, err)
            return nil, err
        }

        var tensor [][][]float64
        if err := json.Unmarshal([]byte(tensorJson), &tensor); err != nil {
            log.Printf("Error unmarshalling %v", err)
            return nil, err
        }
        req := PredictRequest{
            Instances: []map[string]interface{}{
                {"input_tensor": tensor},
            },
        }

        jsonData, err := json.Marshal(req)
        if err != nil {
            fmt.Println("marhsal err")
            return nil, err
        }

        url := "http://localhost:8501/v1/models/my_model:predict"
        resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
        if err != nil {
            log.Print("send err")
            return nil, err
        }
        defer resp.Body.Close()

        var predictResponse PredictResponse
        if err := json.NewDecoder(resp.Body).Decode(&predictResponse); err != nil {
            return nil, err
        }
        fmt.Println("scores:", predictResponse.Scores)

        /*tensorContent := tensorProto.TensorContent
        tickerKey := []float64{}
        buffer := bytes.NewReader(tensorContent)

        for buffer.Len() > 0 {
            var value float64
            err := binary.Read(buffer,binary.LittleEndian, &value)
            if err != nil {
                return nil, err
            }
            tickerKey = append(tickerKey, value)
        /*tickerKey := make([]float64, len(tensor))
        for i := range predictions {
            tickerKey[i] = tensor[i][0][3]
        }

        thresholdFloat := float64(threshold) / 100
        for i, score := range predictions {
            if score >= thresholdFloat {
                ticker := tickerKey[i]
                setups = append(setups, []interface{}{ticker, score, setupID})
            }
        }*/
    }
    return setups, nil
}

