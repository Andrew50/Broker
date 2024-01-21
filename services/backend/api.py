import datetime, uvicorn, jwt, json, yfinance as yf
from fastapi import FastAPI, HTTPException, status, Request as FastAPIRequest, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from async_Data import Data

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "god"

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

def create_app():
	app = FastAPI()
	app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://localhost:5057",],allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)

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
		
	@app.post('/private',status_code=201)
	async def data_request(request_model: Request, request: FastAPIRequest, user_id: str = Depends(validate_auth)):
		data_ = request.app.state.data
		func, args = request_model.function, request_model.arguments
		print(f'received private request for {func}: {args}',flush=True)
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
				await data_.queue_task(func,args,user_id)

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
			return await data_.queue_task(func,args,user_id)

			#raise Exception('to code' + func)
		
	@app.post('/backend',status_code=201)
	async def backend(request_model: Request, request: FastAPIRequest, user_id: str = Depends(validate_auth)):
		data_ = request.app.state.data
		func, args = request_model.function, request_model.arguments
		print(f'received backend request for {func}: {args}',flush=True)
		return await data_.queue_task(func,args,user_id)

	@app.get('/poll/{job_id}')
	async def get_result(job_id: str, request: FastAPIRequest):
		data_ = request.app.state.data
		result = await data_.get_task_result(job_id)
		return result

	return app

app = create_app()

if __name__ == '__main__':
	uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)