
import random
import pandas as pd
from Create import Create as create
import time
import numpy as np
import sys, os
from tensorflow.keras.models import load_model
import mplfinance as mpf
from Data7 import Data as data
from matplotlib import pyplot as plt
import datetime

class modelTest:
	def runRandomTicker(setuptype,thresh):
		print('testing with random')


		
		while True:
			arglist = []
			for _ in range(100):
				arglist.append([setuptype,thresh])

			data.pool(modelTest.testRandom,arglist)

	def testRandom(bar):
		setuptype = bar[0]
		thresh = bar[1]
		time = datetime.datetime.now()

		
		model = load_model('C:/Screener/sync/models/model_' + setuptype)
	   
		tickers = pd.read_feather(r"C:\Screener\sync\full_ticker_list.feather")['Ticker'].to_list()
		while True:
			try:
				ticker = tickers[random.randint(0,len(tickers)-1)]

				tickerdf = data.get(ticker)
				if(len(tickerdf) > 10):
					date_list = tickerdf.index.to_list()
					date = date_list[random.randint(0,len(date_list) - 1)]
					if(tickerdf.iloc[data.findex(tickerdf, date)]['volume'] > 250000):
						df = create.test_data(ticker, date, setuptype)
						
					   
						sys.stdout = open(os.devnull, 'w')
						god = model.predict(df)
						
						val = 0
						if god[0][1] > thresh:
							val = 1
						sys.stdout = sys.__stdout__
				
				
			   
						if val == 1:
						   
							df1 = data.get(ticker)


							ind= data.findex(df1,date)

							left = ind - 50
							if left < 0:
								left = 0
							df1 = df1[left:ind + 2]
							

				   
							mc = mpf.make_marketcolors(up='g',down='r')
							s  = mpf.make_mpf_style(marketcolors=mc)
							print(god[0][1])
							mpf.plot(df1, type='candle', volume=True  , 
							title = str(god[0][1]),
							style=s, warn_too_much_data=100000,returnfig = True, panel_ratios = (5,1), 
							tight_layout = True,
							vlines=dict(vlines = [date])
							#colors = colorlist, alpha = .2,linewidths=1),
								)      
							plt.show()

				   
			except:
			#(ValueError, FileNotFoundError, TimeoutError, TypeError):
				pass




	def runTestData(setuptype,tickers, dates):

		model = load_model('C:/Screener/sync/models/model_'+ setuptype)
		#setups = pd.read_feather('C:/Screener/setups/database/Testdata_' + setuptype + '.feather')
	   
		right = 0
		total = 0

		ii = 0

		while True:
			ticker = tickers[ii]
			date = dates[ii]
			try:
			
				df = create.test_data(ticker,date, setuptype)
			
				sys.stdout = open(os.devnull, 'w')
				god = model.predict(df)
				
				sys.stdout = sys.__stdout__
				god = god[0][1] * 100
				if True:
					df1 = data.get(ticker,date = date)

					
					ind= data.findex(df1,date) 
					left = ind - 100
					if left < 0:
						left = 0
					df1 = df1[left:ind + 1]
					#print(df1)
					mc = mpf.make_marketcolors(up='g',down='r')
					s  = mpf.make_mpf_style(marketcolors=mc)
			
					mpf.plot(df1, type='candle', volume=True  , 
					title = str(god),
					style=s, warn_too_much_data=100000,returnfig = True, panel_ratios = (5,1), 
					tight_layout = True
					 #  vlines=dict(vlines=[date])
					#colors = colorlist, alpha = .2,linewidths=1),
					)
				
		
					plt.show()



			except TimeoutError:#(TypeError, ValueError, IndexError):
				pass


			ii += 1
	def combine(new,setuptype): 
	


			#setups = ['EP', 'NEP' , 'P','NP' , 'MR', 'PS' , 'F' , 'NF']

		setups = create.get_setups_list()


			
		for setup in setups:
			try:
				df1 = pd.read_feather(f"C:/Screener/sync/database/ben_{setup}.feather")
				df1['sindex'] = df1.index
				df1['source'] = 'ben_'

			except:
				df1 = pd.DataFrame()
			try:
				df2 = pd.read_feather(f"C:/Screener/sync/database/aj_{setup}.feather")
				df2['sindex'] = df2.index
				df2['source'] = 'aj_'
			except:
				df2 = pd.DataFrame()
			try:

				df4 = pd.read_feather(f"C:/Screener/sync/database/laptop_{setup}.feather")
				df4['sindex'] = df4.index
				df4['source'] = 'laptop_'
			except:
				df4 = pd.DataFrame()

				

			df3 = pd.concat([df1, df2, df4]).reset_index(drop = True)
			try:
				df3.to_feather(f"C:/Screener/setups/database/{setup}.feather")
			except:
				print(setup + ' failed')
				#print(df3)
		#else:
		#	df = pd.read_feather(r"C:/Screener/sync/allsetups.feather").sample(frac = .2)

		#	new_df = df.drop(axis=1, labels=["Z", "timeframe", "annotation"])
		#	for i in range(len(df)):
		#		new_df.at[i, 'ticker'] = df.iloc[i]['Ticker']
		#		new_df.at[i, 'date'] = df.iloc[i]['Date']
		#		if(df.iloc[i]['Setup'] == setuptype):
		#			new_df.at[i, 'setup'] = 1
		#		else:
		#			new_df.at[i, 'setup'] = 0
		#	new_df = new_df.drop(axis=1, labels=['Ticker', 'Date', 'Setup']).reset_index(drop = True)
			
		

		#	new_df.to_feather('C:/Screener/setups/database/' + setuptype + '.feather')

		




