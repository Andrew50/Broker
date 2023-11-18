from tasks.Data import Database, Cache, Data, Dataset
import uvicorn, traceback, multiprocessing, datetime
       
    
if __name__ == '__main__':
    try:
        start = datetime.datetime.now()
        ds = Dataset()
        Cache().set_hash(ds,'1d')
        print(f'started backend in {datetime.datetime.now() - start}',flush = True)
        
    except Exception as e:
        print(traceback.format_exc() + str(e),flush=True)

    uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)