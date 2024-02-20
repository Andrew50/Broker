from vmdpy import VMD
import tqdm
#from PyEMD import CEEMDAN
import numpy as np
from scipy.signal import savgol_filter
from train import train
import datetime
import mysql.connector
from tensorflow.keras.callbacks import EarlyStopping
import mysql.connector
import pandas as pd
import tensorflow as tf
import vmdpy
import scipy
import os
import traceback
from sync_Data import Data
import time
import random

#setup_types = 'd_EP', 'd_NEP', 'd_P', 'd_NP', 'd_F', 'd_NF', 'd_MR'
setup_types = 'd_P',
sampling_ratios = 0.05, .1, .2, .3, .4
feature_methods = 'close', 'ohlc', 'ohlcv', 'rsi_c', 'rsi_ohlc'
preprocessing_methods = 'rolling_change', 'none', 'savitzky-golay', 'min_max','st_rolling_change', 'log_dif' #,'CEEMDAN', 'VMD', 

lengths = 3, 10, 25, 50, 80, 120
model_types = 'lstm', 'bilstm', 'gru' #,'gcn', 'dkf', 'transformer'

def process(bar):
    parameters = None
    try:
        raw_data, parameters = bar
        st, sr, fm, pm, l, mt = parameters
        print(f"Processing {' '.join([str(x) for x in parameters])}------------------------------------------------------------------")
        raw_x, y = raw_data[st]
        tx, ty, vx, vy = sample(sr,raw_x,y)
        tx, vx = features(fm,tx), features(fm,vx)
        tx, vx = preprocess(pm,tx), preprocess(pm,vx)
        tx, vx = length(l,tx), length(l,vx)
        tuner = train(mt,tx,ty,vx,vy,parameters)
        log(parameters,tuner)
        #save(tuner)
    except Exception as e:

        #exception = traceback.format_exc()
        #print(f'Error processing {parameters} {e} {exception}')
        error_message = f"Error processing {parameters}: {str(e)}"
        # Optionally, include traceback information
        error_message += "\n" + traceback.format_exc()
        log_file_name = f"error_log_{os.getpid()}.txt"
        with open(log_file_name, "a") as file:
            file.write(error_message + "\n\n")

def get_user(email, password):
    if os.environ.get('INSIDE_CONTAINER', False): #inside container
        mysql_host = 'mysql'
    else:
        mysql_host = 'localhost'
    mysql_conn = mysql.connector.connect(host=mysql_host,port='3306',user='root',password='7+WCy76_2$%g',database='broker')
    with mysql_conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        if user_data and len(user_data) > 0:
            if password == user_data[2]:  # Assuming password is at index 2
                return user_data[0]  

def sample(sr,raw_x,y):
    yes = [[x,y] for x,y in zip(raw_x,y) if y == 1]
    no = [[x,y] for x,y in zip(raw_x,y) if y == 0]
    num_yes_training = len(yes)
    num_no_training = int((num_yes_training / sr) - num_yes_training)
    training_instances = yes + random.sample(no, num_no_training)
    training_x, training_y = zip(*training_instances)
    print(f"Training set size: {len(training_y)}, Class balance: {np.mean(training_y)}")
    print(f"Validation set size: {len(y)}, Class balance: {np.mean(y)}")
    return training_x, np.array(training_y), raw_x, np.array(y)

def features(fm,xs):
    features = []
    for x in xs:
        def rsi(data):
            period = 14
            delta = np.diff(data)
            gain = np.where(delta > 0, delta, 0)
            loss = np.where(delta < 0, -delta, 0)
            avg_gain = np.zeros(len(data))
            avg_loss = np.zeros(len(data))
            avg_gain[period] = gain[:period].mean()
            avg_loss[period] = loss[:period].mean()
            for i in range(period + 1, len(data)):
                avg_gain[i] = (avg_gain[i - 1] * (period - 1) + gain[i - 1]) / period
                avg_loss[i] = (avg_loss[i - 1] * (period - 1) + loss[i - 1]) / period
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi[avg_loss == 0] = 100
            rsi[:period] = np.nan
            return rsi

        def get():
            if fm == "close":
                return x[:,4].reshape(-1,1)
            #return np.array(x[:,4])
            elif fm == "ohlc":
                return x[:,1:5]
            elif fm == "ohlcv":
                return x[:,1:]
            elif fm == "rsi_c":
                return np.hstack((x[:,4],rsi(x[:,4]))).reshape(-1,1)
            elif fm == "rsi_ohlc":
                return np.hstack((x[:,1:5],rsi(x[:,4]).reshape(-1,1)))

        features.append(get())
    
    return features

