

import tensorflow as tf
import pandas as pd
from tqdm import tqdm

def compute(bar):
	raw_data, st, model_types = bar
	stat_df = pd.DataFrame()

    
	for method_data, classification_data, method in tqdm(data):
		#train all the models and optimize and all that shit
		for model_type in model_types:
			model, score, stats = train(method_data,classification_data,model_type)
			model.save(f'{st}_{method}_{model_type}')
			#stat_df.add line or something

	stat_df.to_csv(f'{st}_model_data.csv')


def train(x,y,model_type):

    if model_type == 'biLSTM':
        
		model = Sequential()
		for i in range(hp.Int('num_lstm_layers', 1, 3)):
			hp_units = hp.Int('units_' + str(i), min_value=32, max_value=192, step=32)
			return_sequences = True if i < hp.get('num_lstm_layers') - 1 else False
			model.add(Bidirectional(LSTM(units=hp_units, return_sequences=return_sequences)))
			hp_dropout = hp.Float('dropout_' + str(i), min_value=0.0, max_value=0.5, step=0.1)
			model.add(Dropout(hp_dropout))
		hp_batch_size = hp.Choice('batch_size', values=[32, 64, 128, 256])
		model.add(Dense(1, activation='sigmoid'))
		hp_learning_rate = hp.Choice('learning_rate', values=[1e-1, 1e-2, 1e-3, 1e-4, 1e-5])
		auc_pr = tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')
		model.compile(optimizer=Adam(learning_rate=hp_learning_rate),
					  loss='binary_crossentropy',
					  #metrics=['accuracy',auc_pr])
					  metrics=[auc_pr])

    if model_type == 'biLSTM+CNN'
	return model, score, stats

def get_features(sample,method):
    if method == 'close':
        pass
    elif method == 'ohlc':
        pass
    elif method == '':
        pass

def get_sample(st,method):

    pass



def preprocess(data, method):
	if method == 'rolling_change':
         
	elif method == '':
		return data
	else:
		raise ValueError('Invalid preprocessing method')
    #remeber to set last bar all equal to open

if __name__ == '__main__':
	preprocessing_methods = 'rolling_change', 'none', 'savitzky-golay', 'min_max',
    'CEEMDAN', 'VMD', 'st_rolling_change', 'log_dif'
	setup_types = 'EP', 'NEP', 'P', 'NP', 'F', 'NF', 'MR'
    sampling_types = '',
    feature_methods = 'close', 'ohlc', 'ohlcv', 'rsi_c', 'rsi_ohlc'
	model_types = '',''
	from sync_Data import Data
	import multiprocessing
	data = Data()

    start = datetime.datetime.now()
	args = []
	for st in setup_types:
		sample = data.get_setup_sample(1,st)
		raw_data = []
		for ticker, dt, classification in sample:
			raw_data.append([data.get_df('raw',ticker, dt), classification])
		preprocessed_data = []
		for method in preprocessing_methods:
			method_data = []
			classification_data = []
			for df, classification in raw_data:
				method_data.append(preprocess(df, method))	
				classification_data.append(classification)	
			preprocessed_data.append([method_data, classification_data, method])

		args.append([preprocessed_data, st,model_types])
    print(f"data loaded in {datetime.datetime.now() - start}")
	with multiprocessing.Pool(8) as p:
		p.map(compute, args)
		p.close()
		p.join()
		
	




	
