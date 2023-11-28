import numpy as np
import random
import tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout, Conv1D, MaxPooling1D, Flatten
from tensorflow.keras.optimizers import Adam
from sklearn.utils.class_weight import compute_class_weight
try: 
	import keras_tuner as kt
	import matplotlib.pyplot as plt
except: pass
from tensorflow.keras.callbacks import EarlyStopping
from sync_Data import data
import json
from imblearn.over_sampling import SMOTE

class Trainer:
	

	def get_sample(st, user_id, use):
		# Existing code to get the dataset
		all_setups, tf, setup_length = data.get_setup_sample(user_id, st)
		yes = [sublist for sublist in all_setups if sublist[2] == 1]
		data.set_setup_info(user_id, st, size=len(yes))
		random.shuffle(all_setups)
		no = [sublist for sublist in all_setups if sublist[2] == 0][:int(len(yes) / use)]
		sample = yes + no
		random.shuffle(sample)

		ds, y = data.get_ds('trainer', sample, tf, setup_length)
		ds = ds[:, :, 1:5]
		ds = np.flip(ds, 1)

		# Reshape ds for SMOTE
		n_samples, n_time_steps, n_features = ds.shape
		ds_reshaped = ds.reshape(-1, n_time_steps * n_features)

		# Apply SMOTE
		smote = SMOTE()
		ds_resampled, y_resampled = smote.fit_resample(ds_reshaped, y)

		# Reshape the dataset back to its original shape
		ds = ds_resampled.reshape(-1, n_time_steps, n_features)
		print(len([x for x in y_resampled if x == 1]))
		print(len([x for x in y_resampled if x == 0]))
		
		return ds, y_resampled

	def build_lstm_trainer_model(hp):
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

	def build_1d_cnn_trainer_model(hp):
		model = Sequential()
	
		# Adjust the range and values according to your specific needs
		#for i in range(hp.Int('num_conv_layers', 1, 3)):
		for i in range(hp.Int('num_conv_layers', 1, 2)): #restricting complexity
			hp_filters = hp.Int('filters_' + str(i), min_value=32, max_value=64, step=16) #rewstricting complexity to combat overfitting
			#hp_filters = hp.Int('filters_' + str(i), min_value=32, max_value=128, step=32)
			hp_kernel_size = hp.Int('kernel_size_' + str(i), min_value=3, max_value=7, step=2)
			model.add(Conv1D(filters=hp_filters, kernel_size=hp_kernel_size, activation='relu', padding='same'))
			hp_pool_size = hp.Int('pool_size_' + str(i), min_value=2, max_value=4, step=2)
			model.add(MaxPooling1D(pool_size=hp_pool_size))

		model.add(Flatten())

		for i in range(hp.Int('num_dense_layers', 1, 3)):
			hp_units = hp.Int('units_' + str(i), min_value=32, max_value=192, step=32)
			model.add(Dense(units=hp_units, activation='relu'))
			hp_dropout = hp.Float('dropout_' + str(i), min_value=0.0, max_value=0.5, step=0.1)
			model.add(Dropout(hp_dropout))

		model.add(Dense(1, activation='sigmoid'))

		hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
		hp_batch_size = hp.Choice('batch_size', values=[32, 64, 128, 256])
		model.compile(optimizer=Adam(learning_rate=hp_learning_rate),
					  loss='binary_crossentropy',
					  metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])
	
		return model

	
	def tune_model_hyperparameters(st, user_id, tuner= False):
		
		epochs = 200
		split = .25
		if not tensorflow.config.list_physical_devices('GPU'):print("No GPU was detected. Using CPU instead.")
		else:print("GPU detected, using GPU for training.")
		ds, y = Trainer.get_sample(st,user_id,split)
		class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
		class_weights_dict = dict(enumerate(class_weights))
		early_stopping = EarlyStopping(
			monitor='val_auc_pr',  # Use the metric name here
			patience=15,
			restore_best_weights=True
		)
		tuner = kt.Hyperband(
			Trainer.build_1d_cnn_trainer_model,
			objective=kt.Objective('val_auc_pr', direction='max'),
			max_epochs=40,
			factor=3,
			directory='C:/dev/broker/backend/kt',
			project_name='1dcnn_lesscomplex'
		)
		tuner.search(ds, y, epochs=epochs, validation_split=0.2, callbacks=[early_stopping])
		best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
		model = tuner.hypermodel.build(best_hps)
		model.fit(
			ds, y, 
			epochs=epochs, 
			batch_size=best_hps.get('batch_size'),  # Use the tuned batch size
			validation_split=0.2, 
			callbacks=[early_stopping],
			class_weight=class_weights_dict
		)
		model.save(f'C:/dev/broker/backend/models/{user_id}_{st}')
		tensorflow.keras.backend.clear_session()
		


	def train_model(st, user_id):
		ds, y = Trainer.get_sample(st, user_id, .1)
		print(ds)
		_, num_time_steps, input_dim = ds.shape
		class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
		class_weights_dict = dict(enumerate(class_weights))


		model = Sequential()
		lucas_numbers = [3, 4, 7, 11, 18, 29, 47, 76]
		# Initial Conv1D layer as a feature extractor
		model.add(Conv1D(filters=lucas_numbers[0], kernel_size=3, activation='relu', input_shape=(num_time_steps, input_dim)))
    
		# LSTM layers as hidden layers
		for units in lucas_numbers[1:3]:  # Using Lucas numbers for LSTM layers
			model.add(LSTM(units=units, return_sequences=True))  # return_sequences=True for stacking LSTM layers
		model.add(LSTM(units=lucas_numbers[3], return_sequences=False))  # Last LSTM layer with return_sequences=False
    
		# Flatten the output of the LSTM layers before passing it to Dense layers
		model.add(Flatten())

		# Dense (MLP) layers as additional hidden layers
		for units in lucas_numbers[4:]:  # Using Lucas numbers for Dense layers
			model.add(Dense(units=units, activation='relu'))
			model.add(Dropout(0.5))  # Dropout for regularization
		model.add(Dense(1, activation='sigmoid'))
		model.compile(optimizer='adam', loss='binary_crossentropy', metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])

		early_stopping = EarlyStopping(
			monitor='auc_pr',
			patience=20,
			restore_best_weights=True,
			mode='max',
			verbose =1
		)

		history = model.fit(
			ds, y,
			epochs=200,
			batch_size=64,
			validation_split=0.1,
			#validation_split=0.2,
			callbacks=[early_stopping],
			#class_weight=class_weights_dict,
			verbose=1
		)

		# Save the model
		model.save(f'models/{user_id}_{st}.h5')

		# Clear the session to free memory
		tensorflow.keras.backend.clear_session()
		score = round(history.history['auc_pr'][-1] * 100)
		data.set_setup_info(user_id, st, score=score)
		return {st: {'score': score}}  # Return the auc pr value of the model to frontend

def train(args,user_id):
	st, = args
	history = Trainer.train_model(st,user_id)
	return json.dumps(history)

if __name__ == '__main__':
	print(train( ['EP'],4))




