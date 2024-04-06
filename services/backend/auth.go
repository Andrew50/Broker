package main 

import (
    "context"
    "api/data"
    "github.com/golang-jwt/jwt/v4"
    "time"
    "fmt"
)

var private_key = []byte("2dde9fg9")

type Claims struct {
    UserID int `json:"user_id"`
    jwt.RegisteredClaims
}


type Setup struct {
    SetupId int `json:"setup_id"`
    SetupName string `json:"setup_name"`
    Score int `json:"score"`
    I string `json:"i"`
    Bars int `json:"bars"`
    Threshold int `json:"threshold"`
    DolVol float64 `json:"dol_vol"`
    Adr float64 `json:"adr"`
    Mcap float64 `json:"mcap"`
}

type LoginResponse struct {
    Token string `json:"token"`
    Settings string `json:"settings"`
    Setups []Setup `json:"setups"`
}

func Signup(conn *data.Conn, args []string) (interface{}, error) {
    if len(args) != 2 {
        return "", fmt.Errorf("expected 2 arguments, got %d", len(args))
    }
    _, err := conn.DB.Exec(context.Background(), "INSERT INTO users (username, password) VALUES ($1, $2)", args[0], args[1])
    if err != nil {
        return "", err
    }
    result, err := Login(conn, args)
    return result, err
}

func Login(conn *data.Conn, args []string) (interface{}, error) {
    if len(args) != 2 {
        return "", fmt.Errorf("expected 2 arguments, got %d", len(args))
    }
    var user_id int
    var settings string
    var setups []Setup
    err := conn.DB.QueryRow(context.Background(), "SELECT user_id, settings FROM users WHERE username=$1 AND password=$2", args[0], args[1]).Scan(&user_id, &settings)
    if err != nil {
        return nil, err
    }
    token, err := create_token(user_id)
    if err != nil {
        return nil, err
    }
    rows, err := conn.DB.Query(context.Background(), "SELECT setup_id, setup_name, score, i, bars, threshold, dolvol, adr, mcap FROM setups WHERE user_id=$1", user_id)
    if err != nil {
        return nil, err
    }
    defer rows.Close()
    for rows.Next() {
        var row Setup
        if err := rows.Scan(&row.SetupId, &row.SetupName, &row.Score, &row.I, &row.Bars, &row.Threshold, &row.DolVol, &row.Adr, &row.Mcap); err != nil {
            return nil, err
        }
        setups = append(setups, row)
    }
    err = rows.Err()
    result := LoginResponse{Token: token, Settings: settings, Setups: setups}
    return result, err
}

func create_token(user_id int) (string, error) {
    expirationTime := time.Now().Add(1 * time.Hour)
    claims := &Claims{
        UserID: user_id,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(expirationTime),
        },
    }
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(private_key)
}

func validate_token(tokenString string) (int, error) {
    claims := &Claims{} // Initialize an instance of your Claims struct
    token, err := jwt.ParseWithClaims(tokenString, claims, func(token *jwt.Token) (interface{}, error) {
        return private_key, nil // Adjust this to match your token's signing method
    })
    if err != nil {
        return -1, fmt.Errorf("cannot parse token: %w", err)
    }
    if !token.Valid {
        return -1, fmt.Errorf("invalid token")
    }
    return claims.UserID, nil
}