def preprocess(pm,features):
    returns = []
    def calc(features):
        if pm == 'rolling_change':
            return features[1:,:] / features[:-1,:] - 1
        elif pm == 'none':
            return features
        elif pm == 'savitzky-golay':
            return savgol_filter(features,window_length = 10, polyorder = 2, axis = 0)
        elif pm == 'min_max':
            min = features.min(axis=1).reshape(-1,1)
            max = features.max(axis=1).reshape(-1,1)
            return (features - min) / (max - min)
        elif pm == 'CEEMDAN':
            ceemdan = CEEMDAN()
            for i in range(features.shape[1]):
                signal = features[:, i]
                imfs = ceemdan(signal)
                imfs_list.append(imfs)
            return imfs_list
        elif pm == 'VMD':
            alpha = 2000       # Moderate bandwidth constraint
            tau = 0            # Noise-tolerance (no strict fidelity enforcement)
            K = 4              # 4 modes
            DC = 0             # No DC component pv
            init = 1           # Initialize omegas uniformly
            tol = 1e-7         # Tolerance for convergence
            modes = np.zeros(data.shape + (K,))  # Adding an extra dimension for modes
            for i in range(data.shape[1]):  # Assuming columns are signals
                signal = data[:, i]
                u, _, _ = VMD(signal, alpha, tau, K, DC, init, tol)
                modes[:, i, :] = u.T  # Transpose to match the placeholder's shape
            return modes
        elif pm == 'st_rolling_change':
            rolling_changes = features[1:,:] / features[:-1,:] - 1
            mean = np.mean(rolling_changes)
            stdev = np.std(rolling_changes)
            return (rolling_changes - mean) / stdev
        elif pm == 'log_dif':
            return np.log(features[1:]) - np.log(features[:-1])

    for f in features:
        returns.append(calc(f))
    return returns

def length(l,preprocess):
    returns = []
    for p in preprocess:
        p = p[-l:,:]
        if p.shape[0] < l:
            p = np.vstack((np.zeros((l - p.shape[0],p.shape[1])),p))
        returns.append(p)
    return np.array(returns)


def log(parameters_values,tuner):
    parameter_columns = ['setup type','training ratio','features','preprocessing','length','model type']
#     best_hps = tuner.get_best_hyperparameters(num_trials=20)
#     records = []
#     for hps in best_hps:
#         trial = tuner.oracle.get_trial(hps.trial_id)
#         auc_val_pr = trial.score
    top_trials = tuner.oracle.get_best_trials(num_trials=20)
    
    records = []
    for trial in top_trials:
        # Access the trial's hyperparameters and score
        hps = trial.hyperparameters
        auc_val_pr = trial.score
        record = {'val_auc_pr': auc_val_pr}
        record.update(dict(zip(parameter_columns, parameters_values)))
        for k in hps.values:
            record[k] = hps.get(k)
        records.append(record)
    df = pd.DataFrame(records)
    all_columns_ordered = ['val_auc_pr'] + parameter_columns + [col for col in df.columns if col not in parameter_columns]
    csv_file_path = f'tuner_results/{os.getpid()}.csv'
    
    # Check if the CSV file exists and read it if it does
    if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
        existing_df = pd.read_csv(csv_file_path)
        # Get a union of all columns from both existing and new data, maintaining the order of parameter columns
        combined_columns_ordered = parameter_columns + list(set(existing_df.columns.union(df.columns)) - set(parameter_columns))
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df = combined_df.reindex(columns=combined_columns_ordered)
    else:
        combined_df = df.reindex(columns=all_columns_ordered)
    
    # Write the combined DataFrame to the CSV, ensuring the fixed parameter columns are always on the left
    combined_df.to_csv(csv_file_path, index=False)



