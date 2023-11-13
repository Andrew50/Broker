from tasks.Data import Database, Dataset, Cache
import uvicorn

if __name__ == '__main__':

    db = Database()
    ds = Dataset(db,'full').dfs
    for data in ds: 
        data.df = data.formatDataframeForMatch()
        
    cache_startup = [[ds,'ds']]
    cache = Cache()
    [ cache.set(data,key) for data, key in cache_startup]
    uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)