from Data import Data
import time
from rq.worker import Worker as _Worker
from redis import Redis, RedisError
from rq import Connection, Queue

#_pools = LocalStack()

# class Worker(_Worker):
# 	def work(self, *args, **kwargs):
# 		Data()
# 		#_pools.push({'data':Data()})
# 		return super(Worker, self).work(*args, **kwargs)

class Worker(_Worker):
    def work(self, burst=False, *args, **kwargs):
        # Initialize the database connection when the worker starts working
        self.data_ = Data()
        super().work(burst=burst, *args, **kwargs)

    def perform_job(self, job, *args, **kwargs):
        # Pass the database connection to the job
        return super().perform_job(job, db_connection=self.data_, *args, **kwargs)



if __name__ == '__main__':
	with Connection(Redis(host='redis', port=6379)):
		qs = [Queue('my_queue')]  # List your queues
		w = Worker(qs)
		w.work()