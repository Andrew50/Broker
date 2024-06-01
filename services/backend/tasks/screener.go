package tasks

import (
    "api/data"
    "encoding/json"
    "context"
    "fmt"
    "net/http"
    "bytes"
    "encoding/base64"
)

type GetScreenerArgs struct {
    Setups []int `json:"a1"`
}
/*
#    tensorJson, helperJson = data.cache.get(f'{interval}_screener'), data.cache.get(f'{interval}_screener_helper')
    #if tensorJson is None or helperJson is None:
#    cacheExists = False
    #else:
#        tensor_binary = base64.b64decode(tensorJson)
#        helper_binary = base64.b64decode(helperJson)
#        tensor = np.load(io.BytesIO(tensor_binary))
#        helper = np.load(io.BytesIO(helper_binary))
*/

func GetScreener(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var args GetScreenerArgs
    err := json.Unmarshal(rawArgs, &args)
    if err != nil {
        return nil, err
    }
    /*
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
    */
    var setups [][]interface{}
    for _, setupID := range args.Setups {
        var threshold int
        var interval string
        err := conn.DB.QueryRow(context.Background(), "SELECT threshold, i FROM setups WHERE setup_id = $1", setupID).Scan(&threshold, &interval)
        if err != nil {
            return nil, err
        }
        /*
        var tensor json.RawMessage
        err = conn.Cache.Get(context.Background(), fmt.Sprintf("%s_screener",interval)).Scan(&tensor)
        if err != nil {
            return nil, err
        }
        //assuming tensor is already json
        */
        tensorBin, err := conn.Cache.Get(context.Background(), fmt.Sprintf("%s_screener",interval)).Result()
        if err != nil {
            return nil, err
        }
        tensorJson, err := base64.StdEncoding.DecodeString(tensorBin)
        if err != nil {
            return nil, err
        }

        requestBody, err := json.Marshal(map[string]interface{}{
            "instances": []map[string]interface{}{{"input_tensor": tensorJson}},
        })
        url := fmt.Sprintf("http://tf:8501/v1/models/%d:predict",setupID)
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
        var tensor [][][]float64
        if err := json.Unmarshal(tensorJson, &tensor); err != nil {
            return nil, err 
        }
        //tickerKey = tensor[:,0,3]
        tickerKey := make([]float64, len(tensor))
        for i := range tensor {
            tickerKey[i] = tensor[i][0][3]
        }
        thresholdFloat := float64(threshold) / 100
        for i, row := range result.Predictions {
            score := row[0]
            if float64(score) >= thresholdFloat { 
                ticker := tickerKey[i]
                setups = append(setups,[]interface{}{ticker, score, setupID})
            }
        }
    }
    return setups, nil
}
