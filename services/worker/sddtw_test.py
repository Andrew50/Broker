
import numpy as np
from scipy.signal import savgol_filter
from sync_Data import Data
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import pytz

BARS, SMOOTHING_WINDOW, POLY_ORDER = 25, 23, 3
#BARS, SMOOTHING_WINDOW, POLY_ORDER = 15, 9, 4
TOP_N = 20


class SDDTW:

	def transform(seq,bars=BARS, smoothing_window=SMOOTHING_WINDOW, poly_order=POLY_ORDER):
		seq =  savgol_filter(seq, smoothing_window, poly_order, deriv=1,delta=2)

		# mean = np.mean(seq)
		# std = np.std(seq)
		# seq = (seq - mean) / std
##
		
		##
		# mean = np.mean(seq)
		# std = np.std(seq)
		# seq = (seq - mean) / std
		#seq =  savgol_filter(seq, SMOOTHING_WINDOW,POLY_ORDER)
		#seq = Keogh EJ, Pazzani MJ (2001) Derivative dynamic time warping. Paper presented at the SIAM International Conference on Data Mining
		return seq

	def path(D,m=-1):
		N, _ = D.shape
		n = N - 1
		if m < 0: m = D[N - 1, :].argmin()
		P = [(n, m)]
		while n > 0:
			if m == 0: cell = (n - 1, 0)
			else:
				val = min(D[n-1, m-1], D[n-1, m], D[n, m-1])
				if val == D[n-1, m-1]: cell = (n-1, m-1)
				elif val == D[n-1, m]: cell = (n-1, m)
				else: cell = (n, m-1)
			P.append(cell)
			n, m = cell
		P.reverse()
		P = np.array(P)
		return P
			
	def compute_matrix(x,y):
		C = np.zeros((len(x), len(y)))
		for i in range(len(x)):
			for j in range(len(y)):
				C[i, j] = abs(x[i] - y[j])
		N, M = C.shape
		D = np.zeros((N, M))
		D[:, 0] = np.cumsum(C[:, 0])
		D[0, :] = C[0, :]
		for n in range(1, N):
			for m in range(1, M):
				D[n, m] = C[n, m] + min(D[n-1, m], D[n, m-1], D[n-1, m-1])
		return D

	def score_instance(bar):
		ticker,tf,dt,ticker2,dt2,bars,smoothing_window,poly_order = bar
		data = Data()
		x = data.get_df('raw',ticker,tf,dt, bars=bars)
		y = data.get_df('raw',ticker2,tf)
		target_index = SDDTW.findex(y,dt2)
		x = x[:, 4]
		y = y[:, 4]
		x, y = SDDTW.transform(x,bars,smoothing_window,poly_order), SDDTW.transform(y,bars,smoothing_window,poly_order)
		D = SDDTW.compute_matrix(x,y)
		sorted_indices = np.argsort(D[-1, :])
		i = 1
		for idx in sorted_indices:
			P = SDDTW.path(D, m=idx)
			index = P[-1, 1]
			if index == target_index:
				cost = D[-1, idx]
				return i, round(cost,2), bars, smoothing_window, poly_order
			i += 1

	def calc(data,ticker,tf,dt,ticker_2): #y is query, x is to check
		x = data.get_df('raw',ticker,tf,dt, bars=BARS)
		if ticker_2:
			ds = [[ticker_2,data.get_df('raw',ticker_2,tf)]]
		else:
			ds = [[ticker,data.get_df('raw',ticker,tf)] for ticker in ['AAPL','MSFT','AMZN','GOOG','FB','TSLA','JNJ','JPM','V']]
		x = x[:, 4]
		for ticker, full_y in ds:
			y = full_y[:, 4]
			sD = SDDTW.compute_matrix(x,y)
			x, y = SDDTW.transform(x), SDDTW.transform(y)
			D = SDDTW.compute_matrix(x,y)
			D = D * sD
			sorted_indices = np.argsort(D[-1, :])
			top_matches = []
			for idx in sorted_indices:
				if all(abs(idx - index) > BARS//3 for ticker,dt,index,cost in top_matches):
					P = SDDTW.path(D, m=idx)
					index = P[-1, 1]
					cost = D[-1, idx]
					dt = str(SDDTW.format_datetime(dt=full_y[:,0][index], reverse=True))[:10]
					top_matches.append([ticker,dt,index,cost])
					if len(top_matches) == TOP_N:
						break
			return top_matches


	def format_datetime(dt,reverse=False):
		if reverse:
			return datetime.datetime.fromtimestamp(dt)
		if type(dt) == int or type(dt) == float or type(dt) == np.float64 or type(dt) == np.int64:
			return dt
		if dt is None or dt == '': return None
		if dt == 'current': return datetime.datetime.now(pytz.timezone('EST'))
		if isinstance(dt, str):
			try: dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
			except: dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
		time = datetime.time(dt.hour, dt.minute, 0)
		dt = datetime.datetime.combine(dt.date(), time)
		if dt.hour == 0 and dt.minute == 0:
			time = datetime.time(9, 30, 0)
			dt = datetime.datetime.combine(dt.date(), time)
		dt = dt.timestamp()
		return dt
	
	def findex(df, dt):
		dt = Data.format_datetime(dt)
		i = int(len(df)/2)		
		k = int(i/2)
		while k != 0:
			date = df[i,0]
			if date > dt:
				i -= k
			elif date < dt:
				i += k
			k = int(k/2)
		while df[i,0] < dt:
			i += 1
		while df[i,0] > dt:
			i -= 1
		return i


def get (user_id,data,ticker,tf,dt,ticker_2=None):
	return SDDTW.calc(data,ticker,tf,dt,ticker_2)

if __name__ == '__main__':





	data = Data()
	instances = [
	['MRK', '1d', '2022-11-17', 'EGY'],
	['FREY', '1d', '2022-10-04', 'FSLR']
	]


	ticker, tf, dt, ticker_2 = instances[0]
	matches = get(None,data,ticker,tf,dt,ticker_2=ticker_2)
	x = data.get_df('raw',ticker,tf,dt, bars=BARS)
	formated_x = x[:,:5]
	formated_x = pd.DataFrame(formated_x)  # Convert x_cropped to a DataFrame
	formated_x = formated_x.rename(columns={0: 'datetime', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
	formated_x['datetime'] = pd.to_datetime(formated_x['datetime'], unit='s')
	formated_x.set_index('datetime', inplace=True)
	mpf.plot(formated_x, type='candlestick', title=f"{ticker} {dt}")  # Plot 
	for ticker, dt, index,cost in matches:

		y = data.get_df('raw',ticker,tf,dt, bars=BARS)[:,:5]
		formated_y = pd.DataFrame(y)  # Convert y_cropped to a DataFrame
		formated_y = formated_y.rename(columns={0: 'datetime', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
		formated_y['datetime'] = pd.to_datetime(formated_y['datetime'], unit='s')
		formated_y.set_index('datetime', inplace=True)
		mpf.plot(formated_y, type='candlestick', title=f" {dt} {cost}")  # Plot on the new Axes object
	

