

import importlib, traceback




def run_task(func,args,user_id):
	try:
		module_name, function_name = func.split('-')
		module = importlib.import_module(module_name)
		func = getattr(module, function_name, None)
		return func(args,user_id)
	except Exception as e:
		raise Warning(str(traceback.format_exc() + str(e)))
		return 'failed'