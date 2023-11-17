from fastapi import FastAPI, HTTPException
from redis import Redis
from rq import Queue
from rq.job import Job
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware

from worker import run_task

#stats
#is it working

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

redis_conn = Redis(host='redis', port=6379)
q = Queue('my_queue', connection=redis_conn)

@app.post('/fetch/{request}', status_code=201)
def addTask(request):
	job = q.enqueue(run_task,kwargs={'request':request},timeout=600)
	#size = len(q)
	return {'task_id': job.get_id()}


@app.get('/poll/{job_id}')
def get_result(job_id: str):
	job = Job.fetch(job_id, connection=redis_conn)
	#print(job)
	if job.is_finished:
		return {"status":"done",
			"result": job.result}
	elif job.is_failed:
		return {"status": "failed"}
	else:
		return {"status": "in progress"}
