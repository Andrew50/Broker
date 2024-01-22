import json
import tensorflow as tf



class Screener:

	

	#god
	
	def load_model(user_id,st):
		return tf.keras.models.load_model(f'/app/models/{user_id}_{st}')

	def screen(data,user_id,setup_types, _format, query = None,threshold = .65, model = None):
		results = []
		
		if _format == 'screener':
			for st in setup_types:
				model = Screener.load_model(user_id,st)
				tf, setup_length = data.get_setup_info(user_id,st)
				ds, ticker_list = data.get_ds('screener','full',tf,setup_length)
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
			st = setup_types
			#for st in setup_types:
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
		
	
	
def get(data, user_id, setup_types):


	results = Screener.screen(data,user_id,setup_types,'screener')
	return results
			
if __name__ == '__main__':
	print(Screener.screen(6,['EP'],'screener'))
