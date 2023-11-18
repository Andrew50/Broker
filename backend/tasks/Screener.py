





from Data import Database, Dataset


def load_score(self, st, model=None):
	if model == None:
		model = Main.load_model(st)
	returns = []
	for df, index in self.np:
		score = model.predict(df)
		returns.append([self.ticker, self.df.index[index], st, score])
	self.score = returns
	return returns





# class Screener:
	

# 	def score(ds):
		




# 		if model == None:
# 			model = Main.load_model(st)
# 		returns = []
# 		for df, index in self.np:
# 			score = model.predict(df)
# 			returns.append([self.ticker, self.df.index[index], st, score])
# 		self.score = returns
# 		return returns
		

# 	#def get(dt = None, ticker = None, tf = 'd',browser = None, fpath = None):
# 	def get(user_id,tf = '1d',dt = None):
# 		db = Database()
# 		ds = Dataset(db, dt = db.format_date(dt))
# 		table = None
# 		st = main.get_config('Screener active_setup_list').split(',')
# 		setups = main.score_dataset(df,st)
		
# 		for ticker, dt, st, score in setups:
			

