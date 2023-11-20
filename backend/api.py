from redis import Redis
from rq import Queue
from rq.job import Job
from fastapi.middleware.cors import CORSMiddleware
import datetime
import uvicorn
import importlib
import sys
import traceback
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import jwt
sys.path.append('./tasks')
import asyncio
from tasks.Data import Data

data = Data()

SECRET_KEY = "your_jwt_secret_key"

#def run_task(request):
def run_task(func,args):
    print(data,flush=True)
    try:
        #split = request.split('_')
        #func = split[0]
        #args = split[1:]
        module_name, function_name = func.split('-')
        module = importlib.import_module(module_name)
        func = getattr(module, function_name, None)
        return func(args, data)
    except Exception as e:
        print(traceback.format_exc() + str(e), flush=True)
        return 'failed'
    
#async def run_data(request):

#class UserLogin(BaseModel):
    #username: str
    #password: str
    
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
    
    @app.post('/data',status_code=201)
    async def data_request(request):
        body = await request.json()
        func = body.get('function')
        args = body.get('arguments', [])
        if func == 'signup':
            await data.set_user(email=args[0],password=args[1])
            func = 'signin'
        if func == 'signin':
            user_id = await data.get_user(args)
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            token = create_jwt_token(user_id)
            return {"access_token": token, "token_type": "bearer"}
        else:
            raise Exception('to code')
            
    @app.post('/backend', status_code=201)
    async def backend_request(request):
        body = await request.json()
        func = body.get('function')
        args = body.get('arguments', [])
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
    db = Data()
    #db.init_cache(debug=True)#load 5% of data for testing
    db.init_cache()
    uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)