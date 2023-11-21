from fastapi import FastAPI, HTTPException, status
import datetime, uvicorn, importlib, sys, traceback, jwt, asyncio, time
from redis import Redis
from rq import Queue
from rq.job import Job
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
sys.path.append('./tasks')

#time.sleep(10)#########+==========================
SECRET_KEY = "god"

from Data import data



class Request(BaseModel):
    function: str
    arguments: list


def run_task(func,args):
    try:
        module_name, function_name = func.split('-')
        module = importlib.import_module(module_name)
        func = getattr(module, function_name, None)
        return func(args)
    except Exception as e:
        print(traceback.format_exc() + str(e), flush=True)
        return 'failed'
    
def create_jwt_token(user_id: str) -> str:
    payload = {
        "sub": user_id, # Subject of the token (user identifier)
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1), # Expiration time
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def create_app():
    
    app = FastAPI()
    origins = ["http://localhost:5173","http://localhost:5057",]

    app.add_middleware(CORSMiddleware,allow_origins=origins,
        allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)

    redis_conn = Redis(host='redis', port=6379)
    q = Queue('my_queue', connection=redis_conn)


    # def convert_request(request):
    #     request = str(request)
    #     parts = request.split()
    #     func = parts[0].split('=')[1].strip("'")
    #     args = parts[1].split('=')[1].strip("[]'").split(',')
    #     return func, args

    @app.on_event("startup")
    async def startup_event():
        app.state.data = data
        await app.state.data.init_async_conn()
    
    @app.post('/data',status_code=201)
    async def data_request(request:Request):
        data = request.app.state.data
        #func, args = convert_request(request)
        func, args = request.function, request.arguments
        print(args,flush=True)
        if func == 'signup':
            await data.set_user(email=args[0],password=args[1])
            func = 'signin'
        if func == 'signin':
            user_id = await data.get_user(args[0],args[1])
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            token = create_jwt_token(user_id)
            return {"access_token": token, "token_type": "bearer"}
        else:
            raise Exception('to code')
            
    @app.post('/backend', status_code=201)
    async def backend_request(request: Request):
        #func, args = convert_request(request)
        func, args = request.function, request.arguments
        job = q.enqueue(run_task, kwargs={'func': func, 'args': args}, timeout=600)
        return {'task_id': job.get_id()}
    
    
    async def fetch_job(job_id):
        loop = asyncio.get_event_loop()
        job = await loop.run_in_executor(None, Job.fetch, job_id, redis_conn)
        return job

    @app.get('/poll/{job_id}')
    async def get_result(job_id: str):
        job = await fetch_job(job_id)
    
        if job.is_finished:
            return {"status": "done", "result": job.result}
        elif job.is_failed:
            return {"status": "failed"}
        else:
            return {"status": "in progress"}
            
    return app

app = create_app()



if __name__ == '__main__':
    #db.init_cache(debug=True)#load 5% of data for testing
   # from Data import data
    
    data.init_cache(force=False)
    uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)