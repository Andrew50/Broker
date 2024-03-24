from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from rq.job import Job
from fastapi.middleware.cors import CORSMiddleware

import importlib

from worker import runTask

app = FastAPI()

origins = [
	"http://localhost:5173",  # Add the origin of your frontend app
	"http://localhost:5057",  # You can add multiple origins if needed
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,  # Allows specified origins
	allow_credentials=True,
	allow_methods=["*"],  # Allows all methods
	allow_headers=["*"],  # Allows all headers
)


redis_conn = Redis(host='myproj_redis', port=6379)
q = Queue('my_queue', connection=redis_conn)

@app.get('/hello')
def hello():
	"""Test endpoint"""
	return {'hello': 'world'}



#main backend caller
@app.post('/{task}', status_code=201)
def addTask(task):
	module_name, function_name = task.split('-')
	module = importlib.import_module(module_name)
	func = getattr(module, function_name, None)

	job = q.enqueue(func)
	size = len(q)

	return {'job': size,
			'task_id': job.get_id()}


@app.post('/groups/group1', status_code=201)
def addTask():
	"""
	Adds tasks to worker queue.
	Expects body as dictionary matching the Group class.
	"""

	job = q.enqueue(runTask)
	size = len(q)

	return {'job': size,
			'task_id': job.get_id()}




@app.get('/poll/{job_id}')
def get_result(job_id: str):
	job = Job.fetch(job_id, connection=redis_conn)

	if job.is_finished:
		return {"status":"done",
			"result": job.result}
	elif job.is_failed:
		return {"status": "failed"}
	else:
		return {"status": "in progress"}


@app.get('/queueSize')
def queueSize():
	"""Test endpoint"""
	return {'Queue Size': len(q)}