if __name__ == "__main__":


	setup = 'd_F'
	#modelTest.combine(True,True)
	if False:
		setuptype = setup

		epochs = 200
		new = True
		prcnt_setup = .1


		modelTest.combine(new,setuptype)

		create.run(setuptype,prcnt_setup,epochs,False)
	
	if False:
		s = setup
		modelTest.runRandomTicker(s,.25)

	if True:
		if setup == 'EP':


			tickers = ['IOT','SMCI','ONON'   ,'SE','DUOL','FSLR','XPEV','SHLS','CELH','CALX','qqq','qqq','qqq','qqq','qqq',
				   'mgni','aehr','nflx','coin'        ]
			dates = ['2023-06-02','2023-05-03','2023-03-21','2023-03-07','2023-03-01','2023-03-01','2022-11-30','2022-11-15','2022-11-10','2022-10-25','2023-03-29','2022-11-10','2022-09-13','2022-08-10','2022-07-27',
				 '2022-11-10','2023-01-06','2023-01-20']     
		

		elif setup == 'NEP':
			pass
		elif setup =='P':
			dates = ['2023-07-06','2023-06-14','2023-05-25','2023-04-26']
			tickers = ['geni','next','mod','msft']



			#dates = ['2021-05-20','2023-03-29','2022-11-10','2022-08-10','2022-07-27',
			#			 '2022-11-10','2023-01-06','2023-01-20','2023-01-09']

			#tickers = ['coin','qqq','qqq','qqq','qqq',
			#			   'mgni','aehr','nflx','coin']



		elif setup == 'NP':

			dates = ['2023-06-20','2023-03-01','2023-06-06','2023-02-16','2023-06-07','2023-07-19']
			tickers = ['ffie','rivn','nvcr','shop','base','tost']

		elif setup == 'NF':
			dates = ['2022-12-02','2023-05-24']
			tickers = ['open','pton',]
		elif setup == 'd_F':
			dates = ['2023-07-24','2023-07-24','2023-03-31','2023-03-10','2023-03-30','2020-08-13','2020-11-10','2023-01-05']
			#dates = ['2023-03-02','2023-01-26','2023-07-12','2023-06-28','2023-07-20','2023-07-12','2023-07-13','2023-04-17','2023-07-12','2023-04-03','2023-03-09','2023-03-29','2023-06-13']
			#,'2020-08-13','2020-11-10','2023-01-05',
			#		 '2023-01-04','2023-02-16','2023-03-22','2023-01-04','2023-01-04',
			#		 '2022-01-05','2022-10-18','2023-01-03','2022-12-09','2022-09-06',
			#		 '2023-03-31','2022-04-11','2022-04-11','2022-08-04','2022-09-22',
			#		 '2023-08-03']

			tickers = ['RIVN','XPEV' ,'dpst','riot','meli','tsla','tsla','elf']
			#tickers = ['gotu','iq','fngu','alto','xp','mod','nkla','cbay','nvda','dpst','riot','meli','ai']
			  #,'tsla','tsla','elf',
					#   'mlco','mlco','aehr','cweb','tme',
					#   'nue','kold','orcl','amat','enph',
					#   'mdb','pump','oxy','mrna','celh',
					#   'rytm']

		modelTest.runTestData(setup,tickers,dates)
	
	## EP 
	#thresh = .6

	

	#modelTest.runRandomTicker(setuptype,thresh)
   








