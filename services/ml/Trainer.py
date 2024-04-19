import tensorflow as tf,  datetime, time, random , numpy as np
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
   
    def getData(data,instances,interval,bars,pm = False):

        table, bucket,aggregate = data.getQueryInfo(interval, pm)

        queries = []
        for ticker_id, timestamp, _ in instances:
            if aggregate:
                raise Exception("Aggregation not implemented for models...yet?")
                query = f"""
                    (SELECT
                        bucket,
                        LOG(first_open) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_open,
                        LOG(max_high) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_high,
                        LOG(min_low) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_low,
                        LOG(last_close) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_close
                    FROM (
                        SELECT
                            time_bucket('{bucket}', q.t) AS bucket,
                            first(q.open, q.t) AS first_open,
                            max(q.high) AS max_high,
                            min(q.low) AS min_low,
                            last(q.close, q.t) AS last_close
                        FROM {table} AS q
                        WHERE q.ticker_id = {ticker_id} AND q.t <= '{timestamp}'
                        GROUP BY bucket
                        ORDER BY bucket DESC
                        LIMIT {bars}
                    ) AS subquery
                    ORDER BY bucket ASC)
                    """
            else:
               query = f"""
                    (SELECT
                        bucket,
                        LOG(first_open) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_open,
                        LOG(max_high) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_high,
                        LOG(min_low) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_low,
                        LOG(last_close) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_close
                    FROM (
                        SELECT
                            q.t AS bucket,
                            q.open AS first_open,
                            q.high AS max_high,
                            q.low AS min_low,
                            q.close AS last_close
                        FROM {table} AS q
                        WHERE q.ticker_id = {ticker_id} AND q.t <= '{timestamp}'
                        ORDER BY q.t DESC
                        LIMIT {bars}
                    ) AS subquery
                    ORDER BY bucket ASC)
                    """
            queries.append(query)
        combined_query = " UNION ALL ".join(queries)
        with data.db.cursor() as cursor:
            cursor.execute(combined_query)
            results = cursor.fetchall()


        ds = []
        classes = []
        for result, i in enumerate(results):
            if len(result) != bars:
                continue
            result = [np.inf for _ in range(4)] + result
            classes.append(instances[i][2])
            ds.append(results)
        ds = np.array(ds)
        classes = np.array(classes)
        return ds, classes
    
    def train_model(data,setupID):
        splitRatio = .85
        trainingClassRatio = .25
        validationClassRatio = .05
        with data.db.cursor() as cursor:
            cursor.execute('SELECT i, bars, dolvol, adr, mcap FROM setups WHERE setup_id = %s', (setupID,))
            traits = cursor.fetchone()
        interval = traits[0]
        bars = traits[1]
        reqs = traits[2:5]
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
        history = model.fit(xTrainingData, yTrainingData,epochs=30,batch_size=64,validation_data=(xValidationData, yValidationData),callbacks=[early_stopping])

        model_id = f"model:{setupID}"
        model_path = f"models/{model_id}"
        model.save(model_path, save_format='tf')
        with open(model_path, 'rb') as model_file:
            model_blob = model_file.read()
        data.cache.modelstore(model_key=model_id, backend='TF', device='CPU', model=model_blob)

        tf.keras.backend.clear_session()
        score = round(history.history['val_auc_pr'][-1] * 100)
        with data.db.cursor(buffered=True) as cursor:
            cursor.execute("UPDATE setups SET score = %s WHERE setup_id = %s;", (score, setupID))
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

    




