import numpy as np
import random
import tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout
from tensorflow.keras.optimizers import Adam
import keras_tuner as kt
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping

class Trainer:
	
	def sample(all_setups, use):
		yes = [sublist for sublist in all_setups if sublist[2] == 1]
		random.shuffle(all_setups)
		no = [sublist for sublist in all_setups if sublist[2] == 0][:int(len(yes) / use)]
		sample = yes + no
		random.shuffle(sample)
		return sample

	def build_trainer_model(hp):
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
		return model
	
	def train_model(data, user_id, st):
		epochs = 200
		use = .1
		if not tensorflow.config.list_physical_devices('GPU'):print("No GPU was detected. Using CPU instead.")
		else:print("GPU detected, using GPU for training.")
		setup_sample, tf, setup_length = data.get_setup_sample(user_id, st)
		setup_sample = Trainer.sample(setup_sample, use)
		ds, y = data.get_ds('screener', setup_sample, tf, setup_length)
		print(ds)
		ds = ds[:, :, 1:5]
		early_stopping = EarlyStopping(
            monitor='val_auc_pr',  # Use the metric name here
            patience=15,
            restore_best_weights=True
        )
		ds = np.flip(ds,1)
		tuner = kt.Hyperband(
            Trainer.build_trainer_model,
            objective=kt.Objective('val_auc_pr', direction='max'),
            max_epochs=40,
            factor=3,
            directory='C:/dev/broker/backend/models/kt',
            project_name='crazy_asf'
        )
		tuner.search(ds, y, epochs=epochs, validation_split=0.2, callbacks=[early_stopping])
		best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
		model = tuner.hypermodel.build(best_hps)
		model.fit(
            ds, y, 
            epochs=epochs, 
            batch_size=best_hps.get('batch_size'),  # Use the tuned batch size
            validation_split=0.2, 
            callbacks=[early_stopping]
        )
		model.save(f'C:/dev/broker/backend/models/{user_id}_{st}')
		tensorflow.keras.backend.clear_session()

# def get(st):
	
# 	return 'trainer-get'



def train(args,data):
	user_id,st = args
	Trainer.train(data,user_id,st)
	return 'done'


if __name__ == '__main__':
	from Data import data
	Trainer.train(data, 4, 'EP')




