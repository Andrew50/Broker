from fastapi import FastAPI, HTTPException, status, Request as FastAPIRequest, Depends
import datetime, uvicorn, importlib, sys, traceback, jwt, asyncio,  json, yfinance as yf
from redis import Redis
from rq import Queue
from rq.job import Job
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
from pydantic import BaseModel

#from worker import run_task

sys.path.append('./tasks')
SECRET_KEY = "god"
from async_Data import Data

#from celery import Celery



# Use the Redis broker
#celery_app = Celery('task_queue', broker='redis://redis:6379/0', backend = 'redis://redis:6379/0')





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
	
def create_jwt_token(user_id: str) -> str:
	payload = {
		"sub": user_id, # Subject of the token (user identifier)
		"exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1), # Expiration time
	}
	return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

#run_task = 'worker.run_task'
# def run_task(func,args,user_id):
# 	try:
# 		module_name, function_name = func.split('-')
# 		module = importlib.import_module(module_name)
# 		func = getattr(module, function_name, None)
# 		return func(args,user_id)
# 	except Exception as e:
# 		raise Warning(str(traceback.format_exc() + str(e)))
# 		return 'failed'

def create_app():
	app = FastAPI()
	app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://localhost:5057",],allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)
	redis_conn = Redis(host='redis', port=6379)
	q = Queue('my_queue', connection=redis_conn,default_timeout=6000)

	@app.on_event("startup")
	async def startup_event():
		app.state.data = Data()
		await app.state.data.init_async_conn()
		
	@app.post('/public',status_code=201)
	async def public_request(request_model: Request, request: FastAPIRequest):
		data = request.app.state.data
		func, args = request_model.function, request_model.arguments
		print(f'received public request for {func}: {args}',flush=True)
		if func == 'signup':
			await data.set_user(email=args[0],password=args[1])
			func = 'signin'
		if func == 'signin':
			user_id = await data.get_user(args[0],args[1])
			if user_id is None:
				raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
			token = create_jwt_token(user_id)
			setups = await data.get_user_setups(user_id)
			settings = await data.get_settings(user_id)
			watchlists = await data.get_watchlists(user_id)
			return {"access_token": token, "token_type": "bearer",
		   "setups":setups,"settings":settings,"watchlists":watchlists}
		
		else:
			raise Exception('to code' + func)
		
	@app.post('/data',status_code=201)
	async def data_request(request_model: Request, request: FastAPIRequest, user_id: str = Depends(validate_auth)):
		data_ = request.app.state.data
		func, args = request_model.function, request_model.arguments
		print(f'received data request for {func}: {args}',flush=True)
		if func == 'chart':
			args += ['MSFT','1d',None][len(args):]
			ticker,tf,dt = args
			val = await data_.get_df('chart',ticker,tf,dt)
			#if data_.is_extended_market_open:
			if True: 
				#current_price = await data_.get_current_price(ticker)
				current_price = yf.download(ticker, interval='1m', period='1d', prepost=True, auto_adjust=True, threads=False, keepna=False)['Close'][-1]
				val = json.loads(val)
				if current_price == None:
					current_bar = val[-1]
				else:
					current_bar = {
								'time': str(datetime.datetime.now())[:10],
								'open': current_price,
								'high':  current_price,
								'low':  current_price,
								'close':  current_price
							}
				
				val.append(current_bar)
				#print(val,flush=True)
				val = json.dumps(val)
			return val
		elif func == 'create setup':
			st, tf, setup_length = args
			await data_.set_setup(user_id,st,tf,setup_length)
			return 'done'
		elif func == 'delete setup':
			st, = args
			await data_.set_setup(user_id,st,delete = True)
			return 'done'
		elif func == 'set sample':
			st, ticker,tf,dt,value = args
			await data_.set_single_setup_sample(user_id,st,ticker,dt,value)
			return 'done'
		elif func == 'get instance':
			st, = args
			queue_size = data_.get_trainer_queue_size(user_id,st)
			if queue_size == 50:
				q.enqueue(run_task, kwargs={'func': 'Trainer-start', 'args': args, 'user_id':user_id}, timeout=6000000)
				# if queue_size == 0:
				# 	while True:
				# 		instance = await data_.get_trainer_queue(user_id,st)
				# 		if instance != None:
				# 			break
				# 		await asyncio.sleep(.2)
			else:
				instance = await data_.get_trainer_queue(user_id,st)
				
			return instance
		elif func == 'study':
			st,ticker,tf,dt,annotation = args
			val = await data_.set_annotation(user_id,st,ticker,tf,dt,annotation)
			return json.dumps(val)
		elif func == 'watchlist':
			ticker,watchlist_name,delete = args
			await data_.set_watchlist(user_id,ticker,watchlist_name,delete)
		else:
			raise Exception('to code' + func)
			
	# @app.post('/backend', status_code=201)
	# async def backend_request(request_model: Request, request: FastAPIRequest, user_id: str = Depends(validate_auth)):
	# 	func, args = request_model.function, request_model.arguments
	# 	print(f'received backend request for {func}: {args}',flush=True)
	# 	job = q.enqueue(run_task, kwargs={'func': func, 'args': args, 'user_id':user_id}, timeout=600)
	# 	#job = q.enqueue_call('worker.run_task', kwargs={'func': func, 'args': args, 'user_id':user_id}, timeout=600)
	# 	return {'task_id': job.get_id()}
	
	# async def fetch_job(job_id):
	# 	loop = asyncio.get_event_loop()
	# 	job = await loop.run_in_executor(None, Job.fetch, job_id, redis_conn)
	# 	return job
		
	# 	@app.get('/poll/{job_id}')
	# async def get_result(job_id: str):
	# 	job = await fetch_job(job_id)
	# 	if job.is_finished:
	# 		return {"status": "done", "result": job.result}
	# 	elif job.is_failed:
	# 		return {"status": "failed"}
	# 	else:
	# 		return {"status": "in progress"}
	# return app
		
	@app.post('/backend', status_code=201)
	async def backend_request(request_model: Request, request: FastAPIRequest, user_id: str = Depends(validate_auth)):
		func, args = request_model.function, request_model.arguments
		task_id = data_.queue_task(func,args,user_id)

	
	@app.get('/poll/{job_id}')
	async def get_result(job_id: str):
		job = await fetch_job(job_id)

	# @app.post('/backend', status_code=201)
	# async def backend_request(request_model: Request, request: FastAPIRequest, user_id: str = Depends(validate_auth)):
	# 	func, args = request_model.function, request_model.arguments
	# 	print(f'received backend request for {func}: {args}', flush=True)
	# 	job = celery_app.send_task('run_task', kwargs={'func': func, 'args': args, 'user_id': user_id})
	# 	return {'task_id': job.id}

	# async def fetch_job(job_id):
	# 	loop = asyncio.get_event_loop()
	# 	job = await loop.run_in_executor(None, celery_app.AsyncResult, job_id)
	# 	return job

	# @app.get('/poll/{job_id}')
	# async def get_result(job_id: str):
	# 	job = await fetch_job(job_id)
	# 	if job.ready():
	# 		if job.successful():
	# 			return {"status": "done", "result": job.result}
	# 		else:
	# 			return {"status": "failed"}
	# 	else:
	# 		return {"status": "in progress"}
	# return app

app = create_app()

if __name__ == '__main__':
	#data.init_cache(force=True)
	#data.init_cache(force=False)#default for quikc loading
	uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)