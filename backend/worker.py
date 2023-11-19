import time,importlib,sys,traceback, redis, pickle
sys.path.append('./tasks')
from startup import get_pool

def run_task(request='Test_get'):
	data = get_pool()
	#data = pool['data']
	try:
		split = request.split('_')
		func = split[0]
		args = split[1:]
		module_name, function_name = func.split('-')
		module = importlib.import_module(module_name)
		func = getattr(module, function_name, None)
		return func(args,data)
	except Exception as e:
		print(traceback.format_exc() + str(e),flush=True)
		return 'failed'
