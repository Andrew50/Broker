from celery import Celery
import importlib, traceback

celery_app = Celery('task_queue', broker='redis://redis:6379/0', backend = 'redis://redis:6379/0')

@celery_app.task
def run_task(func,args,user_id):
	try:
		module_name, function_name = func.split('-')
		module = importlib.import_module(module_name)
		func = getattr(module, function_name, None)
		return func(args,user_id)
	except Exception as e:
		raise Warning(str(traceback.format_exc() + str(e)))
		return 'failed'

# --scale_worker=3
# @celery_app.task
# def run_task(func,args,user_id):
# 	try:
# 		module_name, function_name = func.split('-')
# 		module = importlib.import_module(module_name)
# 		func = getattr(module, function_name, None)
# 		return func(args,user_id)
# 	except Exception as e:
# 		raise Warning(str(traceback.format_exc() + str(e)))
# 		return 'failed'