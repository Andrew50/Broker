import tensorflow,  datetime, time, random , numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout, Conv1D, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from imblearn.over_sampling import SMOTE

class Trainer:

    def get_ds(data,instances, tf, setup_length): #no reason to try and be efficient by getting everything becuase its prolly just faster to get it one by one becuase thae change of overlaps is low and date is unkown
        ds = []
        values = []
        for ticker, dt, value in instances:
            try:
                df = data.get_df('trainer',ticker,tf,dt,setup_length)
                ds.append(df)
            except TimeoutError:
                pass
            else:
                values.append(value)
        return np.array(ds), np.array(values)

    def sample(data,st, user_id):
        training_ratio, validation_ratio, oversample = .25, .05, 1.5
        #training_ratio, validation_ratio, oversample = .3, .2, 1.05
        
        all_instances, tf, setup_length = data.get_sample(user_id, st)
        yes_instances = [x for x in all_instances if x[2] == 1]
        no_instances = [x for x in all_instances if x[2] == 0]
        print(len(yes_instances), len(no_instances))
        
        data.set_setup_info(user_id,st,size = len(yes_instances))
        
        # For validation set
        num_yes_validation = len(yes_instances)
        num_no_validation = int((num_yes_validation / validation_ratio) - num_yes_validation)
        validation_instances = yes_instances + random.sample(no_instances, num_no_validation)
        validation_x, validation_y = Trainer.get_ds(data,validation_instances, tf, setup_length)
        print(validation_x.shape)

        num_yes_training = len(yes_instances) * oversample
        num_no_training = int((num_yes_training / training_ratio) - num_yes_training)
        training_instances = yes_instances + random.sample(no_instances, num_no_training)
        
        training_x, training_y = Trainer.get_ds(data,training_instances, tf, setup_length)
        # Reshape training set for SMOTE


        _, shape_1, shape_2 = training_x.shape
        training_x = training_x.reshape(-1, shape_1 * shape_2)

        # Apply SMOTE
        smote_percent = training_ratio / (1 - training_ratio)
        smote = SMOTE(sampling_strategy=smote_percent)
        training_x, training_y = smote.fit_resample(training_x, training_y)

        # Reshape training set back to original shape
        training_x = training_x.reshape(-1, shape_1, shape_2)

        print(f"Training set size: {len(training_y)}, Class balance: {np.mean(training_y)}")
        print(f"Validation set size: {len(validation_y)}, Class balance: {np.mean(validation_y)}")
    
        return training_x, training_y, validation_x, validation_y
    
    def train_model(data,st, user_id):

        ds, y, ds_val, y_val = Trainer.sample(data,st, user_id)
        _, num_time_steps, input_dim = ds.shape
        model = Sequential()

        conv_filter = 32
        kernal_size = 3
        lstm_list = [64,32]
        dense_list = []
        dropout = .2

        # for i in range(len(ds)):
        #   if y[i] == 1:
    #       print(ds[i,:,:])
            
        #       input()
        model.add(Conv1D(filters=conv_filter, kernel_size=kernal_size, activation='relu', input_shape=(num_time_steps, input_dim)))
        for units in lstm_list[:-1]: 
            model.add(Bidirectional(LSTM(units=units, return_sequences=True)))  # return_sequences=True for stacking LSTM layers
            model.add(Dropout(.2))
        model.add(Bidirectional(LSTM(units=lstm_list[-1], return_sequences=False)))  # Last LSTM layer with return_sequences=False
        model.add(Flatten())
        for units in dense_list:  # Using Lucas numbers for Dense layers
            model.add(Dense(units=units, activation='sigmoid'))
            model.add(Dropout(dropout))  # Dropout for regularization
        model.add(Dense(1, activation='sigmoid'))
        #opt = SGD(learning_rate=0.0001)
        #model.compile(loss = "categorical_crossentropy", optimizer = opt)
        #model.compile(optimizer='adam', loss='binary_crossentropy', metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])
        model.compile(optimizer=Adam(learning_rate=1e-3), loss='binary_crossentropy', metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])


        # model = Sequential([Bidirectional(LSTM(64, input_shape=(ds.shape[1], ds.shape[2]), return_sequences=True,),), Dropout(
        #   0.2), Bidirectional(LSTM(32)), Dense(1, activation='sigmoid'),])
        # model.compile(loss='binary_crossentropy',
        #             optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])

        # model = Sequential([
        #   TCN(input_shape=(num_time_steps, input_dim)),
        #   Dense(1, activation='sigmoid')
        # ])

        # model.compile(optimizer='adam', loss='binary_crossentropy', metrics=[tensorflow.keras.metrics.AUC(curve='PR', name='auc_pr')])
        # tcn_full_summary(model, expand_residual_blocks=False)


        early_stopping = EarlyStopping(
            monitor='val_auc_pr',
            patience=5,
            restore_best_weights=True,
            mode='max',
            verbose =1
        )

        history = model.fit(ds, y,epochs=30,batch_size=64,validation_data=(ds_val, y_val),)  # Use the actual validation set herecallbacks=[early_stopping],verbose=1)
        
        # if not os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False):
        #   print('saved model -----------outside container so kinda useless god---------')
        #   model.save(f'C:/dev/broker/backend/models/{user_id}_{st}', save_format='tf')
        #   #model.save(f'C:/dev/broker/backend/models/{user_id}_{st}.h5')
        # else:
        data.set_model(user_id, st, model)
        #model.save(f'models/{user_id}_{st}',save_format = 'tf')
            #model.save(f'models/{user_id}_{st}.h5')
            
        tensorflow.keras.backend.clear_session()
        score = round(history.history['val_auc_pr'][-1] * 100)
        data.set_setup_info(user_id, st, score=score)
        return {st: {'score': score}}  # Return the auc pr value of the model to frontend
    


    def run_generator(data,st,user_id): #busted
        i = 0
        model = Screener.load_model(user_id,st)
        prev_length = None
        while True:
            print('in generator',flush=True)
            length = data.get_trainer_queue_size(user_id,st)
            print('trainer queue length: ',length,flush=True)
            if length != prev_length:
                start = datetime.datetime.now()
                print('generator timeout reset',flush=True)
            if (datetime.datetime.now() - start).seconds > 60:
                break
            if length < 20:
                print('running trainer screener',flush=True)
                if i == 0:
                    sample,_,_ = data.get_sample(user_id,st)
                    sample = [[ticker,dt] for ticker,dt,val in sample]
                    query = sample
                    i = 1
                elif i == 1:
                    raise Warning('to code')
                # elif i == 1:
                #   query = []
                #   for setup in sample:
                #       #get neihgbor
                #       neighbors = get_neighbors(setup)
                #       for neighbor in neighbors:
                #           if neighbor not in sample:
                #               query.append(neighbor)
                #   i = 2
                #elif i == 2:
                    #random
                instances = Screener.screen(user_id,st,'trainer',query,.3,model)
                [data.set_trainer_queue(user_id,st,instance) for instance in instances]
            prev_length = length
            time.sleep(10)
        return


def train(data,user_id,st):
    results = Trainer.train_model(data,st,user_id)
    return results


def start(data,user_id,st):
    Trainer.run_generator(data,st,user_id)


if __name__ == '__main__':
    from data import Data
    print(train(Data(False),1, 'P'))

    




