import numpy as np
import random
import tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout
from tensorflow.keras.optimizers import Adam
import keras_tuner as kt

class Trainer:
    
    def sample(all_setups, use):
        yes = [sublist for sublist in all_setups if sublist[2] == 1]
        random.shuffle(all_setups)
        no = [sublist for sublist in all_setups if sublist[2] == 0][:int(len(yes) / use)]
        sample = yes + no
        random.shuffle(sample)
        y = np.array([val for _, _, val in sample])
        sample = [[ticker, dt] for ticker, dt, _ in sample]
        return sample, y

    def build_model(hp):
        model = Sequential()

        # Tune the number of LSTM layers
        for i in range(hp.Int('num_lstm_layers', 1, 3)):
            # Tune the number of units in each LSTM layer
            hp_units = hp.Int('units_' + str(i), min_value=32, max_value=128, step=32)
            return_sequences = True if i < hp.get('num_lstm_layers') - 1 else False
            model.add(Bidirectional(LSTM(units=hp_units, return_sequences=return_sequences)))

            # Tune the dropout rate
            hp_dropout = hp.Float('dropout_' + str(i), min_value=0.0, max_value=0.5, step=0.1)
            model.add(Dropout(hp_dropout))

        # Output layer
        model.add(Dense(3, activation='softmax'))

        # Tune the learning rate
        hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
        model.compile(optimizer=Adam(learning_rate=hp_learning_rate),
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        return model
    
    

    def train(data, user_id, st):
        epochs = 200
        use = .15

        if not tensorflow.config.list_physical_devices('GPU'):
            print("No GPU was detected. Using CPU instead.")
        else:
            print("GPU detected, using GPU for training.")

        setup_sample, tf, setup_length = data.get_setup_sample(user_id, st)
        setup_sample, y = Trainer.sample(setup_sample, use)
        ds = data.get_ds('screener', setup_sample, tf, setup_length)
        ds = ds[:, :, 1:5]

        tuner = kt.Hyperband(Trainer.build_model,
                             objective='val_accuracy',
                             max_epochs=30,
                             factor=2,
                             directory='C:/dev/broker/backend/models/kt',
                             project_name='tunable_layers_more_epochs')

        tuner.search(ds, y, epochs=epochs, validation_split=0.2)
        best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]

        model = tuner.hypermodel.build(best_hps)
        model.fit(ds, y, epochs=epochs, batch_size=64, validation_split=0.2)

        model.save(f'C:/dev/broker/backend/models/{user_id}_{st}')
        tensorflow.keras.backend.clear_session()
        


   


def get(st):
    return 'trainer-get'


def set(st, ticker, tf, dt):
    return 'trainer-set'


if __name__ == '__main__':
    from Data import data
    Trainer.train(data, 4, 'EP')

# from tensorflow.keras.models import Sequential
# #from ..subpackage2 import module2
# import tensorflow
# from tensorflow.keras.optimizers import Adam
# from tensorflow.keras.models import Sequential
# from multiprocessing import Pool, current_process
# from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout
# import random
# import keras_tuner as kt

# import numpy as np

# class Trainer:
	
# 	def sample(all_setups,use):
# 		# allsetups = pd.read_feather('local/data/' + st + '.feather').sort_values(
# 		# 	by='dt', ascending=False).reset_index(drop=True)
# 		# yes = []
# 		# no = []
# 		# groups = allsetups.groupby(pd.Grouper(key='ticker'))
# 		# dfs = [group for _, group in groups]
# 		# for df in dfs:
# 		# 	df = df.reset_index(drop=True)
# 		# 	for i in range(len(df)):
# 		# 		bar = df.iloc[i]
# 		# 		if bar['value'] == 1:
# 		# 			for ii in [i + ii for ii in [-2, -1, 1, 2]]:
# 		# 				if abs(ii) < len(df):
# 		# 					bar2 = df.iloc[ii]
# 		# 					if bar2['value'] == 0:
# 		# 						no.append(bar2)
# 		# 			yes.append(bar)
# 		# yes = pd.DataFrame(yes)
# 		# no = pd.DataFrame(no)
# 		# required = int(len(yes) - ((len(no)+len(yes)) * use))
		
# 		# if required < 0:
# 		# 	no = no[:required]
# 		# while True:
# 		# 	no = no.drop_duplicates(subset=['ticker', 'dt'])
# 		# 	required = int(len(yes) - ((len(no)+len(yes)) * use))
# 		# 	sample = allsetups[allsetups['value'] == 0].sample(frac=1)
# 		# 	if required < 0 or len(sample) == len(no):
# 		# 		break
# 		# 	sample = sample[:required + 1]
# 		# 	no = pd.concat([no, sample])
# 		# df = pd.concat([yes, no]).sample(frac=1).reset_index(drop=True)
# 		# df['tf'] = st.split('_')[0]
# 		# df = df[['ticker', 'dt', 'tf']]
		
# 		# return df
		
# 		yes = [sublist for sublist in all_setups if sublist[2] == 1]
# 		random.shuffle(all_setups)
# 		no = [sublist for sublist in all_setups if sublist[2] == 0][:int(len(yes)/use)]
# 		sample = yes + no
# 		random.shuffle(sample)
# 		y = np.array([val for _,_,val in sample])
# 		sample = [[ticker,dt] for ticker,dt,_ in sample]
# 		return sample, y

	
# 	def train(data,user_id,st):
# 		epochs = 200
# 		use = .15


# 		if not tensorflow.config.list_physical_devices('GPU'):
# 			print("No GPU was detected. Using CPU instead.")
# 		else:
# 			print("GPU detected, using GPU for training.")
# 		setup_sample, tf, setup_length = data.get_setup_sample(user_id,st)
# 		setup_sample, y = Trainer.sample(setup_sample,use)
# 		ds = data.get_ds('screener',setup_sample,tf,setup_length)
# 		ds = ds[:,:,1:5]
# 		print(ds)
# 		print(ds.shape)
# 		model = Sequential([Bidirectional(LSTM(64, input_shape=(ds.shape[1], ds.shape[2]), return_sequences=True,),), Dropout(
# 				0.2), Bidirectional(LSTM(32)), Dense(3, activation='softmax'),])
		
# 		model.compile(loss='sparse_categorical_crossentropy',
# 						optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])
		
# 		model.fit(ds, y, epochs=epochs, batch_size=64, validation_split=.2,)
# 		model.save(f'C:/dev/broker/backend/models/{user_id}_{st}')
# 		tensorflow.keras.backend.clear_session()
		

# def get(st):
# 	return 'trainer-get'


# def set(st,ticker,tf,dt):
# 	return 'trainer-set'

# if __name__ == '__main__':
# 	from Data import data
# 	Trainer.train(data,4,'EP')