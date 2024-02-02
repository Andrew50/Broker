

import tensorflow as tf
import pandas as pd
from tqdm import tqdm





def compute(bar):
	data, st, model_types = bar
	stat_df = pd.DataFrame()

	for method_data, classification_data, method in tqdm(data):
		#train all the models and optimize and all that shit
		for model_type in model_types:
			model, score, stats = train(method_data,classification_data,model_type)
			model.save(f'{st}_{method}_{model_type}')
			#stat_df.add line or something

	stat_df.to_csv(f'{st}_model_data.csv')


def train(x,y,model_type):



	return model, score, stats

def preprocess(data, method):
	if method == 'rolling_change':
		return data.rolling_change()
	elif method == '':
		return data
	else:
		raise ValueError('Invalid preprocessing method')

if __name__ == '__main__':
	preprocessing_methods = 'rolling_change', ''
	setup_types = 'EP', 'NEP', 'P', 'NP', 'F', 'NF', 'MR'
	model_types = '',''
	from sync_Data import Data
	import multiprocessing
	data = Data()

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

	with multiprocessing.Pool(8) as p:
		p.map(compute, args)
		p.close()
		p.join()
		
	




	