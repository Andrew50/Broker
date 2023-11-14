from tasks.Data import Database, Dataset, Cache
import uvicorn, traceback

if __name__ == '__main__':
    try:
        cache = Cache()
        db = Database()
        ds = Dataset(db,'full',debug = 100,_print=True).dfs
        match_data = []
        for data in ds: 
            data.formatDataframeForMatch()
            match_data.append([data.df,data.ticker])
        cache.set_hash(match_data,'ds')
            
    except Exception as e:
        print(traceback.format_exc() + str(e),flush=True)
        




    #cache = Cache()







    uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)