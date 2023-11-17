from tasks.Data import Database, Cache, Data
import uvicorn, traceback, multiprocessing, datetime
       
    
if __name__ == '__main__':
    try:
        start = datetime.datetime.now()
        #while True:
        Cache().set_hash(Database().get_ds(),'ds')
            #except Exception as e: print(e)
            #else: break
        print(datetime.datetime.now() - start,flush = True)
        
    except Exception as e:
        print(traceback.format_exc() + str(e),flush=True)


    uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)