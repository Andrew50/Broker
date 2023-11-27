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






class Trainer:
	
	def get_sample(st,user_id,use):
		all_setups, tf, setup_length = data.get_setup_sample(user_id, st)
		yes = [sublist for sublist in all_setups if sublist[2] == 1]
		data.set_sample_size(user_id,st,len(yes))
		print('set')
		random.shuffle(all_setups)
		no = [sublist for sublist in all_setups if sublist[2] == 0][:int(len(yes) / use)]
		sample = yes + no
		random.shuffle(sample)
		ds, y = data.get_ds('trainer', sample, tf, setup_length)
		ds = ds[:, :, 1:5]
		ds = np.flip(ds,1)
		return ds, y

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
		

	def train_model(st,user_id):
		ds, y = Trainer.get_sample(st,user_id,.01)
		
		#num_time_steps = #... (e.g., 100)
		#input_dim = 4  # Assuming you have 4 feature
		#s per time step as per your description
		_,num_time_steps, input_dim = ds.shape
		class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
		class_weights_dict = dict(enumerate(class_weights))

		model = Sequential()
	
		# Convolutional and pooling layers with hard-coded hyperparameters
		model.add(Conv1D(filters=96, kernel_size=7, activation='relu', input_shape=(num_time_steps, input_dim), padding='same'))
		model.add(MaxPooling1D(pool_size=4))
		model.add(Conv1D(filters=32, kernel_size=3, activation='relu', padding='same'))
		model.add(MaxPooling1D(pool_size=2))
		model.add(Conv1D(filters=32, kernel_size=7, activation='relu', padding='same'))
		model.add(MaxPooling1D(pool_size=2))
		model.add(Flatten())
	
		# Dense layers with hard-coded hyperparameters
		model.add(Dense(units=192, activation='relu'))
		model.add(Dropout(0.2))
		model.add(Dense(units=64, activation='relu'))
		model.add(Dropout(0.4))
		model.add(Dense(units=32, activation='relu'))
		model.add(Dropout(0.2))
	
		# Output layer
		model.add(Dense(1, activation='sigmoid'))

		# Compile the model
		model.compile(optimizer=Adam(learning_rate=0.01),
					  loss='binary_crossentropy',
					  metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])

		# Define early stopping callback
		early_stopping = EarlyStopping(
			monitor='val_auc_pr',  # Use the metric name here
			patience=35,
			restore_best_weights=True
		)

		# Fit the model to the training data
		history = model.fit(
			ds, y,
			epochs=200, 
			batch_size=64,  # This batch size is from your hyperparameter tuning results
			validation_split=0.2, 
			callbacks=[early_stopping],
            class_weight=class_weights_dict
		)

		# Save the model, replace 'path_to_my_model' with the actual path
		model.save(f'models/{user_id}_{st}.h5')

		# Clear the session to free memory
		tensorflow.keras.backend.clear_session()
		return history.history


# Plot training & validation loss values
		plt.figure(figsize=(12, 6))
		plt.plot(history.history['auc_pr'], label='Train AUC')
		plt.plot(history.history['val_auc_pr'], label='Validation AUC')
		plt.title('Model AUC Progress During Training')
		plt.ylabel('AUC')
		plt.xlabel('Epoch')
		plt.legend(['Train', 'Validation'], loc='lower right')
		plt.show()
		return history



def train(args,user_id):
	st, = args
	history = Trainer.train_model(st,user_id)
	#history = Trainer.tune_model_hyperparameters(st,user_id)
	return json.dumps(history)


if __name__ == '__main__':
	train( ['EP'],4)




