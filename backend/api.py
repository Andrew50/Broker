from fastapi import FastAPI, HTTPException, status, Request as FastAPIRequest, Depends, Header
import datetime, uvicorn, importlib, sys, traceback, jwt, asyncio, time, json
from redis import Redis
from rq import Queue
from rq.job import Job
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from pydantic import BaseModel
sys.path.append('./tasks')
SECRET_KEY = "god"
from Data import data

class Request(BaseModel):
	function: str
	arguments: list
	


async def validate_auth(token: str = Depends(oauth2_scheme)):
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
		user_id = payload.get("sub")
		if user_id is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
		return user_id
	except jwt.PyJWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

def run_task(func,args):
	try:
		module_name, function_name = func.split('-')
		module = importlib.import_module(module_name)
		func = getattr(module, function_name, None)
		return func(args,data)
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
	app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://localhost:5057",],allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)
	redis_conn = Redis(host='redis', port=6379)
	q = Queue('my_queue', connection=redis_conn)

	@app.on_event("startup")
	async def startup_event():
		app.state.data = data
		await app.state.data.init_async_conn()
		

	@app.post('/public',status_code=201)
	async def data_request(request_model: Request, request: FastAPIRequest):
		data = request.app.state.data
		func, args = request_model.function, request_model.arguments
		if func == 'signup':
			await data.set_user(email=args[0],password=args[1])
			func = 'signin'
		if func == 'signin':
			user_id = await data.get_user(args[0],args[1])
			if user_id is None:
				raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
			token = create_jwt_token(user_id)
			setups = await data.get_setups(user_id)
			settings = await data.get_settings(user_id)
			return {"access_token": token, "token_type": "bearer","setups":setups,"settings":settings}
		
		else:
			raise Exception('to code' + func)



	
	@app.post('/data',status_code=201)
	async def data_request(request_model: Request, request: FastAPIRequest, user_id: str = Depends(validate_auth)):
		data = request.app.state.data
		func, args = request_model.function, request_model.arguments
		if func == 'chart':
			args += ['MSFT','1d',None][len(args):]
			ticker,tf,dt = args
			val = await data.get_df('chart',ticker,tf,dt)
			return val
		elif func == 'create setup':
			st, tf, setup_length = args
			await data.set_setup(user_id,st,tf,setup_length)
			return 'done'
		elif func == 'delete setup':
			st, = args
			await data.set_setup(user_id,st,delete = True)
			return 'done'
		elif func == 'set sample':
			user_id, st, query = args
			data.set_setup_sample(user_id,st,query)
			return 'done'
		else:
			raise Exception('to code' + func)
			
	@app.post('/backend', status_code=201)
	async def backend_request(request_model: Request, request: FastAPIRequest, user_id: str = Depends(validate_auth)):
		func, args = request_model.function, request_model.arguments
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
	#data.init_cache()#use when redis_init changed and old format/data needs to be overwriten
	data.init_cache(force=False)#default for quikc loading
	uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)