import json
import tensorflow as tf
import numpy as np
from sync_Data import data
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.firefox.options import Options 
from selenium.webdriver.firefox.service import Service
import pathlib, time, selenium, datetime, os, math, tensorflow
import pandas as pd


import yfinance as yf
import datetime
import multiprocessing


class Screener:

	def fetch_stock_data(tickers):
		args = " ".join(tickers)
		ds = yf.download(args, interval = '1m',period = '1d',prepost = True, auto_adjust = True,threads = True)
		print(ds)
		time.sleep(50)

	def get_pm_prices():
		from sync_Data import data
	
		tickers = data.get_ticker_list()[:8000]
		batches = []
		for i in range(0,len(tickers),100):
			batches.append(tickers[i:i+ 100])
		
		with multiprocessing.Pool(8) as pool:
			results = pool.map(Screener.fetch_stock_data,batches)
	
		return results
		#for data in results:
		#	print(data)

	
	
	def load_model(user_id,st):
		return tf.keras.models.load_model(f'{user_id}_{st}')

	def screen(user_id,setup_types, _format, query = None,threshold = .65, model = None):
		results = []
		
		if _format == 'screener':
			
			for st in setup_types:
				tf, setup_length = data.get_setup_info(user_id,st)
				ds, ticker_list = data.get_ds('screener','full',tf,setup_length)
				model = Screener.load_model(user_id,st)
				ds = ds[:,:,1:]
				scores = model.predict(ds)[:,0]
				i = 0
				for score in scores:
					if score > threshold:
						ticker = ticker_list[i]
						results.append([ticker,int(100*score)])
					i += 1
			
			results.sort(key=lambda x: x[1],reverse=True)
			return results
		
		elif _format == 'trainer':
			st = setup_types
			tf, setup_length = data.get_setup_info(user_id,st)
			ds, ticker_list = data.get_ds('screener',query,tf,setup_length)
			dt_list = ds[:,-1,0]
			ds = ds[:,:,1:]
			scores = model.predict(ds)[:,0]
			i = 0
			for score in scores:
				if score > threshold and score < 1 - threshold:
					ticker = ticker_list[i]
					results.append([ticker,tf,dt_list[i]])
				i += 1
			
			return results
		
		elif _format == 'study':
			query = [[query,None]]
			st = setup_types
			#for st in setup_types:
			tf, setup_length = data.get_setup_info(user_id,st)
			ds, ticker_list = data.get_ds('screener',query,tf,None)
				
			model = Screener.load_model(user_id,st)
			dt_list = ds[:,:,0]
			ds = ds[:,:,1:]
			scores = model.predict(ds)[:,0]
			i = 0
			for score in scores:
				if score > threshold:
					dt = dt_list[i]
					results.append([dt,int(100*score)])
				i += 1
			
			return results
		
	
	
def get(args,user_id):
	setup_types = args

	results = Screener.screen(user_id,setup_types,'screener')
	return json.dumps(results)
			
if __name__ == '__main__':
	print(Screener.get_pm_prices())
