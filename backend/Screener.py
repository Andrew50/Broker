





import pandas as pd
import mplfinance as mpf
import PySimpleGUI as sg
import datetime
import matplotlib.ticker as mticker
from matplotlib import pyplot as plt
from multiprocessing.pool import Pool
import os, pathlib, shutil, math, PIL, io
from Data import Database, Dataset








class Screener:
	

	def score(ds):
		




		if model == None:
			model = Main.load_model(st)
		returns = []
		for df, index in self.np:
			score = model.predict(df)
			returns.append([self.ticker, self.df.index[index], st, score])
		self.score = returns
		return returns
		

	#def get(dt = None, ticker = None, tf = 'd',browser = None, fpath = None):
	def get(user_id,tf = '1d',dt = None):
		db = Database()
		ds = Dataset(db, dt = db.format_date(dt))
		table = 
		st = main.get_config('Screener active_setup_list').split(',')
		setups = main.score_dataset(df,st)
		
		for ticker, dt, st, score in setups:
			

