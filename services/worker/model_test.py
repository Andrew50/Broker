



from sync_Data import Data
import datetime
data = Data()
st = 'd_EP'
sample = data.get_setup_sample(1,st)[0]
raw_data = []
start = datetime.datetime.now()
for ticker, dt, classification in sample:
    raw_data.append([data.get_df('raw',ticker, dt), classification])
print(datetime.datetime.now()-start)
