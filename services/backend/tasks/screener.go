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
    Instances [][][]float64 `json:"instances"`
}

type PredictResponse struct {
    Scores [][]float64 `json:"predictions"`
}

func GetScreener(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    //extract args from frontend request
    var args GetScreenerArgs
    err := json.Unmarshal(rawArgs, &args)
    if err != nil {
        log.Printf("Error unmarshaling rawArgs: %v\n", err)
        return nil, err
    }
    //prepare ticker map
    tickerMap := make(map[int]string)
    rows, err := conn.DB.Query(context.Background(), "SELECT ticker_id, ticker FROM tickers")
    if err != nil {
        log.Printf("Error querying ticker info: %v\n", err)
        return nil, err
    }
    defer rows.Close()
    for rows.Next() {
        var tickerID int
        var ticker string
        if err := rows.Scan(&tickerID, &ticker); err != nil {
            log.Printf("Error scanning ticker info: %v\n", err)
            return nil, err
        }
        tickerMap[tickerID] = ticker
    }
    //iterate through requested setup
    var setups [][]interface{}
    for _, setupID := range args.Setups {
        //get setup metadata
        var threshold int
        var interval string
        err := conn.DB.QueryRow(context.Background(), "SELECT threshold, i FROM setups WHERE setup_id = $1", setupID).Scan(&threshold, &interval)
        if err != nil {
            log.Printf("Error querying setup info for setupID %d: %v\n", setupID, err)
            return nil, err
        }
        //fetch tensor from cache
        key := fmt.Sprintf("%s_screener", interval)
        tensorJson, err := conn.Cache.Get(context.Background(), key).Result()
        if err != nil {
            log.Printf("Error getting cache for interval %s: %v\n", interval, err)
            return nil, err
        }
        //unmarshal json response into tensor
        var tensor [][][]float64 //about 9000, 101, 4
        if err := json.Unmarshal([]byte(tensorJson), &tensor); err != nil {
            log.Printf("Error unmarshalling %v", err)
            return nil, err
        }
        //prepare prediction request
        req := PredictRequest{
            Instances: tensor,
        }
        jsonData, err := json.Marshal(req)
        if err != nil {
            fmt.Println("marhsal err")
            return nil, err
        }
        //send request to tensorflow serving container
        url := fmt.Sprintf("http://tf:8501/v1/models/%d:predict", setupID)
        fmt.Println(url)
        resp, err := http.Post(url, "application/json", bytes.NewBuffer(jsonData))
        if err != nil {
            log.Print("send err")
            return nil, err
        }
        //handle and deconde response
        defer resp.Body.Close()
        var predictResponse PredictResponse
        if err := json.NewDecoder(resp.Body).Decode(&predictResponse); err != nil {
            return nil, err
        }
        //compare scores to threshold and store in list
        //thresholdFloat := float64(threshold) / 100
        thresholdFloat := 0.315
        for i, dim := range predictResponse.Scores {
            score := dim[0]
            if score >= thresholdFloat {
                tickerID := int(tensor[i][0][3])
                ticker, ok := tickerMap[tickerID]
                if !ok {
                    fmt.Printf("ticker id %d not found", tickerID)
                    continue
                }
                setups = append(setups, []interface{}{ticker, score, setupID})
            }
        }


    }
    return setups, nil
}
