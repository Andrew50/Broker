
import importlib
import traceback
import redis
import json, time
from data import Data
import datetime

def process_tasks():
	r = redis.Redis(host='redis', port=6379)
	data = Data(True)
	while True:
		task = r.brpop('temp_1', timeout=1000)
		if not task:
			data.check_connection()
		else:
			_, task_message = task
			task_data = json.loads(task_message)
			task_id, func_ident, args = task_data['id'], task_data['func'], task_data['args']
			module_name, function_name = func_ident.split('-')
			print(f"starting {func_ident} {args} {task_id}", flush=True)
			try:
				module = importlib.import_module(module_name)
				func = getattr(module, function_name, None)
				r.set(f"result:{task_id}", json.dumps('running'))
				result = func(data,*args)
				r.set(f"result:{task_id}", json.dumps(result))
				print(f"finished {func_ident} {args} result: {result}", flush=True)
			except:
				exception = traceback.format_exc()
				r.set(f"result:{task_id}", json.dumps('error: ' + exception))
				print(exception, flush=True)

if __name__ == "__main__":
	process_tasks()


	
