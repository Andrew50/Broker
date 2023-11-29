import numpy as np
import random
import tensorflow, os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout, Conv1D, MaxPooling1D, Flatten
from tensorflow.keras.optimizers import Adam
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Bidirectional
from tensorflow.python import training
try: 
	import keras_tuner as kt
	import matplotlib.pyplot as plt
except: pass
from tensorflow.keras.callbacks import EarlyStopping
from sync_Data import data
import json
from imblearn.over_sampling import SMOTE


from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split


from imblearn.pipeline import Pipeline
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import train_test_split
from keras.optimizers import SGD
from tcn import TCN, tcn_full_summary

class Trainer:




	def get_sample(st, user_id):
		training_ratio, validation_ratio, oversample = .2, .1, 1
		
		all_instances, tf, setup_length = data.get_setup_sample(user_id, st)
		yes_instances = [x for x in all_instances if x[2] == 1]
		no_instances = [x for x in all_instances if x[2] == 0]
		
		
		print(len(yes_instances))
		# For validation set
		num_yes_validation = len(yes_instances)
		num_no_validation = int((num_yes_validation / validation_ratio) - num_yes_validation)
		validation_instances = yes_instances + random.sample(no_instances, num_no_validation)
		validation_x, validation_y = data.get_ds('trainer', validation_instances, tf, setup_length)

		num_yes_training = len(yes_instances) * oversample
		num_no_training = int((num_yes_training / training_ratio) - num_yes_training)
		training_instances = yes_instances + random.sample(no_instances, num_no_training)
		
		training_x, training_y = data.get_ds('trainer', training_instances, tf, setup_length)

		# Reshape training set for SMOTE
		_, shape_1, shape_2 = training_x.shape
		training_x = training_x.reshape(-1, shape_1 * shape_2)

		# Apply SMOTE
		#print(f'pre ratio {np.mean(training_y)}')
		smote_percent = training_ratio / (1 - training_ratio)
		smote = SMOTE(sampling_strategy=smote_percent)
		training_x, training_y = smote.fit_resample(training_x, training_y)

		# Reshape training set back to original shape
		training_x = training_x.reshape(-1, shape_1, shape_2)

		print(f"Training set size: {len(training_y)}, Class balance: {np.mean(training_y)}")
		print(f"Validation set size: {len(validation_y)}, Class balance: {np.mean(validation_y)}")
	
		return training_x, training_y, validation_x, validation_y

	
	
	def train_model(st, user_id):

		ds, y, ds_val, y_val = Trainer.get_sample(st, user_id)
		_, num_time_steps, input_dim = ds.shape
		model = Sequential()
		

		



		
		conv_filter = 50
		kernal_size = 3
		lstm_list = [64,64,32,32]
		dense_list = [32,16]
		dropout = .2

		
		model.add(Conv1D(filters=conv_filter, kernel_size=kernal_size, activation='relu', input_shape=(num_time_steps, input_dim)))
		for units in lstm_list[:-1]: 
			model.add(Bidirectional(LSTM(units=units, return_sequences=True)))  # return_sequences=True for stacking LSTM layers
		model.add(Bidirectional(LSTM(units=lstm_list[-1], return_sequences=False)))  # Last LSTM layer with return_sequences=False
		model.add(Flatten())
		for units in dense_list:  # Using Lucas numbers for Dense layers
			model.add(Dense(units=units, activation='sigmoid'))
			model.add(Dropout(dropout))  # Dropout for regularization
		model.add(Dense(1, activation='sigmoid'))
		opt = SGD(learning_rate=0.0001)
		#model.compile(loss = "categorical_crossentropy", optimizer = opt)
		#model.compile(optimizer='adam', loss='binary_crossentropy', metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])
		model.compile(optimizer=opt, loss='binary_crossentropy', metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])





		# model = Sequential([Bidirectional(LSTM(64, input_shape=(ds.shape[1], ds.shape[2]), return_sequences=True,),), Dropout(
		# 	0.2), Bidirectional(LSTM(32)), Dense(1, activation='sigmoid'),])
		# model.compile(loss='binary_crossentropy',
		# 			  optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])




		# model = Sequential([
		# 	TCN(input_shape=(num_time_steps, input_dim)),
		# 	Dense(1, activation='sigmoid')
		# ])

		# model.compile(optimizer='adam', loss='binary_crossentropy', metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])
		# tcn_full_summary(model, expand_residual_blocks=False)


		early_stopping = EarlyStopping(
			#monitor='val_auc_pr',
			monitor='val_auc_pr',
			patience=40,
			restore_best_weights=True,
			mode='max',
			verbose =1
		)

		history = model.fit(
			ds, y,
			epochs=200,
			batch_size=64,
			validation_data=(ds_val, y_val),  # Use the actual validation set here
			callbacks=[early_stopping],
			verbose=1
		)
		
		if not os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
			print('saved model --------------------')
			model.save(f'C:/dev/broker/backend/models/{user_id}_{st}', save_format='tf')
			#model.save(f'C:/dev/broker/backend/models/{user_id}_{st}.h5')
		else:
			model.save(f'models/{user_id}_{st}', save_format='tf')
			#model.save(f'models/{user_id}_{st}.h5')
			
		tensorflow.keras.backend.clear_session()
		score = round(history.history['val_auc_pr'][-1] * 100)
		data.set_setup_info(user_id, st, score=score)
		return {st: {'score': score}}  # Return the auc pr value of the model to frontend

