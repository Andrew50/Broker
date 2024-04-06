package main

import (
    "fmt"
    "os"
    "api/tasks"
    "encoding/json"
    "log"
    "net/http"
    "api/data"
)

type Request struct {
    Function string `json:"function"`
    Arguments []string `json:"arguments"`
}

var privateFunc = map[string]func(*data.Conn, int, []string) (interface{}, error){
    "getJournal": tasks.GetJournal,
    "setJournal": tasks.SetJournal,
    "getChart": tasks.GetChart,
}

var publicFunc = map[string]func(*data.Conn, []string) (interface{}, error) {
    "signup": Signup,
    "login": Login,
}

func addCORSHeaders(w http.ResponseWriter) {
    w.Header().Set("Access-Control-Allow-Origin", "*")
    w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE")
    w.Header().Set("Access-Control-Allow-Headers", "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization")
}

func handleError(w http.ResponseWriter, err error, context string) bool {
    if err != nil {
        logMessage := fmt.Sprintf("Error in %s: %v", context, err)
        fmt.Println(logMessage)
        http.Error(w, logMessage, http.StatusBadRequest)
        return true
    }
    return false
}

func public_handler(conn *data.Conn) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        addCORSHeaders(w)
        if r.Method == "OPTIONS" {
            return
        }
        var req Request
        err := json.NewDecoder(r.Body).Decode(&req)
        if handleError(w, err, "decoding request") {
            return
        }
        if function, ok := publicFunc[req.Function]; ok {
            result, err := function(conn, req.Arguments)
            if handleError(w, err, fmt.Sprintf("executing function %s", req.Function)) {
                return
            }
            err = json.NewEncoder(w).Encode(result)
            if handleError(w, err, "encoding response") {
                return
            }
            return
        } else {
            http.Error(w, fmt.Sprintf("invalid function: %s", req.Function), http.StatusBadRequest)
            return
        }
    }
}

func private_handler(conn *data.Conn) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        addCORSHeaders(w)
        if r.Method != "POST" {
            return 
        }
        token_string := r.Header.Get("Authorization")
        user_id, err := validate_token(token_string)
        if handleError(w, err, "validating token") {
            return
        }
        var req Request
        err = json.NewDecoder(r.Body).Decode(&req)
        if handleError(w, err, "decoding request") {
            return
        }
        if function, ok := privateFunc[req.Function]; ok {
            result,err := function(conn,user_id, req.Arguments)
            if handleError(w, err, fmt.Sprintf("executing function %s", req.Function)) {
                return
            }
            err = json.NewEncoder(w).Encode(result)
            if handleError(w, err, "encoding response") {
                return
            }
        } else {
            http.Error(w, fmt.Sprintf("invalid function: %s", req.Function), http.StatusBadRequest)
            return
        }
    }
}

func main() {
    _, exists := os.LookupEnv("IN_CONTAINER")
    conn := data.GetConn(exists)
    defer conn.DB.Close()
    http.HandleFunc("/public", public_handler(conn))
    http.HandleFunc("/private", private_handler(conn))
    fmt.Println("Server running on port 5057")
    if err := http.ListenAndServe(":5057",nil); err != nil {
        log.Fatal(err)
    }
}
