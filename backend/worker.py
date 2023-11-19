import time,importlib,sys,traceback, redis, pickle
sys.path.append('./tasks')
from startup import get_pool  # Replace with actual module name



def run_task(request='Test_get'):
	pool = get_pool()
	mysql_conn = pool['mysql']
	redis_conn = pool['redis']

	try:
		#print('Some message', flush=True)
		split = request.split('_')
		func = split[0]
		args = split[1:]
		module_name, function_name = func.split('-')
		module = importlib.import_module(module_name)
		func = getattr(module, function_name, None)
		return func(args,redis_conn,mysql_conn)
	except Exception as e:
		print(traceback.format_exc() + str(e),flush=True)
		return 'failed'
	#except TimeoutError:
		#return 'failed'