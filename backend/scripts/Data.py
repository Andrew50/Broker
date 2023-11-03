try:
	from Database import Database
except:
	from .Database import Database
import numpy as np

from argparse import ArgumentTypeError
from tensorflow.keras.models import Sequential
#from ..subpackage2 import module2
from tensorflow.keras import models
#sys.path.append(Stocks2/backend')
# Now, you can import the Match module

class Dataset: #object
	

	def train(self, st, use, epochs): 
		db.consolidate_database()
		allsetups = pd.read_feather('local/data/' + st + '.feather').sort_values(
			by='dt', ascending=False).reset_index(drop=True)
		yes = []
		no = []
		groups = allsetups.groupby(pd.Grouper(key='ticker'))
		dfs = [group for _, group in groups]
		for df in dfs:
			df = df.reset_index(drop=True)
			for i in range(len(df)):
				bar = df.iloc[i]
				if bar['value'] == 1:
					for ii in [i + ii for ii in [-2, -1, 1, 2]]:
						if abs(ii) < len(df):
							bar2 = df.iloc[ii]
							if bar2['value'] == 0:
								no.append(bar2)
					yes.append(bar)
		yes = pd.DataFrame(yes)
		no = pd.DataFrame(no)
		required = int(len(yes) - ((len(no)+len(yes)) * use))
		if required < 0:
			no = no[:required]
		while True:
			no = no.drop_duplicates(subset=['ticker', 'dt'])
			required = int(len(yes) - ((len(no)+len(yes)) * use))
			sample = allsetups[allsetups['value'] == 0].sample(frac=1)
			if required < 0 or len(sample) == len(no):
				break
			sample = sample[:required + 1]
			no = pd.concat([no, sample])
		df = pd.concat([yes, no]).sample(frac=1).reset_index(drop=True)
		df['tf'] = st.split('_')[0]
		df = df[['ticker', 'dt', 'tf']]
		
		return df
		df = pd.read_feather('local/data/' + st + '.feather')
		ones = len(df[df['value'] == 1])
		if ones < 150:
			print(f'{st} cannot be trained with only {ones} positives')
			return
		x = self.raw_np
		y = self.y_np

		model = Sequential([Bidirectional(LSTM(64, input_shape=(x.shape[1], x.shape[2]), return_sequences=True,),), Dropout(
			0.2), Bidirectional(LSTM(32)), Dense(3, activation='softmax'),])
		model.compile(loss='sparse_categorical_crossentropy',
					  optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])
		model.fit(x, y, epochs=epochs, batch_size=64, validation_split=.2,)
		model.save('sync/models/model_' + st)
		tensorflow.keras.backend.clear_session()

	def init_worker(pack):
		bar, other = pack
		ticker = bar['ticker']
		dt = bar['dt']
		tf = bar['tf']
		bars, offset, value, pm, np_bars = other
		# needs to be fixed becaujse m
		return Data(ticker, tf, dt, bars, offset, value, pm, np_bars)

	def __init__(self, request='full',tf='d', bars=0, offset=0, value=None, pm=True):
		
		if request == 'full':
			request = [[ticker,None] for ticker in db.get_ticker_list('full')]
		for ticker, dt in request:
			self.dfs = Data(ticker, tf, dt, bars, offset, value, pm)
		self.bars = bars
		self.offset = offset
		self.len = len(self.dfs)
		
class Data:

	def __init__(self, ticker='QQQ', tf='d', dt=None, bars=0,value=None, pm=True):
		try:
			self.df = db.get_df(ticker,tf,dt,bars,pm)
		except:
			self.df = []
		self.len = len(self.df)
		self.ticker = ticker
		self.tf = tf
		self.dt = dt
		self.value = value

	def load_score(self, st, model=None):
		if model == None:
			model = Main.load_model(st)
		returns = []
		for df, index in self.np:
			score = model.predict(df)
			returns.append([self.ticker, self.df.index[index], st, score])
		self.score = returns
		return returns

	def findex(self, dt):
		dt = Main.format_date(dt)
		if not isinstance(self, pd.DataFrame):
			df = self.df
		else:
			df = self
		i = int(len(df)/2)		
		k = int(i/2)
		while k != 0:
			date = df.index[i].to_pydatetime()
			if date > dt:
				i -= k
			elif date < dt:
				i += k
			k = int(k/2)
		while df.index[i].to_pydatetime() < dt:
			i += 1
		while df.index[i].to_pydatetime() > dt:
			i -= 1
		return i