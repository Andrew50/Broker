
import importlib
import traceback
import redis
import json, time
from sync_Data import Data
import datetime

def process_tasks():
	r = redis.Redis(host='redis', port=6379)
	data = Data()
	while True:
		task = r.brpop('task_queue_1', timeout=100000)
		if not task:
			data.check_connection()
		else:
			_, task_message = task
			task_data = json.loads(task_message)
			task_id, func_ident, args, user_id = task_data['id'], task_data['func'], task_data['args'], task_data['user_id']
			module_name, function_name = func_ident.split('-')
			print(f"starting {func_ident} {args}", flush=True)
		try:
			module = importlib.import_module(module_name)
			func = getattr(module, function_name, None)
			r.set(f"result:{task_id}", json.dumps('running'))
			result = func(data,user_id,*args)
			r.set(f"result:{task_id}", json.dumps(result))
			print(f"finished {func_ident} {args}", flush=True)
		except:
			exception = traceback.format_exc()
			r.set(f"result:{task_id}", json.dumps('error: ' + exception))
			print(exception, flush=True)

if __name__ == "__main__":
	process_tasks()


	
