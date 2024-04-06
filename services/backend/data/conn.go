package data
 
import (
    "log"
    "context"
    "github.com/jackc/pgx/v4/pgxpool"
    "github.com/go-redis/redis/v8"
)

type Conn struct {
    DB *pgxpool.Pool
    Cache *redis.Client
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
    db, err := pgxpool.Connect(context.Background(), db_url)
    if err != nil {
        log.Fatalf("Unable to connect to database: %v\n", err)
    }
    cache := redis.NewClient(&redis.Options{Addr: cache_url,})
    err = cache.Ping(context.Background()).Err()
    if err != nil {
        log.Fatalf("Unable to connect to cache: %v\n", err)
    }
    return &Conn{DB: db, Cache: cache}
}
