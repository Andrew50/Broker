import heapq, json
import tensorflow as tf

class Screener:


	#async def load_model(user_id,st):
	def load_model(user_id,st):
		return tf.keras.models.load_model(f'models/{user_id}_{st}')
			 
	

	def get(args,data):
		args += ['current',1,None][len(args):]
		dt, user_id, st = args
		st = st.split('-')
		if dt == 'current':
			bars = 100#to fix
		else:
			raise Exception('to code')
		ds = data.get_ds('screener','full',tf,bars)
		ticker_list = data.get_ticker_list('full')
		for st in st:
			model = Screener.load_model(user_id,st)
			tf, model = data.get_model(user_id,st)
			scores = model.predict(ds)[:,1]
			results = []
			threshold = .25 ####shouldnt be hard coded
			i = 0
			for score in scores:
				if score > threshold:
					ticker = ticker_list[i]
					results.append([ticker,score])
				i += 1
		results.sort(key=lambda x: x[0])
		return json.dumps(results)
			
if __name__ == '__main__':
	from Data import Data
	data = Data()
	print(Screener.get(['current',1],data))
