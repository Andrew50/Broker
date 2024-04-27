import tensorflow as tf,  datetime, time, random , numpy as np, os
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, LSTM, Bidirectional, Dropout, Conv1D, Flatten, Lambda, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from imblearn.over_sampling import SMOTE
import re

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
   
#    def getData(data,instances,interval,bars,pm = False):
#
#        table, bucket,aggregate = data.getQueryInfo(interval, pm)
#
#        queries = []
#        print(len(instances))
#        for ticker_id, timestamp, _ in instances:
#            query = "("
#            if aggregate:
#                query += f"SELECT  first(open, t), max(high), min(low), last(close, t), sum(volume) "
#            else:
#                query += "SELECT open, high, low, close, volume "
#            query += f"""FROM {table} WHERE ticker_id = {ticker_id} 
#                    AND time_bucket('{bucket}',t) <= '{timestamp}' """
#        #    if not timestamp.IsZero():
#        #        query += f"AND bucket <= {timestamp} "
#            if not pm and "extended" in table:
#                query += "AND extended_hours = true "
#            if aggregate:
#                query += f"GROUP BY time_bucket('{bucket}',t) "
#            query += f"ORDER BY time_bucket('{bucket}', t) DESC LIMIT {bars + 1} )"
#            queries.append(query)
#
#        combined_query = " UNION ALL ".join(queries)
#        with data.db.cursor() as cursor:
#            cursor.execute(combined_query)
#            results = cursor.fetchall()
#        ds = []
#        classes = []
#        for result, i in enumerate(results):
#            if len(result) != bars:
#                continue
#            result = [np.inf for _ in range(4)] + result
#            classes.append(instances[i][2])
#            ds.append(results)
#        ds = np.array(ds,dtype=np.float64)
#        ds = np.diff(np.log(ds),axis=0)
#        classes = np.array(classes)
#        return ds, classes
#
#        return results

    def getData(data, instances, interval, bars, pm=False):
        table, bucket, aggregate = data.getQueryInfo(interval, pm)
        ds = []
        classes = []
        for ticker_id, timestamp, class_info in instances:
            query = ""
            args = [ticker_id]
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

    def train_model(data,setupID):
        splitRatio = .85
        trainingClassRatio = .25
        validationClassRatio = .05
        with data.db.cursor() as cursor:
            cursor.execute('SELECT i, bars, model_version, dolvol, adr, mcap FROM setups WHERE setup_id = %s', (setupID,))
            traits = cursor.fetchone()
        interval = traits[0]
        bars = traits[1]
        modelVersion = traits[2] + 1
        reqs = traits[3:6]
        model = Trainer.createModel(data,bars,reqs)
        trainingSample, validationSample = Trainer.getSample(data,setupID,interval,trainingClassRatio, validationClassRatio, splitRatio)
        xTrainingData, yTrainingData = Trainer.getData(data,trainingSample,interval,bars)
        xValidationData, yValidationData = Trainer.getData(data,validationSample,interval,bars)
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

        model_path = f"models/{setupID}/{modelVersion}"
        model.save(model_path, save_format='tf')

        tf.keras.backend.clear_session()
        score = round(history.history['val_auc_pr'][-1] * 100)
        with data.db.cursor(buffered=True) as cursor:
            cursor.execute("UPDATE setups SET score = %s, model_version = %s WHERE setup_id = %s;", (score, modelVersion, setupID))
        data.db.commit()
        data.set_setup_info(user_id, st, score=score)
        return score 

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

def train(data,setupID):
    results = Trainer.train_model(data,setupID)
    return results

if __name__ == '__main__':
    from data import Data
    print(train(Data(False),1))

    




