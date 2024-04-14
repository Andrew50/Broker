package data


import (
    "time"
)

func StartScheduler(conn *Conn) chan struct{} {
    ticker := time.NewTicker(1 * time.Minute)
    quit := make(chan struct{})
    location, err := time.LoadLocation("EST")
    if err != nil {
        panic(err)
    }
    go func() {
        for {
            select {
            case <-ticker.C:
                now := time.Now().In(location)
                if c := checkSchedule(now); c != 0 {
                    Queue(conn, 1, "update-update", []interface{}{c})
                }
            case <-quit:
                ticker.Stop()
                return
            }
        }
    }()
    return quit // Returning the channel allows the caller to stop the scheduler
}

// handleScheduling decides which task to run based on the current time.
func checkSchedule(now time.Time) int {
    //type 0 = no update
    //type 1 = pull cp, append to quotes, refresh aggregates, update screener tensor
    //type 2 = new tickers, new journal, clear task results and temp stuff (anything thats just a uuid)
    year, month, day := now.Date()
    startMorning := time.Date(year, month, day, 9, 0, 0, 0, now.Location())
    endMorning := time.Date(year, month, day, 9, 30, 0, 0, now.Location())
    endDay := time.Date(year, month, day, 16, 0, 0, 0, now.Location())
    if now.After(startMorning) && now.Before(endMorning) {
        return 1
    }
    if now.After(endMorning) && now.Before(endDay) && (now.Minute() == 0 || now.Minute() == 30) {
        return 1
    }
    if (now.Hour() == 21 && now.Minute() == 0) {
        return 1
    }
    if (now.Hour() == 0 && now.Minute() == 0) {
        return 2
    }
    return 0
}
