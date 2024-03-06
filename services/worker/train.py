from tensorflow.keras.models import Sequential
import sys, os
from tcn import TCN
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout, Conv1D, MaxPooling1D, Flatten, Attention, GRU 
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import backend, metrics
import keras_tuner as kt

def train(mt,tx,ty,vx,vy,parameters):
    _, timesteps, features = tx.shape
    def custom_layer(hp_units, return_sequences,i):
        i = str(i)
        if mt == 'bilstm':
            return (Bidirectional(LSTM(name = mt+'_'+i,units=hp_units, return_sequences=return_sequences)))
        elif mt == 'lstm':
            return LSTM(name = mt+'_'+i,units=hp_units, return_sequences=return_sequences)
        elif mt == 'gru':
            return GRU(name = mt+'_'+i,units=hp_units, return_sequences=return_sequences)
        elif mt == 'transformer': #also need to have it with positional encoding
            return
        elif mt == 'gcn':
            return
        elif mt == 'dkf':
            return

    def create_model(hp):
        layers = [1,2,3] #first to second, inclusive i think
        units = [8, 16, 32, 64, 96]
        #dropout = 0.0, .5, .1
        dropout = [0.0,.2,.3,.4,.5]
        batch_size = [32, 64, 128, 256]
        learning_rate = [1e-1,1e-2,1e-3,1e-4,1e-5]
        hidden = [0,1]

        pre_layers = [0]#[0,1,2]
        pre_layer_types = ['cnn','tcn']
        kernel_size = [3,5,7]
        filters = units
        nb_stack = [1,2,3]

        model = Sequential()
        for i in range(hp.Choice('pre_layers', values = pre_layers)):
            pre_layer_type = hp.Choice(f'pre_layer_{i}_type',values = pre_layer_types)
            if pre_layer_type == 'tcn':
                model.add(TCN(
                    name = f'tcn_{i}',
                    nb_filters=hp.Choice(f'tcn_{i}_filters',values = filters),
                    kernel_size=hp.Choice(f'tcn_{i}_kernel_size', values=kernel_size),
                    nb_stacks= hp.Choice(f'tcn_{i}_stacks',values = nb_stack),#hp.Int('tcn_1_nb_stacks', min_value=1, max_value=3, step=1),
                    dilations=[1, 2, 4, 8],
                    activation='relu',
                    padding='causal',
                    use_skip_connections=hp.Boolean(f'tcn_{i}_skip_connections'),
                    input_shape=(timesteps, features) if i == 0 else (None, features),
                    return_sequences=True
                ))

            #might want to add optional pooling layer(s) after cnn
            elif pre_layer_type == 'cnn':
                model.add(Conv1D(
                    name = f'cnn_{i}',
                    filters=hp.Choice(f'cnn_{i}_filters',values = filters),
                    kernel_size=hp.Choice(f'cnn_{i}_kernel_size', values=kernel_size),
                    activation='relu',
                    padding='same',
                    input_shape=(timesteps, features) if i == 0 else (None, features),
                ))
        #use_attention = hp.Choice('attention',values = [True,False])
        for i in range(hp.Choice('layers', values = layers)):
            hp_units = hp.Choice('units_' + str(i), values = units)
            return_sequences = True if i < hp.get('layers') - 1 else False
            model.add(custom_layer(hp_units,return_sequences,i))
        #    if use_attention:
        #        model.add(Attention())
            hp_hidden = hp.Choice('dense_' + str(i), values = hidden)
            if hp_hidden:
                model.add(Dense(hp.Choice('units_dense_' + str(i),values = units)))
            hp_dropout = hp.Choice('dropout_' + str(i), values=dropout) #min_value=dropout[0], max_value=dropout[1], step=dropout[2])
            model.add(Dropout(hp_dropout))
        hp_batch_size = hp.Choice('batch_size', values=batch_size)
        model.add(Dense(1, activation='sigmoid'))
        hp_learning_rate = hp.Choice('learning_rate', values=learning_rate)
        auc_pr = metrics.AUC(curve='PR', name='auc_pr')
        model.compile(optimizer=Adam(learning_rate=hp_learning_rate),
                      loss='binary_crossentropy',
                      #metrics=['accuracy',auc_pr])
                      metrics=[auc_pr])

        return model

    #if tensorflow.config.list_physical_devices('GPU'): print('using gpu')
    sys.stdout = open(os.devnull, 'w')
    early_stopping = EarlyStopping(monitor='auc_pr',patience=15,restore_best_weights=True)
#     tuner = kt.Hyperband(
#         build_model,
#         objective=kt.Objective('val_auc_pr', direction='max'),
#         max_epochs=40,
#         factor=3,
#         directory='.',
#         project_name='olympics'
#     )
    # tuner.search(ds, y, epochs=epochs, validation_data=(vx, vy), callbacks=[early_stopping])
    tuner = kt.BayesianOptimization(
            create_model,
            objective=kt.Objective('val_auc_pr',direction='max'),
            max_trials=100,
            num_initial_points = 10,
            directory='.',
            project_name='tuner/bayesian_olympics2-'+('-').join([str(x) for x in parameters])
            )
    tuner.search(tx,ty,epochs=25,validation_data=(vx,vy))
    backend.clear_session()
    sys.stdout = sys.__stdout__
    return tuner




