
import importlib
import traceback
import redis
import json, time

def process_tasks():
	r = redis.Redis(host='redis', port=6379)
	while True:
		try:
			_, task_message = r.brpop('task_queue_1')
		except:
			time.wait(1)
		else:
			task_data = json.loads(task_message)
			task_id, func_ident, args, user_id = task_data['id'], task_data['func'], task_data['args'], task_data['user_id']
			module_name, function_name = func_ident.split('-')
			module = importlib.import_module(module_name)
			func = getattr(module, function_name, None)
			print(f"starting {func_ident}, with {args}", flush=True)
			try:
				r.set(f"result:{task_id}", json.dumps('running'))
				result = func(args, user_id)
				r.set(f"result:{task_id}", json.dumps(result))
			except:
				r.set(f"result:{task_id}", json.dumps('failed'))
				traceback.print_exc()

if __name__ == "__main__":
	process_tasks()


	
