from tasks.Data import Data
import uvicorn, traceback, datetime, mysql, time
from rq.local import LocalStack
from rq.worker import Worker as _Worker
from redis import Redis, RedisError

def is_redis_ready(redis_conn):
    try:
        # The INFO command returns various information about the server state
        return redis_conn.info()['loading'] == 0
    except RedisError:
        return False

# Replace 'your_redis_host' and 'your_redis_port' with your actual Redis host and port
#redis_conn = Redis(host='your_redis_host', port='your_redis_port')

# Wait for Redis to become ready before proceeding


_pools = LocalStack()

class Worker(_Worker):
	def work(self, *args, **kwargs):
		redis_conn = self.redis_conn()
		while not is_redis_ready(redis_conn):
			print("Waiting for Redis to load data...",flush = True)
			time.sleep(.5)
		#_pools.push({ 'data':Data()})
		_pools.push(Data())
		return super(Worker, self).work(*args, **kwargs)

	@staticmethod
	def redis_conn():
		return Redis(host='redis', port=6379)

def get_pool():
	return _pools.top

	
if __name__ == '__main__':

	start = datetime.datetime.now()
	db = Data()
	db.init_cache()
	print(f'started backend in {datetime.datetime.now() - start}',flush = True)
	uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)