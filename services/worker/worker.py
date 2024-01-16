
import importlib
import traceback
def run_task(func,args,user_id):
	try:
		module_name, function_name = func.split('-')
		module = importlib.import_module(module_name)
		func = getattr(module, function_name, None)
		return func(args,user_id)
	except Exception as e:
		raise Warning(str(traceback.format_exc() + str(e)))
		return 'failed'
	


import redis
import json # Import your task functions here



def process_tasks():
    r = redis.Redis(host='redis', port=6379, db=0)
    while True:
        _, task_message = r.brpop('task_queue')
        task_data = json.loads(task_message)
        try:
			result = run_task(task_data['task'],task_data['args'],task_data['kwargs'])
		except:
			result = 'failed'
		
        task_func = task_functions.get(task_data['task'])
        if task_func:
            result = task_func(*task_data['args'], **task_data['kwargs'])
            print(f"Task result: {result}")

if __name__ == "__main__":
    process_tasks()
