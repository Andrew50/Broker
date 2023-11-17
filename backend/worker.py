import time,importlib,sys,traceback, redis, pickle
sys.path.append('./tasks')






def run_task(request='Test_get'):

	try:
		print('god')
		#print('Some message', flush=True)
		split = request.split('_')
		func = split[0]
		args = split[1:]
		module_name, function_name = func.split('-')
		module = importlib.import_module(module_name)
		func = getattr(module, function_name, None)
		return func(args)
	except Exception as e:
		return str(traceback.format_exc()) + str(e)
	#except TimeoutError:
		#return 'failed'