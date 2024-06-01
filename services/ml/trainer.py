import tensorflow as tf,  datetime, time, random , numpy as np, os
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout, Conv1D, Flatten, Lambda, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from imblearn.over_sampling import SMOTE
from google.protobuf import text_format
from tensorflow_serving.config import model_server_config_pb2
#import grpc
#from tensorflow_serving.apis import model_management_pb2, model_management_pb2_grpc
import requests

class Trainer:

    def getSample(data,setupID,interval,trainingClassRatio, validationClassRatio, splitRatio):

        b = 3 # exclusive I think

        if 'd' in interval:
            timedelta = datetime.timedelta(days=b*int(interval[:-1]))
        elif 'w' in interval:
            timedelta = datetime.timedelta(weeks=b*int(interval[:-1]))
        elif 'm' in interval:
            timedelta = datetime.timedelta(weeks=b*int(interval[:-1]))
        elif 'h' in interval:
            timedelta = datetime.timedelta(hours=b*int(interval[:-1]))
        else:
            timedelta = datetime.timedelta(minutes=b*int(interval))
        with data.db.cursor() as cursor:
            yesQuery = """
            SELECT ticker_id, t, class FROM samples
            WHERE setup_id = %s AND class IS TRUE
            ORDER BY t;
            """

            cursor.execute(yesQuery, (setupID,))
            yesInstances = cursor.fetchall()

            numYes = len(yesInstances)
            t = trainingClassRatio
            v = validationClassRatio
            s = splitRatio
            z = t*s + v*(1-s)
            numYesTraining = int(numYes * (t*s / z))
            numYesValidation = int(numYes * (v*(1-s) / z))
            numNoTraining = int(numYesTraining * (1/t - 1))
            numNoValidation = int(numYesValidation * (1/v - 1))
            totalNo = numNoTraining + numNoValidation

            unionQuery = []

            for tickerID, t, _ in yesInstances:
                unionQuery.append(f"""
                (SELECT sample_id, ticker_id, t, class FROM samples
                WHERE ticker_id = {tickerID}
                AND setup_id = {setupID}
                AND class IS FALSE
                AND t between '{t - timedelta}' AND '{t + timedelta}'
                LIMIT {totalNo})
                """)
            noQuery = ' UNION '.join(unionQuery)
            cursor.execute(noQuery)
            noInstances = cursor.fetchall()
            noIDs = [x[0] for x in noInstances]
            noInstances = [x[1:] for x in noInstances]
            neededNo = totalNo - len(noInstances)


            if  neededNo > 0:
                randomNoQuery = f"""
                SELECT ticker_id, t, class FROM samples
                WHERE setup_id = {setupID}
                AND class IS FALSE
                AND sample_id NOT IN ({','.join(map(str, noIDs))})
                LIMIT {neededNo};
                """
                cursor.execute(randomNoQuery)
                noInstances += cursor.fetchall()
            

            random.shuffle(yesInstances)
            random.shuffle(noInstances)
            trainingInstances = yesInstances[:numYesTraining] + noInstances[:numNoTraining]
            validationInstances = yesInstances[numYesTraining:] + noInstances[numNoTraining:]
            random.shuffle(trainingInstances)
            random.shuffle(validationInstances)
            return np.array(trainingInstances), np.array(validationInstances)
   
    def getData(data, instances, interval, bars, pm=False):
        table, bucket, aggregate = data.getQueryInfo(interval, pm)
        ds = []
        classes = []
        for ticker_id, timestamp, class_info in instances:
            query = ""
            if aggregate:
                raise Exception('to code')
            else:
                query = f"""SELECT open, high, low, close
                            FROM {table}
                            WHERE ticker_id = {ticker_id} AND t <= '{timestamp}'
                            ORDER BY t DESC
                            LIMIT {bars}"""
            with data.db.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
            if len(results) < bars:
                continue  # Skip if insufficient data
            results = np.array(results, dtype=np.float64)
            results = np.log(results)
            close = np.roll(results[:,2], shift=1)
            results = results - close[:,np.newaxis]
            ds.append(results[1:])
            classes.append(class_info)
        return np.array(ds), np.array(classes)


    def createModel(data,bars,reqs):
        dolvol, adr, mcap = reqs
        reqs = np.array([dolvol, adr, mcap,-np.inf])
        def customLayer(x):
            metadata = x[:, 0,:]  
            conditions_met = tf.reduce_all(metadata >= reqs, axis=-1)
            conditions_met = tf.expand_dims(conditions_met, -1)
            conditions_met = tf.expand_dims(conditions_met, -1)
            croppedData = x[:, 1:bars+1,:]
            return tf.where(conditions_met, croppedData, tf.zeros_like(croppedData))
        model = Sequential()
        model.add(Input(shape=(None, 4))) # assuming o h l c
        model.add(Lambda(customLayer))
        conv_filter = 32
        kernal_size = 3
        lstm_list = [64, 32]
        dropout = .2
        model.add(Conv1D(filters=conv_filter, kernel_size=kernal_size, activation='relu'))
        for units in lstm_list[:-1]:
            model.add(Bidirectional(LSTM(units=units, return_sequences=True)))
            model.add(Dropout(dropout))
        model.add(Bidirectional(LSTM(units=lstm_list[-1], return_sequences=False)))
        model.add(Flatten())
        model.add(Dense(1, activation='sigmoid'))
        model.compile(optimizer=Adam(learning_rate=1e-3), loss='binary_crossentropy', metrics=[tf.keras.metrics.AUC(curve='PR', name='auc_pr')])
        return model

    def train_model(data,setupID):
        splitRatio = .85
        trainingClassRatio = .25
        validationClassRatio = .05
        with data.db.cursor() as cursor:
            cursor.execute('SELECT i, bars, model_version, dolvol, adr, mcap FROM setups WHERE setup_id = %s', (setupID,))
            traits = cursor.fetchone()
        interval = traits[0]
        if interval != "1d":
            return 'invalid tf'
        bars = traits[1]
        modelVersion = traits[2] + 1
        reqs = traits[3:6]
        model = Trainer.createModel(data,bars,reqs)
        trainingSample, validationSample = Trainer.getSample(data,setupID,interval,trainingClassRatio, validationClassRatio, splitRatio)
        xTrainingData, yTrainingData = Trainer.getData(data,trainingSample,interval,bars)
        xValidationData, yValidationData = Trainer.getData(data,validationSample,interval,bars)
        failure = (len(xTrainingData) + len(xValidationData)) / (len(trainingSample) + len(validationSample))
        print(f"{failure * 100}% failure of {len(trainingSample) + len(validationSample)} samples")
        print("training class ratio",np.mean(yTrainingData))
        print("validation class ratio", np.mean(yValidationData))
        early_stopping = EarlyStopping(
            monitor='val_auc_pr',
            patience=5,
            restore_best_weights=True,
            mode='max',
            verbose =1
        )
        history = model.fit(xTrainingData, yTrainingData,epochs=100,batch_size=64,validation_data=(xValidationData, yValidationData),callbacks=[early_stopping])
        tf.keras.backend.clear_session()
        score = round(history.history['val_auc_pr'][-1] * 100)
        with data.db.cursor() as cursor:
            cursor.execute("UPDATE setups SET score = %s, model_version = %s WHERE setup_id = %s;", (score, modelVersion, setupID))
        data.db.commit()
        Trainer.save(data,setupID,modelVersion,model)
        size = None
        for val, ident in [[size,'sample_size'],[score,'score']]:
            if val != None:
                with data.db.cursor() as cursor:
                    query = f"UPDATE setups SET {ident} = %s WHERE setup_id = %s;"
                    cursor.execute(query, (val, setupID))
        data.db.commit()
        return score 

    def save(data,setupID,modelVersion,model):
        model_folder = f"models/{setupID}/{modelVersion}"
        #model_path = f"{model_folder}/model.keras"
        configPath = "/models/models.config"
        if not os.path.exists(model_folder):
            os.makedirs(model_folder)
        #model.save(model_path)#, save_format='tf')
        #model.save(model_folder)
        model.export(model_folder)
        config = model_server_config_pb2.ModelServerConfig()
        with open(configPath, 'r') as f:
            text_format.Merge(f.read(), config)
        config_exists = False
        for model in config.model_config_list.config:
            if model.name == str(setupID):
                config_exists = True
                break
        if not config_exists:
            new_model_text = f"""
            model_config_list {{
                config {{
                    name: "{setupID}"
                    base_path: "/models/{setupID}"
                    model_platform: "tensorflow"
                    model_version_policy {{ all {{}} }}
                }}
            }}
            """
            new_model_config = model_server_config_pb2.ModelServerConfig()
            text_format.Merge(new_model_text, new_model_config)
            config.model_config_list.config.extend(new_model_config.model_config_list.config)
            with open(configPath, 'w') as f:
                f.write(text_format.MessageToString(config))
