import heapq

class Screener:

	def get(args,data):
		args += ['current',1,None][len(args):]
		dt, user_id, st = args
		if dt == 'current':
			bars = 100#to fix
		else:
			raise Exception('to code')
			
		user_id = args[1]
		st = args[2]
		tf, model = data.get_model(user_id,st)
		ds = data.get_ds('screener','full',tf,bars)
		scores = model.predict(ds)[:,1]
		results = []
		threshold = .25 ####shouldnt be hard coded
		ticker_list = data.get_ticker_list('full')
		i = 0
		for score in scores:
			if score > threshold:
				ticker = ticker_list[i]
				results.append([ticker,score])
			i += 1
		results = heapq.nsmallest(20, results, key=lambda x: x[0])
		return 
			
if __name__ == '__main__':
	from Data import Data
	data = Data()
	print(Screener.get(['current',1],data))
