
import os
import numpy as np
import pandas as pd
from Data7 import Data as data

import numpy as np
from typing import Tuple
from tqdm import tqdm
from matplotlib import pyplot as plt
import datetime

# NN imports
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout

# Imports for evaluating the network
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


BATCH_SIZE = 64
VALIDATION = 0.2
LEARN_RATE = 1e-3
MODEL_SAVE_NAME = 'model'
TRAIN_SPLIT = 1
#FEAT_LENGTH = 50
FEAT_COLS = ['open', 'low', 'high', 'close']
TICKERS = ['TSLA', 'AAPL', 'MSFT', 'NVDA', 'GOOG', 'AMD']

class Create:
	def evaluate_training(model: Sequential,x_test: np.array,y_test: np.array):
		score = model.evaluate(x_test,y_test,verbose = 0,)
		pred = np.argmax(model.predict(x_test), axis = 1,)
		cm = confusion_matrix(y_true = y_test,y_pred = pred,)
		cm_scaled = cm/cm.astype(np.float).sum(axis = 0)
		unscaled = ConfusionMatrixDisplay(confusion_matrix = cm)
		unscaled.plot()
		unscaled.ax_.set_title('Unscaled confusion matrix')
		scaled = ConfusionMatrixDisplay(confusion_matrix = cm_scaled)
		scaled.plot()
		scaled.ax_.set_title('Scaled confusion matrix')
		plt.show()
		return

	def time_series(df: pd.DataFrame,
					col: str,
					name: str, sample_size) -> pd.DataFrame:
		return df.assign(**{
			f'{name}_t-{lag}': col.shift(lag)
			for lag in range(0, sample_size)
		})


	def get_lagged_returns(df: pd.DataFrame, sample_size) -> pd.DataFrame:

		#close = df.iat[-2,3]
		for col in FEAT_COLS:
			#return_col = df[col]/df[col].shift(1)-1
			return_col = df[col]/df['close'].shift(1)  -1
			#return_col = df[col].div(close) - 1
			df = Create.time_series(df, return_col, f'feat_{col}_ret', sample_size)
		return df

	def get_classification(df: pd.DataFrame,value) -> pd.DataFrame:
		df['classification'] = value
		return df

	def reshape_x(x: np.array,FEAT_LENGTH) -> np.array:

		
	  #  num_feats = x.shape[1]//FEAT_LENGTH
		num_feats = x.shape[1]//FEAT_LENGTH
		#print(num_feats)
		#num_feats = 4
		x_reshaped = np.zeros((x.shape[0], FEAT_LENGTH, num_feats))
		for n in range(0, num_feats):
			x_reshaped[:, :, n] = x[:, n*FEAT_LENGTH:(n+1)*FEAT_LENGTH]


	   
		return x_reshaped

	def nn_multi(bar):
		try:

		 
			setups = bar
			ticker = setups[0]
			date = setups[1]
			value = setups[2]
			setup_type = setups[6]
			
			#setup_type = [3] god reallllly 
			sample_size = Create.setup_size(setup_type)
	   

			df = data.get(ticker,date = date )
		 
			
			index = data.findex(df,date)
			left = index-sample_size
			if left < 0:
				left = 0
			df2 = df[left:index]
			
			o = df.iat[index,0]
			add = pd.DataFrame({
				'datetime':[date],
				'open':[o],
				'high':[o],
				'low':[o],
				'close':[o],
				'volume':[0]}).set_index('datetime')
			df2 = pd.concat([df2,add])

			df = df2
		  
			if len(df) < sample_size:
				col = df.columns
				add = pd.DataFrame(df.iat[-1,3], index=np.arange(sample_size - len(df) + 1), columns=col)

			   # add.Index = df.index[0] - datetime.timedelta(days = 1)
				df = pd.concat([add,df])
			  

		  
			print(len(df))
			

			df = Create.get_lagged_returns(df, sample_size)
			df = Create.get_classification(df,value)
			
			df = df.replace([np.inf, -np.inf], np.nan).dropna()[[col for col in df.columns if 'feat_' in col] + ['classification']]
			
			return  df
			
			#return Create.reform(df)
		except:
			pass




	

	def reform(df,setup_type,currentday):
		sample_size = Create.setup_size(setup_type)

		o = df.iat[currentday,0]
		df = df[currentday-sample_size:currentday]


	 
		
		#bandage
		date = datetime.datetime.now()
		
		add = pd.DataFrame({
			'datetime':[date],
			'open':[o],
			'high':[o],
			'low':[o],
			'close':[o],
			'volume':[0]}).set_index('datetime')
		df = pd.concat([df,add])

		if len(df) < sample_size:
			col = df.columns
			add = pd.DataFrame(df.iat[-1,3], index=np.arange(sample_size - len(df) + 1), columns=col)

			# add.Index = df.index[0] - datetime.timedelta(days = 1)
			df = pd.concat([add,df])

		df = Create.get_lagged_returns(df, sample_size)
		df = Create.get_classification(df,1)
		df =  df.replace([np.inf, -np.inf], np.nan).dropna()[[col for col in df.columns if 'feat_' in col] + ['classification']]
		df = df.values
		df = Create.reshape_x(df[0:, :-1],sample_size)
		return df

	def get_setups_list():

		setups = []

		path = "C:/Screener/sync/database/"

		dir_list = os.listdir(path)

		for p in dir_list:
				 
			s = p.split('_')
			s = s[1] + '_' + s[2].split('.')[0]
			use = True
			for h in setups:
				if s == h:
					use = False
					break
			if use:
				setups.append(s)


		return setups



	def sample(setuptype,use,split):
		buffer = 2
		if setuptype == 'F' and False:
			f = pd.read_feather('C:/Screener/setups/database/F.feather').sort_values(by='date', ascending = False).reset_index(drop = True)
			nf = pd.read_feather('C:/Screener/setups/database/NF.feather').sort_values(by='date', ascending = False).reset_index(drop = True)
			nf = nf[nf['setup'] == 1]
			for i in range(len(nf)):
				dt = nf.iat[i,1]
				index = data.findex(f.set_index('date'),dt)
				try:
					f.iat[index,2] = 1
				except:
					pass
			allsetups = f
		else:
			allsetups = pd.read_feather('C:/Screener/setups/database/' + setuptype + '.feather').sort_values(by='date', ascending = False).reset_index(drop = True)
		yes = []
		no = []
		req_no = []
		g = allsetups.groupby(pd.Grouper(key='ticker'))
		dfs = [group for _,group in g]
		for df in dfs:
			df = df.reset_index(drop = True)
			rem = 0
			for i in range(len(df)):
				bar = df.iloc[i]
				setup = bar[2]
				if setup == 1:
					if df.iat[i-1,2] == 0:
						for j in range(buffer):
							try:
								req_no.append(df.iloc[i - j - 1])
							except:
								pass
					yes.append(bar)
					rem = buffer
				else:
					if rem > 0:
						req_no.append(bar)
						rem -= 1
					else:
						#needs to be fixes because if setup occurs it will ad to no and to no_req because it adds to no req on a 1
						no.append(bar)
		yes = pd.DataFrame(yes)
		print(f'{len(yes)} setups')
		no = pd.DataFrame(no)
		req_no = pd.DataFrame(req_no)
		required_no = allsetups[allsetups['req'] == 1]
		required_no = required_no[required_no['setup'] == 0]
		req_no = pd.concat([req_no,required_no])
		length = ((len(yes) / use) - len(yes)) - len(req_no)
		use = length / len(no)
		if use > 1:
			use = 1
		if use < 0:
			use = 0
		no = no.sample(frac = use)
		allsetups = pd.concat([yes,no,req_no]).sample(frac = 1).reset_index(drop = True)
		setups = allsetups
		return setups

	def setup_size(setup_type):
		if 'EP' in setup_type:
			sample_size = 40
		elif setup_type == 'MR':
			sample_size = 40
		elif 'F' in setup_type:
			sample_size = 80
		   
		else: #pivot
			sample_size = 40
		return sample_size

	def get_nn_data(setuptype,use,split):
		setups = Create.sample(setuptype,use,split)
		arglist = []
		for i in range(len(setups)):
			bar = setups.iloc[i].tolist()
			bar.append(setuptype)
			arglist.append(bar)
		dfs = data.pool(Create.nn_multi,arglist)
		nn_values = pd.concat(dfs)
		nn_values = nn_values.values
		np.random.shuffle(nn_values)
		sample_size = Create.setup_size(setuptype)
		split_idx = 0
		np.save('C:/Screener/tmp/training data/x_test.npy', Create.reshape_x(nn_values[split_idx:, :-1],sample_size))
		np.save('C:/Screener/tmp/training data/y_test.npy', nn_values[split_idx:, -1],sample_size)
		split_idx = -1
		np.save('C:/Screener/tmp/training data/x_train.npy', Create.reshape_x(nn_values[0:split_idx, :-1],sample_size))
		np.save('C:/Screener/tmp/training data/y_train.npy', nn_values[0:split_idx:, -1],sample_size)
		return
   
	def load_data() -> Tuple[np.array, np.array, np.array, np.array]:
		return (np.load('C:/Screener/tmp/training data/x_train.npy'),np.load('C:/Screener/tmp/training data/y_train.npy'),np.load('C:/Screener/tmp/training data/x_test.npy'),np.load('C:/Screener/tmp/training data/y_test.npy'),)

	def get_model(x_train: np.array) -> Sequential:
		
		return Sequential([
			Bidirectional(
				LSTM(
					64, 
					input_shape = (x_train.shape[1], x_train.shape[2]),
					return_sequences = True,
				),
			),
			Dropout(0.2),
			Bidirectional(LSTM(32)),
			Dense(3, activation = 'softmax'),
		])


	def test_data(ticker,date,setup_type):

		bar = [ticker,date,1,"" ,"","",setup_type]
		x = Create.nn_multi(bar)
		print(x)
		x = x.values
		sample_size = Create.setup_size(setup_type)
	 
		x = Create.reshape_x(x[0:, :-1],sample_size)

		return x
   
	def run(setuptype,keep,epochs,split = True):
		Create.get_nn_data(setuptype,keep,split)
		x_train, y_train, x_test, y_test = Create.load_data()
		model = Create.get_model(x_train)
		model.compile(loss = 'sparse_categorical_crossentropy',optimizer = Adam(learning_rate = LEARN_RATE),metrics = ['accuracy'])
		model.fit(x_train,y_train,epochs = epochs,batch_size = BATCH_SIZE,validation_split = VALIDATION,)
		model.save('C:/Screener/sync/models/model_' + setuptype)

		if split:

		   # pass
			Create.evaluate_training(model, x_test, y_test)
		



	
	