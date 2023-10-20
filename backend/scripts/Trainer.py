
import pathlib, io, shutil, os, math, random, PIL
import pandas as pd
import numpy as np
import mplfinance as mpf
import PySimpleGUI as sg
from Data import Data as data
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from Screener import Screener as screener
from multiprocessing.pool import Pool

class Trainer:

	def run(self):
		with Pool(int(data.get_config('Data cpu_cores'))) as self.pool:
			sg.theme('DarkGrey')
			self.sub_preload_amount = 10
			self.trainer_cutoff = 60
			self.current_setup = 'd_EP'
			self.current_tf = self.current_setup.split('_')[0]
			self.full_ticker_list = screener.get('full')
			self.event = 'Trainer'
			while True:
				if self.event in ['Trainer','Validator','Tuner','Tester','Manual']:  
					self.current_menu = self.event
					self.init = True
					self.update(self)
				elif self.current_menu == 'Trainer': self.trainer(self)
				elif self.current_menu in ['Validator','Tuner']: self.validator_and_tuner(self)
				elif self.current_menu in ['Tester','Manual']: self.tester_and_manual(self)
				self.event, self.values = self.window.read()

	def trainer(self):
		if self.event in self.tf_list:
			self.current_tf = self.event
			self.current_setup = [s for s in self.full_setup_list if self.current_tf in s][0]
			self.init = True
			self.update(self)
		elif self.event in ['Skip No','Use No']:
			self.save_training_data(self)
			self.i += 1
			self.update(self)
			self.preload(self)
		elif self.event in ['right_button','left_button','-chart-']: self.click(self)
		else: self.log(self)

	def validator_and_tuner(self):
		if self.event in self.full_setup_list:
			if self.current_menu == 'Tuner':
				if not os.path.exists('C:/Stocks/sync/models/model_' + self.event): 
					sg.Popup(f'{self.event} model does not exist')
					return
				df = pd.read_feather('C:/Stocks/local/data/' + self.event + '.feather')
				length = len(df[df['value'] == 1])
				if  length < 150: 
					sg.Popup(f'{self.event} only has {length} yes data points')
					return
			self.init = True
			self.current_setup = self.event
			self.update(self)
		elif self.i < len(self.chart_info) - 1 or self.current_menu == 'Tuner':
			if self.event in ['right_button','left_button']:
				if self.event == 'right_button': val = 1
				else: val = 0
				if self.current_menu == 'Validator': 
					bar = self.chart_info[self.i]
					ident = self.setup_df.iloc[self.i]['source']
				else: 
					bar = self.chart_info[math.floor(self.i/self.sub_preload_amount)].get()[self.i%self.sub_preload_amount]
					ident = None
				try: data.add_setup(bar[1],bar[0].index[-1],self.current_setup,val,1,ident)
				except Exception as e: sg.popup(e)
			self.i += 1
			self.update(self)
			self.preload(self)

	def tester_and_manual(self):
		ticker = self.values['-input_ticker-']
		dt = self.values['-input_dt-']
		st = self.values['-input_st-']
		try:
			st.split('_')[1]
			if self.current_menu == 'Manual': data.add_setup(ticker,dt,st,1,0)
			else:
				x,_,_,_ = data.create_arrays(pd.DataFrame({'ticker':[ticker],'dt':[dt],'tf':[st.split('_')[0]]}))
				self.window['-score-'].update(f'{round(100 * data.load_model(st).predict(x)[:,1][0])}% confident')
		except Exception as e: sg.Popup(e)

	def update(self):
		if self.init:
			try: self.window.close()
			except: AttributeError
			data.consolidate_database()
			self.chart_info = []
			self.i = 0
			while os.path.exists('C:/Stocks/local/trainer/charts'):
				try: shutil.rmtree('C:/Stocks/local/trainer/charts')
				except: pass
			os.mkdir('C:/Stocks/local/trainer/charts')
			self.chart_edge_size = data.get_config('Trainer chart_edge_size')
			self.chart_height = data.get_config('Trainer image_box_height')
			self.chart_width = data.get_config('Trainer image_box_width')
			self.full_setup_list = data.get_setups_list()
			self.current_setup_list = [s for s in self.full_setup_list if self.current_tf in s]
			self.tf_list = [*set([s.split('_')[0] for s in self.full_setup_list])]
			graph = sg.Graph(canvas_size = (self.chart_width, self.chart_height), graph_bottom_left = (0, 0), graph_top_right = (self.chart_width, 
				self.chart_height), key = '-chart-', change_submits = (self.current_menu == 'Trainer'), background_color = 'grey', drag_submits = False)
			if self.current_menu == 'Trainer':
				self.selected_trainer_index = 0
				self.y = int(self.chart_height / 2)
				def setup_len(s):
					df = pd.read_feather('C:/Stocks/local/data/' + s + '.feather')
					return len(df[df['value'] == 1])
				self.setup_count_stats = [setup_len(s) for s in self.full_setup_list]
				layout = [[graph],
				[sg.Text(key = '-setup_count_stats-')],
				[sg.Button('Use No'), sg.Button('Skip No')] + [sg.Button(tf) for tf in self.tf_list]]
			elif self.current_menu == 'Validator':
				df = pd.read_feather('C:/Stocks/local/data/' + self.current_setup + '.feather').sample(frac = 1)
				df = df[df['value'] == 1]
				
				model = data.load_model(self.current_setup)
				df['tf'] = self.current_setup.split('_')[0]
				print(len([*set(df['ticker'].to_list())]))
				
				x,y,info,dfs = self.pool.apply(data.create_arrays,[df])
				setups = data.score(x,info,dfs,self.current_setup,model,0)
				print(len(x))
				print(len(df))
				print(len(info))
				df['score'] = [bar[2] for bar in setups]
				layout = [[graph],
				[sg.Button(s) for s in self.full_setup_list],
				[sg.Text(self.current_setup), sg.Text(key = '-counter-')]]
			elif self.current_menu == 'Tuner':
				layout = [[graph],
				[sg.Button(s) for s in self.full_setup_list],
				[sg.Text(self.current_setup)],]
			elif self.current_menu in ['Tester','Manual']:
				layout = [[sg.Text('Ticker'),sg.InputText(key = '-input_ticker-')],
				[sg.Text('Datetime'),sg.InputText(key = '-input_dt-')],
				[sg.Text('Setup Type'),sg.InputText(key = '-input_st-')],
				[sg.Button('Enter')]]
				if self.current_menu == 'Tester': layout.append([sg.Text(key = '-score-')])
			layout.append([sg.Button(m) for m in ['Trainer','Validator','Tuner','Tester','Manual']])
			self.window = sg.Window(self.current_menu, layout, margins = (10,10), scaling = data.get_config('Trainer ui_scale'), finalize = True)
			self.init = False
			self.preload(self)
		self.window.maximize()
		if self.current_menu in ['Trainer','Validator','Tuner']:
			for k, v in [['<q>', '1'],['<w>', '2'],['<e>', '3'],['<a>', '4'],['<s>', '5'],['<d>', '6'],
				['<z>', '7'],['<x>', '8'],['<c>', '9'],['<p>', 'right_button'],['<i>', 'left_button'],['<o>', 'center_button']]:
				self.window.bind(k,v)
			self.window['-chart-'].erase()
			while True:
				try:
					image1 = PIL.Image.open(r'C:/Stocks/local/trainer/charts/' + str(self.i) + '.png')
					bio1 = io.BytesIO()
					image1.save(bio1, format='PNG')
					self.window['-chart-'].draw_image(data=bio1.getvalue(), location=(0, self.chart_height))
					break
				except: pass
		if self.current_menu == 'Trainer':
			self.x_size = image1.size[0]
			self.select_line_x = 0
			self.select_line = self.window['-chart-'].draw_line((self.select_line_x,0), (self.select_line_x,self.chart_height), color='green', width=1)
			df = self.chart_info[self.i][0]
			chart_size = self.x_size - 20
			round_x = int((self.trainer_cutoff)/(len(df)) * (chart_size)) + 10 - int((chart_size/len(df))/2)
			self.window['-chart-'].draw_line((round_x,0), (round_x,self.chart_height), color='red', width=2)
			self.current_setups = []
		elif self.current_menu == 'Validator': self.window['-counter-'].update(f'{self.i + 1} of {len(self.setup_df)}')

	def preload(self):
		












		if self.current_menu in ['Trainer','Validator']:
			if self.i == 0: index_list = list(range(10))
			else: index_list = [self.i + 9]
			for i in index_list:
				if self.current_menu == 'Trainer':
					while True:
						ticker = self.full_ticker_list[random.randint(0,len(self.full_ticker_list)-1)]
						df = data.get(ticker,tf = self.current_tf)
						if not df.empty:
							index = random.randint(0,len(df) - 1)
							left = index - 300
							if left < 0:left = 0
							df = df[left:index+ 1]
							if data.get_requirements(ticker, df, self.current_setup): break
					title = ''
				elif self.current_menu == 'Validator':
					if i >= len(self.setup_df): break
					ticker = self.setup_df.iat[i,0]
					dt = self.setup_df.iat[i,1]
					df = data.get(ticker,self.current_setup.split('_')[0],dt,250)
					title = f'{self.current_setup} {self.setup_df.iat[i,2]}'
				self.chart_info.append([df,ticker,title,i])
			arglist = [self.chart_info[i] for i in index_list if i in list(range(len(self.chart_info)))]
			self.pool.map_async(Trainer.plot,arglist)
		elif self.current_menu == 'Tuner':
			run = True
			if self.i == 0: index_list = list(range(0,self.sub_preload_amount*6,self.sub_preload_amount))
			elif self.i%self.sub_preload_amount == 0: index_list = [self.i + self.sub_preload_amount*5]
			else: run = False
			if run:
				arglist = [[list(range(i,i+self.sub_preload_amount)),self.current_tf,self.current_setup,self.full_ticker_list] for i in index_list]
				for arg in arglist: self.chart_info.append (self.pool.apply_async(Trainer.create_tune, args = (arg)))
				
	def create_tune(i_list,current_tf,st,full_ticker_list):
		model = data.load_model(st)
		info_list = []
		ii = 0
		while True:
			ticker = full_ticker_list[random.randint(0,len(full_ticker_list)-1)]
			x,_,info, dfs = data.create_arrays(pd.DataFrame({'ticker':[ticker],'dt':[None],'tf':[current_tf]}))
			#dfs ={ticker:data.get(ticker,tf = current_tf)}
			#if list(dfs.values())[0].empty: continue#zzzzzz theres gotta be a better way to check if the df is empty
			#x,_,info = data.format(dfs,True)
			setups = data.score(x,info,dfs,st,model,use_requirements=True)
			for ticker,_,score,df in setups:
				index = 300
				if index >= len(df): index = len(df) - 1
				df = df[-index:]
				title = str(score)
				i = i_list[ii]
				Trainer.plot([df,ticker,title,i])
				info_list.append([df,ticker,title,i])
				ii += 1
				if ii == len(i_list):
					return info_list

	def plot(bar):
		df = bar[0]
		title = bar[2]
		i = bar[3]
		p = pathlib.Path('C:/Stocks/local/trainer/charts') / (str(i) + '.png')
		try:
			_, axlist = mpf.plot(df, type = 'candle', volume=True, style = mpf.make_mpf_style(marketcolors = mpf.make_marketcolors(up = 'g', down = 'r')), warn_too_much_data=100000, returnfig = True, figratio = (data.get_config('Trainer chart_aspect_ratio'),1),
			figscale = data.get_config('Trainer chart_size'), panel_ratios = (5,1), title = title, tight_layout = True,axisoff=True)
			ax = axlist[0]
			ax.set_yscale('log')
			ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
			plt.savefig(p, bbox_inches='tight',dpi = data.get_config('Trainer chart_dpi'))
		except Exception as e: 
			print(e)
			shutil.copy(r'C:\Stocks\sync\files\blank.png',p)
						
	def save_training_data(self):
		info = self.chart_info[self.i][0]
		ticker = self.chart_info[self.i][1]
		ii = 0
		for s in self.current_setup_list:
			df = pd.DataFrame()
			df['dt'] = info.index
			df['ticker'] = ticker
			df['value'] = 0
			df['required'] = 0
			for bar in self.current_setups:
				if bar[1] == s:
					self.setup_count_stats[ii] += 1
					index = bar[0]
					df.iat[index,2] = 1
					if index <= self.trainer_cutoff:
						add = pd.DataFrame({'ticker':[ticker],'dt':[info.index[index]], 'value':[1], 'required':[0]})
						df = pd.concat([df,add]).reset_index(drop = True)
			df = df[self.trainer_cutoff:]
			if self.event == 'Skip No': df = df[df['value'] == 1]
			if df.empty: continue
			ident = data.get_config('Data identity')
			path = 'C:/Stocks/sync/database/' + ident + '_' + s + '.feather'
			try: setup_df = pd.read_feather(path)
			except FileNotFoundError: setup_df = pd.DataFrame()
			df = pd.concat([setup_df,df[['ticker','dt','value','required']]]).reset_index(drop = True)
			df.to_feather(path)

	def click(self):
		df = self.chart_info[self.i][0]
		chart_size = self.x_size - (self.chart_edge_size*2)
		if self.event == '-chart-':
			x = self.values['-chart-'][0]
			self.y = self.values['-chart-'][1]
			percent = (x - self.chart_edge_size)/chart_size
			self.selected_trainer_index = math.floor(len(df) * percent)
			if self.selected_trainer_index <= -1: self.selected_trainer_index = 0
			if self.selected_trainer_index >= len(df): self.selected_trainer_index = len(df) - 1
			try: self.date = df.index[self.selected_trainer_index]
			except: return
		else:
			if self.event == 'right_button' and self.selected_trainer_index < len(df) - 1: self.selected_trainer_index += 1
			elif self.event == 'left_button' and self.selected_trainer_index > 0: self.selected_trainer_index -= 1
			self.y = int ((self.chart_height/4)*3)
		round_x = int((self.selected_trainer_index + 1)/len(df) * (self.x_size - (self.chart_edge_size * 2))) + self.chart_edge_size - int((chart_size/len(df))/2)
		self.window['-chart-'].MoveFigure(self.select_line,round_x - self.select_line_x,0)
		self.select_line_x = round_x

	def log(self):
		if self.event == 'center_button':
			for i in range(len(self.current_setups) - 1,-1,-1):
				if self.current_setups[i][0] == self.selected_trainer_index:
					for k in range(2): self.window['-chart-'].MoveFigure(self.current_setups[i][2][k],5000,0)
					del self.current_setups[i]
			self.window.refresh()
		else:
			try:
				i = int(self.event)
				setup = self.current_setup_list[i-1]
			except IndexError: return
			y = self.y - 50
			if y < int (self.chart_height/4): y = int(self.chart_height/4)
			if y > int ((self.chart_height/4)*3): y = int ((self.chart_height/4)*3)
			text = self.window['-chart-'].draw_text(setup, (self.select_line_x,y), font = None, color = 'black', angle = 0, text_location = 'center')
			line = self.window['-chart-'].draw_line((self.select_line_x,0), (self.select_line_x,self.chart_height), color = 'black', width = 1)
			self.current_setups.append([self.selected_trainer_index,setup,[line,text]])
			self.y -= 30

if __name__ == '__main__':
	Trainer.run(Trainer)