#        # Reload the config no even if config not changed so that it can update to new model version
#        url = "http://tf:8501/v1/config/reload"
#        #data.tf + "v1/config/reload"
#        response = requests.post((url))
#        if response.status_code == 200:
#            print("reloaded tf")
#        else:
#            print(f"reload failed {response.text}")

        if False: #reload request, might work to just have the auto reload handle it
            try:
                # Create a channel to the TensorFlow Serving gRPC server
                channel = grpc.insecure_channel('tf:8500')
                
                # Create a stub (client)
                stub = model_management_pb2_grpc.ModelServiceStub(channel)
                
                # Create a ReloadConfigRequest
                request = model_management_pb2.ReloadConfigRequest()
                
                # Populate the request with the new configuration
                #with open(configPath, 'r') as f:
                    #                config_text = f.read()
                
                #new_config = model_server_config_pb2.ModelServerConfig()
                #text_format.Merge(config_text, new_config)
                
                request.config.CopyFrom(config)
                
                # Send the request
                response = stub.HandleReloadConfigRequest(request)
                
                if response.status.error_code == 0:
                    print("Successfully reloaded config")
                else:
                    print(f"Failed to reload config: {response.status.error_message}")
            except grpc.RpcError as e:
                print(f"gRPC call failed: {e}")

            if config_exists:
                print(f"Model {setupID} already exists in the configuration.")


def train(data,setupID):
    results = Trainer.train_model(data,setupID)
    return results

if __name__ == '__main__':
    from data import Data
    print(train(Data(False),1))
