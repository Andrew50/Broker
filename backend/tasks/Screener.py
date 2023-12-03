import json
import tensorflow as tf
import numpy as np
from sync_Data import data

class Screener:
	
	def load_model(user_id,st):
		return tf.keras.models.load_model(f'{user_id}_{st}')

	def screen(user_id,setup_types, _format, query = None,threshold = .65, model = None):
		results = []
		
		if _format == 'screener':
			
			for st in setup_types:
				tf, setup_length = data.get_setup_info(user_id,st)
				ds, ticker_list = data.get_ds('screener','full',tf,setup_length)
				model = Screener.load_model(user_id,st)
				ds = ds[:,:,1:]
				scores = model.predict(ds)[:,0]
				i = 0
				for score in scores:
					if score > threshold:
						ticker = ticker_list[i]
						results.append([ticker,int(100*score)])
					i += 1
			
			results.sort(key=lambda x: x[1],reverse=True)
			return results
		
		elif _format == 'trainer':
			st = setup_types
			tf, setup_length = data.get_setup_info(user_id,st)
			ds, ticker_list = data.get_ds('screener',query,tf,setup_length)
			dt_list = ds[:,-1,0]
			ds = ds[:,:,1:]
			scores = model.predict(ds)[:,0]
			i = 0
			for score in scores:
				if score > threshold and score < 1 - threshold:
					ticker = ticker_list[i]
					results.append([ticker,tf,dt_list[i]])
				i += 1
			
			return results
		
		elif _format == 'study':
			query = [[query,None]]
			for st in setup_types:
				tf, setup_length = data.get_setup_info(user_id,st)
				ds, ticker_list = data.get_ds('screener',query,tf,None)
				
				model = Screener.load_model(user_id,st)
				dt_list = ds[:,:,0]
				ds = ds[:,:,1:]
				scores = model.predict(ds)[:,0]
				i = 0
				for score in scores:
					if score > threshold:
						dt = dt_list[i]
						results.append([dt,int(100*score)])
					i += 1
			
			return results
		

	
def get(args,user_id):
	ticker, tf, dt, setup_types = args

	results = Screener.screen(user_id,ticker,dt,setup_types)
	return json.dumps(results)
			
if __name__ == '__main__':
	pass
