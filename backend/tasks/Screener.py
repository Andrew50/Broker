import heapq, json
import tensorflow as tf

class Screener:


	#async def load_model(user_id,st):
	def load_model(user_id,st):
		return tf.keras.models.load_model(f'models/{user_id}_{st}')
			 
	

	def get(args,data):
		args += ['current',1,None][len(args):]
		
		dt, user_id, st, setup_length = args
			
		if dt == 'current':
			bars = 100#to fix
		else:
			raise Exception('to code')
		ds = data.get_ds('screener','full',tf,setup_length)
		#ticker_list = data.get_ticker_list('full')
		for st in setup_types:

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
	




# def train(self, st, use, epochs): 
# 		db.consolidate_database()
# 		allsetups = pd.read_feather('local/data/' + st + '.feather').sort_values(
# 			by='dt', ascending=False).reset_index(drop=True)
# 		yes = []
# 		no = []
# 		groups = allsetups.groupby(pd.Grouper(key='ticker'))
# 		dfs = [group for _, group in groups]
# 		for df in dfs:
# 			df = df.reset_index(drop=True)
# 			for i in range(len(df)):
# 				bar = df.iloc[i]
# 				if bar['value'] == 1:
# 					for ii in [i + ii for ii in [-2, -1, 1, 2]]:
# 						if abs(ii) < len(df):
# 							bar2 = df.iloc[ii]
# 							if bar2['value'] == 0:
# 								no.append(bar2)
# 					yes.append(bar)
# 		yes = pd.DataFrame(yes)
# 		no = pd.DataFrame(no)
# 		required = int(len(yes) - ((len(no)+len(yes)) * use))
# 		if required < 0:
# 			no = no[:required]
# 		while True:
# 			no = no.drop_duplicates(subset=['ticker', 'dt'])
# 			required = int(len(yes) - ((len(no)+len(yes)) * use))
# 			sample = allsetups[allsetups['value'] == 0].sample(frac=1)
# 			if required < 0 or len(sample) == len(no):
# 				break
# 			sample = sample[:required + 1]
# 			no = pd.concat([no, sample])
# 		df = pd.concat([yes, no]).sample(frac=1).reset_index(drop=True)
# 		df['tf'] = st.split('_')[0]
# 		df = df[['ticker', 'dt', 'tf']]
		
# 		return df
# 		df = pd.read_feather('local/data/' + st + '.feather')
# 		ones = len(df[df['value'] == 1])
# 		if ones < 150:
# 			return
# 		x = self.raw_np
# 		y = self.y_np

# 		model = Sequential([Bidirectional(LSTM(64, input_shape=(x.shape[1], x.shape[2]), return_sequences=True,),), Dropout(
# 			0.2), Bidirectional(LSTM(32)), Dense(3, activation='softmax'),])
# 		model.compile(loss='sparse_categorical_crossentropy',
# 					  optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])
# 		model.fit(x, y, epochs=epochs, batch_size=64, validation_split=.2,)
# 		model.save('sync/models/model_' + st)
# 		tensorflow.keras.backend.clear_session()
