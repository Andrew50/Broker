


from Data7 import Data as data
import matplotlib.pyplot as plt
import random
import mplfinance as mpf
import pandas as pd
import PySimpleGUI as sg
from multiprocessing.pool import Pool

from PIL import Image
import time
import sys
import pathlib
import datetime
import io
import matplotlib.ticker as mticker
import shutil
import os
from Detection2 import Detection as detection
from tensorflow.keras.models import load_model

from Create import Create as create
import math


from modelTest import modelTest



class Trainer:


	def log(self):
		if self.event == 'Clear' or self.event == 'cl':
			for i in range(len(self.current_setups)-1,-1,-1):
				if self.current_setups[i][0] == self.index:
					for k in range(2):
						self.window["-GRAPH-"].MoveFigure(self.current_setups[i][2][k],5000,0)

					del self.current_setups[i]
			self.window.refresh()
		else:
			try:
				i = int(self.event)
				setup = self.setup_list[i-1]
			except:
				setup = self.event
			x = self.select_line_x
			y = self.y - 50
			if y < 10:
				y = 110
			text = self.window["-GRAPH-"].draw_text( setup, (x,y) , color='black', font=None, angle=0, text_location='center')
			line = self.window["-GRAPH-"].draw_line((self.select_line_x,0), (self.select_line_x,self.height), color='black', width=1)
			self.current_setups.append([self.index,setup,[line,text]])
			self.y -= 35

	def save(self):
		df1 = self.dict[self.i][2]
		ticker = self.dict[self.i][0]
		ii = 0
		for s in self.setup_list:
			df = pd.DataFrame()
			df['date'] = df1.index
			df['ticker'] = ticker
			df['setup'] = 0
			for bar in self.current_setups:
				if bar[1] == s:
					self.stats_list[ii] += 1
					index = bar[0]
					df.iat[index,2] = 1
					if index <= self.cutoff:
						df2 = pd.DataFrame({
							'date':[df1.index[index]],
							'ticker':[ticker],
							'setup':[1]})
						df = pd.concat([df,df2]).reset_index(drop = True)
			df = df[self.cutoff:]
			add = df[['ticker','date','setup']]



			if not self.use_no:
				add = add[df['setup'] == 1]




			add['req'] = 0
			
			try:
				if(data.isBen()):
					df = pd.read_feather('C:/Screener/sync/database/ben_' + s + '.feather')
				elif data.isLaptop():
					df = pd.read_feather('C:/Screener/sync/database/laptop_' + s + '.feather')
				else:
					df = pd.read_feather('C:/Screener/sync/database/aj_' + s + '.feather')
			except:
				df = pd.DataFrame()
			df = pd.concat([df,add]).reset_index(drop = True)
			if(data.isBen()):
				df.to_feather('C:/Screener/sync/database/ben_' + s + '.feather')
			elif data.isLaptop():
				df.to_feather('C:/Screener/sync/database/laptop_' + s + '.feather')
			else:
				df.to_feather('C:/Screener/sync/database/aj_' + s + '.feather')
			ii += 1
	

	def tune(self,val):
		s = self.current_setup
		ticker = self.setup_string.split('+')[1]
		date = pd.to_datetime(self.setup_string.split('+')[2])
		if val == 1:
			req = 0
		else:
			req = 1
		add = pd.DataFrame({
			'ticker':[ticker],
			'date':[date],
			'setup':[val],
			'req':[req]
		})
		try:
			if(data.isBen()):
				df = pd.read_feather('C:/Screener/sync/database/ben_' + s + '.feather')
			elif data.isLaptop():
				df = pd.read_feather('C:/Screener/sync/database/laptop_' + s + '.feather')
			else:
				df = pd.read_feather('C:/Screener/sync/database/aj_' + s + '.feather')
		except:
			df = pd.DataFrame()

		df = pd.concat([df,add]).reset_index(drop = True)
		
		
		if(data.isBen()):
			df.to_feather('C:/Screener/sync/database/ben_' + s + '.feather')
		elif data.isLaptop():
			df.to_feather('C:/Screener/sync/database/laptop_' + s + '.feather')
		else:
			df.to_feather('C:/Screener/sync/database/aj_' + s + '.feather')
		
	def click(self,clicked = True):

		df = self.dict[self.i][2]
		ticker = self.dict[self.i][0]
		chart_size = self.x_size - 20
		if clicked:
			x = self.values['-GRAPH-'][0]
			self.y = self.values['-GRAPH-'][1]
			chart_click = x - 10
			percent = chart_click/chart_size
			self.index = math.floor(len(df) * percent)
			if self.index <= -1:
				self.index = 0
			if self.index >= len(df):
				self.index = len(df) - 1
			try:
				self.date = df.index[self.index]
			except:
				return
		else:
			if self.event == 'right' and self.index < len(df) - 1:
				self.index += 1
			elif self.event == 'left' and self.index > 0:
				self.index -= 1
			self.y = self.height - 80
		round_x = int((self.index + 1)/(len(df)) * (self.x_size - 20)) + 10 - int((chart_size/len(df))/2)
		self.window["-GRAPH-"].MoveFigure(self.select_line,round_x - self.select_line_x,0)
		self.select_line_x = round_x

	def update(self):
		if self.init:

			modelTest.combine(True,'')
			self.full_setup_list = create.get_setups_list()

			if self.menu == 0:
				self.stats_list = []
				self.setup_list = []
				for s in self.full_setup_list:
					if self.current_tf in s:
						self.setup_list.append(s)
				for setup in self.setup_list:
					
					try:
						df = pd.read_feather("C:/Screener/setups/database/" + setup + ".feather")
						df = df[df['setup'] == 1]
					except:
						df = pd.DataFrame()
					self.stats_list.append(len(df))
				graph = sg.Graph(
				canvas_size=(self.width, self.height),
				graph_bottom_left=(0, 0),
				graph_top_right=(self.width, self.height),
				key="-GRAPH-",
				change_submits=True,  # mouse click events
				background_color='grey',
				drag_submits=False)
				layout = [
				[graph],
				[sg.Text(key = '-stats-')],
				[sg.Button('Next'), sg.Button('Clear'), sg.Button('Skip'), sg.Button('Toggle'),sg.Text('use no ' + str(self.use_no), key = '-use_no-'), sg.Button('d'), sg.Button('w'), sg.Button('h'), sg.Button('1min') , sg.Text(self.current_tf)],
				[sg.Button('Trainer'), sg.Button('Validator'), sg.Button('Tuner'), sg.Button('Manual')]
				]
				self.window = sg.Window('Trainer', layout,margins = (10,10),scaling=self.scale,finalize = True)
				self.window.bind("<q>", "1")
				self.window.bind("<w>", "2")
				self.window.bind("<e>", "3")
				self.window.bind("<a>", "4")
				self.window.bind("<s>", "5")
				self.window.bind("<d>", "6")
				self.window.bind("<z>", "7")
				self.window.bind("<x>", "8")
				self.window.bind("<c>", "9")
				self.window.bind("<p>", "right")
				self.window.bind("<i>", "left")
				self.window.bind("<o>", "cl")
				self.window.bind("<Button-3>", "cl")
			elif self.menu == 1:
				self.setup_list = self.full_setup_list
				layout = [
				[sg.Image(key = '-CHART-')],
				[sg.Button(s) for s in self.setup_list],
				[sg.Button('Prev'),sg.Button('Remove'), sg.Button('Next'), sg.Text(self.current_setup, key = '-text-'), sg.Text(key = '-counter-')],
				[sg.Button('Trainer'), sg.Button('Validator'), sg.Button('Tuner'), sg.Button('Manual')]
				]
				self.window = sg.Window('Validator', layout,margins = (10,10),scaling=self.scale,finalize = True)
				self.window.bind("<p>", "Next")
				self.window.bind("<i>", "Prev")
				self.window.bind("<o>", 'Remove')
			
			elif self.menu == 2:
				self.setup_list = self.full_setup_list
				layout = [
				[sg.Image(key = '-CHART-')],
				[sg.Button(s) for s in self.setup_list],
				[sg.Button('No'),sg.Button('Skip'),sg.Button('Yes'), sg.Text(self.current_setup, key = '-text-'), sg.Text(key = '-counter-')],
				[sg.Button('Trainer'), sg.Button('Validator'), sg.Button('Tuner'), sg.Button('Manual')]
				]
				self.window = sg.Window('Tuner', layout,margins = (10,10),scaling=self.scale,finalize = True)
				self.window.bind("<p>", "Yes")
				self.window.bind("<i>", "No")
				self.window.bind("<o>", "Skip")
			elif self.menu == 3:
				self.setup_list = self.full_setup_list
				layout = [
					[sg.Text('Ticker'),sg.InputText(key = '-input_ticker-')],
					[sg.Text('Date'),sg.InputText(key = '-input_date-')],
					[sg.Text('Setup'),sg.InputText(key = '-input_setup-')],
					[sg.Text('Timeframe'),sg.InputText(key = '-input_timeframe-')],
					[sg.Button('Enter')],
					[sg.Button('Trainer'), sg.Button('Validator'), sg.Button('Tuner'), sg.Button('Manual')]
					]
				self.window = sg.Window('Manual', layout,margins = (10,10),scaling=self.scale,finalize = True)

			self.init = False
			self.window.maximize()
		done = False
		
		if self.menu == 2:
			path = "C:/Screener/setups//charts/"
			keyword = f'_{self.i}_'
			wait = False
			while True:
				try:
					dir_list = os.listdir(path)
					for d in dir_list:
						if keyword in d:
							try:
								if wait:
									time.sleep(2)
								gush = path + d
								image1 = Image.open(gush)
								bio1 = io.BytesIO()
								image1.save(bio1, format="PNG")
								self.setup_string = d
								done = True
								break
							except:
								pass
					wait = True
					if done:
						break
					
				except TimeoutError:
					pass
		elif self.menu == 1 or self.menu == 0:
			while True:
				try:
					image1 = Image.open(r'C:/Screener/setups/charts/' + str(self.i) + '.png')
					bio1 = io.BytesIO()
					image1.save(bio1, format="PNG")
					break
				except:
					pass
		
		if self.menu == 0:
			self.x_size = image1.size[0]
			self.window['-GRAPH-'].erase()
			self.window["-GRAPH-"].draw_image(data=bio1.getvalue(), location=(0, self.height))
			self.select_line_x = -100
			self.select_line = self.window["-GRAPH-"].draw_line((self.select_line_x,0), (self.select_line_x,self.height), color='green', width=1)
			df = self.dict[self.i][2]
			chart_size = self.x_size - 20
			round_x = int((self.cutoff)/(len(df)) * (chart_size)) + 10 - int((chart_size/len(df))/2)
			self.window["-GRAPH-"].draw_line((round_x,0), (round_x,self.height), color='red', width=2)
			self.current_setups = []
			stat_string = ''
			for i  in range(len(self.setup_list)):
				setup = self.setup_list[i]
				num = self.stats_list[i]
				stat_string += f'  {num} {setup.split("_")[1]}  |'
			stat_string = stat_string[:-1]
			self.window['-stats-'].update(stat_string)
		elif self.menu == 1 or self.menu == 2:
			if self.menu == 1:
				string = f'{self.i + 1} of {len(self.setups_df)}'
			else:
				string = ''
			self.window['-counter-'].update(string)
			self.window["-CHART-"].update(data=bio1.getvalue())


	def manual_log(self):
		try:
			ticker = self.values['-input_ticker-']
			date = self.values['-input_date-']
			tf = self.values['-input_timeframe-']
			try:
				date = datetime.datetime.strptime(date, '%Y-%m-%d')
			except:
				date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
			setup = tf + '_' + self.values['-input_setup-']

			try:
				if(data.isBen()):
					df = pd.read_feather('C:/Screener/sync/database/ben_' + setup + '.feather')
				elif data.isLaptop():
					df = pd.read_feather('C:/Screener/sync/database/laptop_' + setup + '.feather')
				else:
					df = pd.read_feather('C:/Screener/sync/database/aj_' + setup + '.feather')

				
			except:
				df = pd.DataFrame()
				

			
			df2 = pd.DataFrame({
			'ticker':[ticker],
			'date':[date],
			'setup':[1],
			'req':[0]})
			df = pd.concat([df,df2]).reset_index(drop = True)
				

			
			if(data.isBen()):
				df.to_feather('C:/Screener/sync/database/ben_' + setup + '.feather')
			elif data.isLaptop():
				df.to_feather('C:/Screener/sync/database/laptop_' + setup + '.feather')
			else:
				df.to_feather('C:/Screener/sync/database/aj_' + setup + '.feather')

		
		except TimeoutError as e:
			sg.Popup(e)
	def loop(self):

		if os.path.exists("C:/Screener/ben.txt"):
			self.height = 850
			self.width = 2000
		elif os.path.exists("C:/Screener/laptop.txt"):
			self.height = 2050
			self.width = 3900
		else:
			self.height = 1150
			self.width = 2500
		self.cutoff = 75
		self.size = 300

		self.use_no = True
		with Pool(6) as self.pool:
			if os.path.exists("C:/Screener/setups/charts"):
				shutil.rmtree("C:/Screener/setups/charts")
			os.mkdir("C:/Screener/setups/charts")
			sg.theme('DarkGrey')
			#self.setup_list = ['EP', 'NEP' , 'P','NP' , 'MR' ,'PS', 'F' , 'NF']
			self.full_setup_list = create.get_setups_list()
			self.setup_list = self.full_setup_list
			self.scale = 4
			self.setup = []
			self.i = 0
			self.menu = 3
			self.current_setup = self.setup_list[0]
			self.current_tf = 'd'


			self.init = True
			self.dict = []
			self.tickers = pd.read_feather(r"C:\Screener\sync\full_ticker_list.feather")['Ticker'].to_list()
			self.index = -1
		
			self.preload(self)
			self.update(self)
			while True:
				self.event, self.values = self.window.read()
				if self.event == 'Next':
					if self.menu == 0:
						self.save(self)
						self.current_setups = []
						self.i += 1
						self.update(self)
						self.preload(self)
						self.index = 0
					else:
						if self.i + 1 < len(self.setups_df):
							self.i += 1
							self.update(self)
							self.preload(self)


				elif self.event == '1min' or self.event == 'h' or self.event == 'd' or self.event == 'w':
					self.current_tf = self.event
					self.window.close()
					self.init = True
					self.i = 0
					while True:

						try:
							if os.path.exists("C:/Screener/setups/charts"):
								shutil.rmtree("C:/Screener/setups/charts")
							os.mkdir("C:/Screener/setups/charts")
							break
						except:
							pass
					self.preload(self)

					self.update(self)


				elif self.event == 'Remove':
					i = self.setups_df.iloc[self.i]['sindex']
					setup = self.current_setup
					source = self.setups_df.iloc[self.i]['source']
					df = pd.read_feather('C:/Screener/sync/database/' + source + setup + '.feather')
					if self.menu == 1:
						df.iat[i,2] = 0
					elif self.menu == 2:
						df.iat[i,2] = 1
					df.to_feather('C:/Screener/sync/database/' + source + setup + '.feather')
					print(f'removed {df.iloc[i][1]} {df.iloc[i][0]}')
					if self.i + 1 < len(self.setups_df):
						self.i += 1
						self.update(self)
						self.preload(self)

				elif self.event == 'Yes' or self.event == 'No' or self.event == 'Skip':
					if self.event == 'Skip':
						pass

					else:
						if self.event == 'No':
							v = 0
						else:
							v = 1

						self.tune(self,v)

					self.i += 1
					self.update(self)
					#self.preload(self)
					
				elif self.event == 'Prev':
					if self.i > 0:
						self.i -= 1
						self.update(self)
						self.preload(self)
				elif self.event == 'Skip':
					self.i += 1
					self.update(self)
					self.preload(self)
					self.current_setups = []
					self.index = 0

				elif self.event == 'Enter':
					self.manual_log(self)

				elif self.event == 'Toggle':
					if self.use_no:
						self.use_no = False
					else:
						self.use_no = True

					self.window['-use_no-'].update('use no ' + str(self.use_no))


				elif self.event == '-GRAPH-':
					self.click(self)
				elif self.event == 'Trainer' or self.event == 'Validator' or self.event == 'Tuner' or self.event == 'Manual':
					#self.pool.terminate()
					if self.event == 'Trainer':
						self.menu = 0
					elif self.event == 'Validator':
						self.menu = 1
					elif self.event == 'Tuner':
						self.menu = 2

					elif self.event == 'Manual':
						self.menu = 3


					self.window.close()
					self.i = 0
					while True:

						try:
							if os.path.exists("C:/Screener/setups/charts"):
								shutil.rmtree("C:/Screener/setups/charts")
							os.mkdir("C:/Screener/setups/charts")
							break
						except:
							pass
					#if self.menu == 2:
					#	self.menu = 0
					#else:
					#	self.menu += 1
					self.init = True

					self.setups_df = pd.read_feather('C:/Screener/setups/database/' + self.current_setup + '.feather').sample(frac = 1).reset_index(drop = True)
					if self.menu == 1:
						self.setups_df = self.setups_df[self.setups_df['setup'] == 1]
					#self.current_setup = 'EP'
					if self.menu != 3:
						self.preload(self)
					self.update(self)
				elif self.event == 'right' or self.event == 'left':
					self.click(self,False)
				else:
					#self.pool.terminate()
					if self.menu == 0:
						self.log(self)
					else:
						self.setups_df = pd.read_feather('C:/Screener/setups/database/' + self.event + '.feather').sample(frac = 1).reset_index(drop = True)
						if self.menu == 1:
							self.setups_df = self.setups_df[self.setups_df['setup'] == 1]
						else:
							pass
						while True:

							try:
								if os.path.exists("C:/Screener/setups/charts"):
									shutil.rmtree("C:/Screener/setups/charts")
								os.mkdir("C:/Screener/setups/charts")
								break
							except:
								pass
						self.i = 0
						self.current_setup = self.event
						self.preload(self)
						self.update(self)
						self.window['-text-'].update(self.event)

	def preload(self):
		arglist = []
		amount = 10
		if self.menu == 2:
			amount = 40
		if self.i == 0:
			l = list(range(amount))
		else:
			l = [amount + self.i - 1]
		if self.menu == 0:
			for i in l:
				while True:
					try:
						ticker = self.tickers[random.randint(0,len(self.tickers)-1)]
						df = data.get(ticker,tf = self.current_tf)

						date_list = df.index.to_list()
						date = date_list[random.randint(0,len(date_list) - 1)]
						index = data.findex(df,date)
						left = index - self.size 
						if left < 0:
							left = 0
						df2 = df[left:index + 1]
						if len(df2) > 30:
							dolVol, adr, pmvol = detection.requirements(df2,len(df2) - 1,2,ticker)
							if self.current_tf == 'h':
								if dolVol > 2000000 and adr > 5:
									break
							else:
								if dolVol > 2000000 and adr > 2:
									break
					except Exception as e:
						if self.current_tf == 'h':
							print(e)
						pass
				self.dict.append([ticker,date,df2])
				arglist.append([i,df2])
		elif self.menu == 1:
			for i in l:
				if i < len(self.setups_df):
					try:
						bar = self.setups_df.iloc[i]
						
						ticker = bar[0]
						
						date = bar[1]
					
						df = data.get(ticker,self.current_setup.split('_')[0])
						index = data.findex(df,date)
					
						left = index-self.size
						if left < 0:
							left = 0

						df2 = df[left:index + 1]
						arglist.append([i,df2])
					except TimeoutError as e:
						print(e)
						arglist.append([i,pd.DataFrame()])
					
					
		elif self.menu == 2:
			tickers = pd.read_feather(r"C:\Screener\sync\full_ticker_list.feather")['Ticker'].to_list()
			for i in range(8):
				arglist.append([self.current_setup,tickers])

				
		self.pool.map_async(self.plot,arglist)

	def plot(bar):


		def save(df,strubg,fucked = False):
			
			
			try:
				if os.path.exists("C:/Screener/laptop.txt"): #if laptop
					fw = 22
					fh = 12
					fs = 4.1
				elif os.path.exists("C:/Screener/ben.txt"):
					fw = 27
					fh = 12
					fs = 1.6
				else:
					fw = 50
					fh = 23
					fs = 2.28
				mc = mpf.make_marketcolors(up='g',down='r')
				s  = mpf.make_mpf_style(marketcolors=mc)
				fig, axlist = mpf.plot(df, type='candle', volume=True  ,                          
				style=s, warn_too_much_data=100000,returnfig = True,figratio = (fw,fh),
				figscale=fs, panel_ratios = (5,1), title = tit,
				tight_layout = True,axisoff=True)
				ax = axlist[0]
				ax.set_yscale('log')
				ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())


				if fucked:
					path = "C:/Screener/setups//charts/"
					i = 0
					while True:
						done = True
						for god in os.listdir(path):
							if f'_{i}_' in god:
								i += 1
								done = False
								break
						if done:
							break

					strubg = '_' + str(i) + '_' + strubg + ".png"

				
				p = pathlib.Path("C:/Screener/setups/charts") / strubg

				plt.savefig(p, bbox_inches='tight')
			except Exception as e:
				print(e)
				p = pathlib.Path("C:/Screener/setups/charts") / strubg
				shutil.copy(r"C:\Screener\tmp\blank.png",p)



		i = bar[0]
		
		if isinstance(bar[0], str):
			setuptype = bar[0]
			tickers = bar[1]
			
			model = load_model('C:/Screener/sync/models/model_'+ setuptype)
			
			sys.stdout = open(os.devnull, 'w')
			while True:
				
				try:


					ticker = tickers[random.randint(0,len(tickers)-1)]
					df = data.get(ticker,tf = setuptype.split('_')[0])
					if len(df) > 10:
						size = len(df)
						
						for _ in range((int(size/2))):
							currentday = random.randint(0,size - 1)
				
							dolVol, adr, pmDolVol = detection.requirements(df,currentday,0,ticker)
							if (dolVol > 8000000 or pmDolVol  > .5 * 1000000) and adr > 2.8:



								df2 = create.reform(df,setuptype,currentday)
								#print(df2)
								

								z = model.predict(df2)[0][1]
								
							
								
								if z > .3:
									tit = str(round(z*100))
									god = currentday - 100
									if god < 0:
										god = 0
									df = df[god:currentday + 1]
									date = df.index[-1].date()
									tickerdate = f'+{ticker}+{date}+'


									


									save(df,tickerdate,True)

			
				except Exception as e:
					pass
					#sys.stdout = sys.__stdout__
					#print(e)
			sys.stdout = sys.__stdout__
		else:
			df = bar[1]
			strubg = str(i) + ".png"
			tit = ''
			save(df,strubg)











		
		p = pathlib.Path("C:/Screener/setups/charts") / strubg

		try:
			if os.path.exists("C:/Screener/laptop.txt"): #if laptop
				fw = 22
				fh = 12
				fs = 4.1
			elif os.path.exists("C:/Screener/ben.txt"):
				fw = 27
				fh = 12
				fs = 1.6
			else:
				fw = 50
				fh = 23
				fs = 2.28
			mc = mpf.make_marketcolors(up='g',down='r')
			s  = mpf.make_mpf_style(marketcolors=mc)
			fig, axlist = mpf.plot(df, type='candle', volume=True  ,                          
			style=s, warn_too_much_data=100000,returnfig = True,figratio = (fw,fh),
			figscale=fs, panel_ratios = (5,1), title = tit,
			tight_layout = True,axisoff=True)
			ax = axlist[0]
			ax.set_yscale('log')
			ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
			plt.savefig(p, bbox_inches='tight')
		except:
			shutil.copy(r"C:\Screener\tmp\blank.png",p)

if __name__ == '__main__':
	Trainer.loop(Trainer)







