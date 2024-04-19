package tasks

import (
    "encoding/json"
    "fmt"
    "api/data"
)


type GetTrainerArgs struct {
    }

func GetTrainer(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a GetTrainerArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("GetTrainer invalid args: %v", err)
    }
    return nil, nil
}


type SetTrainerArgs struct {
}

func SetTrainer(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    var a SetTrainerArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("SetTrainer invalid args: %v", err)
    }
    return nil, nil
}


type TrainModelArgs struct {
    SetupID int `json:"a1"`
}

func TrainModel(conn *data.Conn, user_id int, rawArgs json.RawMessage) (interface{}, error) {
    //if sample size < something return error !!!!!!!!!!!!!!
    var a TrainModelArgs
    if err := json.Unmarshal(rawArgs, &a); err != nil {
        return nil, fmt.Errorf("TrainModel invalid args: %v", err)
    }
    id, err := data.Queue(conn, 1, "trainer-train", []interface{}{user_id, a.SetupID})
    if err != nil {
        return nil, err
    }
    return data.Poll(conn, id)
}