def train(args,user_id):
	st, = args
	history = Trainer.train_model(st,user_id)
	return json.dumps(history)

if __name__ == '__main__':

	print(train( ['F'],4))








	# def build_lstm_trainer_model(hp):
	# 	model = Sequential()
	# 	for i in range(hp.Int('num_lstm_layers', 1, 3)):
	# 		hp_units = hp.Int('units_' + str(i), min_value=32, max_value=192, step=32)
	# 		return_sequences = True if i < hp.get('num_lstm_layers') - 1 else False
	# 		model.add(Bidirectional(LSTM(units=hp_units, return_sequences=return_sequences)))
	# 		hp_dropout = hp.Float('dropout_' + str(i), min_value=0.0, max_value=0.5, step=0.1)
	# 		model.add(Dropout(hp_dropout))
	# 	hp_batch_size = hp.Choice('batch_size', values=[32, 64, 128, 256])
	# 	model.add(Dense(1, activation='sigmoid'))
	# 	hp_learning_rate = hp.Choice('learning_rate', values=[1e-1, 1e-2, 1e-3, 1e-4, 1e-5])
	# 	auc_pr = tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')
	# 	model.compile(optimizer=Adam(learning_rate=hp_learning_rate),
	# 				  loss='binary_crossentropy',
	# 				  #metrics=['accuracy',auc_pr])
	# 				  metrics=[auc_pr])
	# 	return model








	# def build_1d_cnn_trainer_model(hp):
	# 	model = Sequential()
	# 	for i in range(hp.Int('num_conv_layers', 1, 2)): #restricting complexity
	# 		hp_filters = hp.Int('filters_' + str(i), min_value=32, max_value=64, step=16) #rewstricting complexity to combat overfitting
	# 		#hp_filters = hp.Int('filters_' + str(i), min_value=32, max_value=128, step=32)
	# 		hp_kernel_size = hp.Int('kernel_size_' + str(i), min_value=3, max_value=7, step=2)
	# 		model.add(Conv1D(filters=hp_filters, kernel_size=hp_kernel_size, activation='relu', padding='same'))
	# 		hp_pool_size = hp.Int('pool_size_' + str(i), min_value=2, max_value=4, step=2)
	# 		model.add(MaxPooling1D(pool_size=hp_pool_size))

	# 	model.add(Flatten())

	# 	for i in range(hp.Int('num_dense_layers', 1, 3)):
	# 		hp_units = hp.Int('units_' + str(i), min_value=32, max_value=192, step=32)
	# 		model.add(Dense(units=hp_units, activation='relu'))
	# 		hp_dropout = hp.Float('dropout_' + str(i), min_value=0.0, max_value=0.5, step=0.1)
	# 		model.add(Dropout(hp_dropout))

	# 	model.add(Dense(1, activation='sigmoid'))

	# 	hp_learning_rate = hp.Choice('learning_rate', values=[1e-2, 1e-3, 1e-4])
	# 	hp_batch_size = hp.Choice('batch_size', values=[32, 64, 128, 256])
	# 	model.compile(optimizer=Adam(learning_rate=hp_learning_rate),
	# 				  loss='binary_crossentropy',
	# 				  metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])
	
	# 	return model

	
	# def tune_model_hyperparameters(st, user_id, tuner= False):
		
	# 	epochs = 200
	# 	split = .25
	# 	if not tensorflow.config.list_physical_devices('GPU'):print("No GPU was detected. Using CPU instead.")
	# 	else:print("GPU detected, using GPU for training.")
	# 	ds, y = Trainer.get_sample(st,user_id,split)
	# 	class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
	# 	class_weights_dict = dict(enumerate(class_weights))
	# 	early_stopping = EarlyStopping(
	# 		monitor='auc_pr',  # Use the metric name here
	# 		patience=15,
	# 		restore_best_weights=True
	# 	)
	# 	tuner = kt.Hyperband(
	# 		Trainer.build_1d_cnn_trainer_model,
	# 		objective=kt.Objective('val_auc_pr', direction='max'),
	# 		max_epochs=40,
	# 		factor=3,
	# 		directory='C:/dev/broker/backend/kt',
	# 		project_name='1dcnn_lesscomplex'
	# 	)
	# 	tuner.search(ds, y, epochs=epochs, validation_split=0.2, callbacks=[early_stopping])
	# 	best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
	# 	model = tuner.hypermodel.build(best_hps)
	# 	model.fit(
	# 		ds, y, 
	# 		epochs=epochs, 
	# 		batch_size=best_hps.get('batch_size'),  # Use the tuned batch size
	# 		validation_split=0.2, 
	# 		callbacks=[early_stopping],
	# 		class_weight=class_weights_dict
	# 	)
	# 	model.save(f'C:/dev/broker/backend/models/{user_id}_{st}')
	# 	tensorflow.keras.backend.clear_session()

	




