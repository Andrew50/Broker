from tasks.Data import Data
import time
from rq.local import LocalStack
from rq.worker import Worker as _Worker
from redis import Redis, RedisError
from rq import Connection, Queue
from redis import Redis

#_pools = LocalStack()

class Worker(_Worker):
	def work(self, *args, **kwargs):
		Data()
		#_pools.push({'data':Data()})
		return super(Worker, self).work(*args, **kwargs)

def get_pool():
	return _pools.top

if __name__ == '__main__':
	with Connection(Redis(host='redis', port=6379)):
		qs = [Queue('my_queue')]  # List your queues
		w = Worker(qs)
		w.work()