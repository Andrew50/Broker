from tasks.Data import Database, Cache, Data
import uvicorn, traceback, multiprocessing, datetime
       
    
if __name__ == '__main__':
    try:
        print('starting backend',flush = True)
        start = datetime.datetime.now()
        #while True:
        Cache().set_hash(Database().get_ds(),'ds')
            #except Exception as e: print(e)
            #else: break
        print(f'started backend in {datetime.datetime.now() - start}',flush = True)
        
    except Exception as e:
        print(traceback.format_exc() + str(e),flush=True)


    uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)