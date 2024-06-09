package data
 
import (
    "log"
    "context"
    "github.com/jackc/pgx/v4/pgxpool"
    "github.com/redisAI/redisai-go/redisai"
    "github.com/go-redis/redis/v8"
    "time"
    //"strings"
)

type Conn struct {
    DB *pgxpool.Pool
    Cache *redis.Client
    AI *redisai.Client
}

func GetConn(container bool) *Conn {
    var db_url string
    var cache_url string
    if container {
        db_url = "postgres://postgres:pass@db:5432"
        cache_url="redis:6379"
    } else {
        db_url = "postgres://postgres:pass@localhost:5432"
        cache_url="localhost:6379"
    }
    var db *pgxpool.Pool
    var err error
    for true {
        db, err = pgxpool.Connect(context.Background(), db_url)
        if err != nil {
            //if strings.Contains(err.Error(), "the database system is starting up") {
            if true{
                log.Println("waiting for db")
            } else {
                log.Fatalf("Unable to connect to database: %v\n", err)
            }
            time.Sleep(5 * time.Second)
        } else {
            break
        }
    }
    cache := redis.NewClient(&redis.Options{Addr: cache_url,})
    err = cache.Ping(context.Background()).Err()
    if err != nil {
        log.Fatalf("Unable to connect to cache: %v\n", err)
    }
    return &Conn{DB: db, Cache: cache}
}