#     if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
#         existing_df = pd.read_csv(csv_file_path)
#         combined_df = pd.concat([existing_df, df], ignore_index=True).reindex(columns=(existing_df.columns.union(df.columns)))
#     else:
#         combined_df = df
#     combined_df.to_csv(csv_file_path, index=False)

#     if os.path.exists(csv_file_path):
#         existing_df = pd.read_csv(csv_file_path)
#         combined_columns = sorted(set(existing_df.columns) | set(df.columns))
#         existing_df = existing_df.reindex(columns=combined_columns)
#         df = df.reindex(columns=combined_columns)
#         df.to_csv(csv_file_path, mode='a', header=False, index=False)
#     else:
#         df.to_csv(csv_file_path, mode='w', header=True, index=False)
# 
# 
# 
# 
# 
#     best_hps = tuner.get_best_hyperparameters(num_trials=20)
#     records = []
#     for hps in best_hps:
#         record = {}
#         for p in parameters:
#             record[p] = p
#         for k in hps.values:
#             record[k] = hps.get(k)
#         records.append(record)
#     df = pd.DataFrame(records, columns=['setup type','training ratio','features','preprocessing','length','model type'] + records[0].keys())
#     df.to_csv(f'tuning_results{os.getpid()}.csv', mode='a', header=False, index=False)

def save(tuner,parameters):
    best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
    model = tuner.hypermodel.build(best_hps)
    early_stopping = EarlyStopping(
            monitor='auc_pr',  # Use the metric name here
            patience=15,
            restore_best_weights=True
            )
    model.fit(
            ds, y, 
            epochs=epochs, 
            batch_size=best_hps.get('batch_size'),  # Use the tuned batch size
            validation_split=0.2, 
            callbacks=[early_stopping],
            class_weight=class_weights_dict
            )
    mode.save(parameters.join('-'), save_format = 'tf')

def get_args(raw_data): 
    for st in setup_types:
        for sm in sampling_ratios:
            for fm in feature_methods:
                for pm in preprocessing_methods:
                    for l in lengths:
                        for mt in model_types:
                            yield [raw_data,[st,sm,fm,pm,l,mt]]

if __name__ == '__main__':
    from sync_Data import Data
    import multiprocessing
    data = Data()
    start = datetime.datetime.now()
    if not os.path.exists('tuner_results'):
        os.makedirs('tuner_results')
    if not os.path.exists('tuner'):
        os.makedirs('tuner')
    raw_data = {}
    for st in setup_types:
        print(f'Loading raw data for {st}')
        raw_data[st] = [[],[]]
        values,tf,setup_length  = data.get_setup_sample(1,st)
        yes = [x for x in values if x[2] == 1][:20]
        values = yes + [x for x in values if x[2] == 0][:int((len(yes) / min(sampling_ratios))*1.02)]
        for ticker, dt, classification in tqdm.tqdm(values):
            try:
                raw_data[st][0].append(data.get_df('raw',ticker,tf,dt,bars=max(lengths)) )
                raw_data[st][1].append(classification)
            except Exception as e:
                print(f'Error loading data for {ticker} {dt} {e}')
#         raw_data[st] = [[data.get_df('raw',ticker,tf,dt), classification] for ticker, dt, classification in values]
#                         #dt, open, high, low, close, volume
    print(f'raw data loaded in {datetime.datetime.now() - start}')
    #args = get_args(raw_data)
    #total = len(list(args))
    cores = multiprocessing.cpu_count()
    print(f'Using {cores} cores')
    with  multiprocessing.Pool(cores) as pool:
        #    list(tqdm.tqdm(pool.imap_unordered(process, args), total=total))
        pool.imap_unordered(process, get_args(raw_data))
        pool.close()
        pool.join()
