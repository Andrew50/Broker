

class Screener:

	def load_score(self, st, model=None):
		if model == None:
			model = Main.load_model(st)
		returns = []
		for df, index in self.np:
			score = model.predict(df)
			returns.append([self.ticker, self.df.index[index], st, score])
		self.score = returns
		return returns




	def get(args,data):
		args += ['current',1,None][len(args):]
		dt = args[0]
		user_id = args[1]
		dt = args[2]
		
			
if __name__ == '__main__':
	from Data import Data
	data = Data()
	print(Screener.get(['current',1],data))
