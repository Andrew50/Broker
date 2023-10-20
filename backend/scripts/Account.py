from inspect import Attribute
import numpy as np
import pandas as pd
from tqdm import tqdm
from imbox import Imbox
import mplfinance as mpf
import PySimpleGUI as sg
from Data import Data as data
import matplotlib.ticker as mticker
from matplotlib import pyplot as plt
from multiprocessing.pool import Pool
import datetime,PIL, io, pathlib, shutil, os, statistics

class Run:

	def run(self):
		with Pool(int(data.get_config('Data cpu_cores'))) as self.pool:
			sg.theme('Black')
			try: self.df_log = pd.read_feather(r"C:\Stocks\local\account\log.feather")
			except FileNotFoundError: self.df_log = pd.DataFrame()
			try: self.df_traits = pd.read_feather(r"C:\Stocks\local\account\traits.feather")
			except FileNotFoundError: self.df_traits = pd.DataFrame()
			try: self.df_pnl = pd.read_feather(r"C:\Stocks\local\account\pnl.feather").set_index('datetime', drop = True)
			except FileNotFoundError: self.df_pnl = pd.DataFrame()
			try: self.queued_recalcs = pd.read_feather('C:/Stocks/local/account/queued_recalcs.feather')
			except FileNotFoundError: self.queued_recalcs = pd.DataFrame()
			self.init = True
			self.event = 'Log'
			while True:
				if self.event in ["Traits", "Plot", "Account", "Log"]: Run.change_menu(self)
				if self.menu == "Traits": Traits.traits(self)
				elif self.menu == "Plot": Plot.plot(self)
				elif self.menu == "Account": Account.account(self)
				elif self.menu == "Log": Log.log(self)
				self.event, self.values = self.window.read()

	def change_menu(self):
		if self.event != 'Log':
			if self.df_log.empty: 
				sg.Popup('Log is empty')
				return
			if self.df_pnl.empty: Account.calc(self,self.df_log)
			if self.df_traits.empty: Traits.calc(self,self.df_log)
			if not self.queued_recalcs.empty: 
				try:
					Account.calc(self)
					Traits.calc(self)
					self.queued_recalcs = pd.DataFrame()
					try: os.remove('C:/Stocks/local/account/queued_recalcs.feather')
					except FileNotFoundError: pass
				except Exception as e: sg.Popup(str('While recaculating:    ') + str(e))
		self.menu = self.event
		self.init = True
		try: self.window.close()
		except AttributeError: pass

class Log:

	def log(self):
		if self.init: Log.update(self)
		elif self.event == 'Pull': Log.pull(self)
		elif self.event == 'Enter': Log.manual_log(self)
		elif self.event == 'Delete':
			updated_log = self.df_log.drop(self.log_index).reset_index(drop = True)
			Log.queue_recalcs(self,updated_log)
		elif self.event == 'Clear': 
			if self.log_index == None: Log.update_inputs(self)
			else: 
				self.log_index = None
				self.window['-log_table-'].update(select_rows=[])
		elif self.event == '-log_table-':
			try:
				self.log_index = self.values['-log_table-'][0]
				Log.update_inputs(self)
			except IndexError: pass

	def update(self):
		if self.init:
			self.init = False
			self.log_index = None
			toprow = ['Ticker        ','Datetime        ','Shares ', 'Price   ','Setup    ']
			c1 = [[(sg.Text("Ticker    ")),sg.InputText(key = '-input_ticker-')],
			[(sg.Text("Datetime")),sg.InputText(key = '-input_datetime-')],[(sg.Text("Shares   ")),sg.InputText(key = '-input_shares-')],[(sg.Text("Price     ")),sg.InputText(key = '-input_price-')],
			[(sg.Text("Setup    ")),sg.InputText(key = '-input_setup-')], [sg.Button('Delete'),sg.Button('Clear'),sg.Button('Enter')],[sg.Button('Pull')],
			[sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]
			c2 = [[sg.Table([],headings=toprow,key = '-log_table-',auto_size_columns=True,num_rows = 30,justification='left',enable_events=True,selected_row_colors='red on yellow')]]
			layout = [[sg.Column(c1),sg.VSeperator(),sg.Column(c2),]]
			self.window = sg.Window('Log', layout,margins = (10,10),scaling=data.get_config('Log ui_scale'),finalize = True)
		self.window['-log_table-'].update(self.df_log.values.tolist())
		self.window.maximize()

	def queue_recalcs(self,updated_log):
		if not self.df_log.empty: 
			new_log = pd.concat([self.df_log, updated_log]).drop_duplicates(subset = ['ticker','datetime','shares','price'], keep = False).sort_values(by='datetime', ascending = False)
			self.df_log = updated_log.sort_values(by='datetime', ascending = False).reset_index(drop = True)
			self.queued_recalcs = pd.concat([self.queued_recalcs,new_log]).reset_index(drop = True)
		else:
			self.df_log = updated_log
			self.queued_recalcs = updated_log
		self.queued_recalcs.to_feather('C:/Stocks/local/account/queued_recalcs.feather')
		Log.update(self)
		self.df_log.to_feather(r"C:\Stocks\local\account\log.feather")

	def update_inputs(self):
		if self.log_index == None: bar = ['','','','','']
		else: bar = self.df_log.iloc[self.log_index]
		self.window["-input_ticker-"].update(bar[0])
		self.window["-input_datetime-"].update(bar[1])
		self.window["-input_shares-"].update(bar[2])
		self.window["-input_price-"].update(bar[3])
		self.window["-input_setup-"].update(bar[4])

	def manual_log(self):
		ticker = self.values['-input_ticker-']
		shares = float(self.values['-input_shares-'])
		price = float(self.values['-input_price-'])
		setup = self.values['-input_setup-']
		try:
			dt = datetime.datetime.strptime(self.values['-input_datetime-'], '%Y-%m-%d %H:%M:%S')
			if ticker == '' or shares == '' or price == '': raise TimeoutError
		except (TimeoutError, TypeError):
			sg.Popup('check inputs')
			return
		updated_log = self.df_log.copy()
		if self.log_index == None: 
			add = pd.DataFrame({'ticker':[ticker],'datetime':[dt],'shares':[shares],'price':[price],'setup':[setup]})
			updated_log = pd.concat([updated_log,add]).reset_index(drop = True)
		else:
			updated_log.iat[self.log_index,0] = ticker
			updated_log.iat[self.log_index,1] = dt
			updated_log.iat[self.log_index,2] = shares
			updated_log.iat[self.log_index,3] = price
			updated_log.iat[self.log_index,4] = setup
		self.log_index = None
		self.window['-log_table-'].update(select_rows=[])
		Log.queue_recalcs(self,updated_log)
	
	def pull(self):
		ident = data.get_config('Data identity')
		if ident in ['desktop','laptop']:
			download_folder = "C:/Stocks/local/account"
			if not os.path.isdir(download_folder): os.makedirs(download_folder, exist_ok=True)
			mail = Imbox("imap.gmail.com", username="billingsandrewjohn@gmail.com", password='kqnrpkqscmvkrrnm', ssl=True, ssl_context=None, starttls=False)
			dt = datetime.date.today() - datetime.timedelta(days = 1)
			messages = mail.messages(sent_from='noreply@email.webull.com',date__gt=dt)
			for (uid, message) in messages:
				mail.mark_seen(uid)
				for _, attachment in enumerate(message.attachments):
					att_fn = attachment.get('filename')
					if not 'IPO' in att_fn and not  'Options' in att_fn:
						download_path = f"{download_folder}/{att_fn}"
						with open(download_path, "wb") as fp:
							fp.write(attachment.get('content').read())
			mail.logout()
			log = pd.read_csv(download_folder + '/Webull_Orders_Records.csv')
			log2 = pd.DataFrame()
			log2['ticker'] = log['Symbol'] 
			log2['datetime']  = pd.to_datetime(log['Filled Time'],format='mixed')
			log2['shares'] = log['Total Qty']
			log2['price'] = log['Avg Price']
			for i in range(len(log)):
				if log.at[i,'Side'] != 'Buy':
					log2.at[i,'shares'] *= -1
			log2['setup'] = ''
			log2 = log2.dropna()
			log2 = log2[(log2['datetime'] > '2021-12-01')]
			log2 = log2.sort_values(by='datetime', ascending = False).reset_index(drop = True)
			updated_log = log2
		elif ident == 'ben':
			raise Exception('need to fix pull method ben')
			df = pd.read_csv("C:/Screener/11-26-21 orders.csv")
			df = df.drop([0, 1, 2])
			dfnew = []
			for i in range(len(df)):
				if "FILLED" in df.iloc[i][1]:
					if "-" not in df.iloc[i][0]:
						dfnew.append(df.iloc[i])
			dfnew = pd.DataFrame(dfnew)
			dfn = []
			dfn = pd.DataFrame(dfn)
			for i in range(len(dfnew)):
				ticker = dfnew.iloc[i][0]
				price = dfnew.iloc[i][1].split("$")[1]
				shareSplit = dfnew.iloc[i][3].split(" ")
				shares = None
				for j in range(len(shareSplit)):
					if(shareSplit[j].isnumeric() == True):
						shares = shareSplit[j]
				shares = float(shares)
				for e in range(len(shareSplit)):
					if("Sell" in shareSplit[e]):
						shares = -shares
				dateSplit = dfnew.iloc[i][4].split(" ")
				dateS = dateSplit[1].split("\n")
				date = dateS[1] + " " + dateSplit[0]
				date = pd.to_datetime(date)
				le = len(dfn)
				dfn.at[le, 'ticker'] = str(ticker)
				dfn.at[le, 'datetime'] = date
				dfn.at[le, 'shares'] = float(shares)
				dfn.at[le, 'price'] = float(price)
				dfn.at[le, 'setup'] = ""
			dfn = pd.DataFrame(dfn)
			updated_log =  dfn
		else:
			raise Exception('no pull method created')
		if not self.df_log.empty: updated_log = pd.concat([updated_log,self.df_log[self.df_log['ticker'] == 'Deposit']]).sort_values('datetime',ascending = False).reset_index(drop = True)
		Log.queue_recalcs(self,updated_log)

class Traits:

	def traits(self):
		if self.event == 'Recalc': 
			Traits.calc(self,self.df_log)
			self.queued_recalcs = pd.DataFrame()
			try: os.remove('C:/Stocks/local/account/queued_recalcs.feather')
			except FileNotFoundError: pass
		elif (self.event == '-table_losers-' or self.event == '-table_winners-') and len(self.values[self.event]) > 0:
			sorted_df = self.df_traits.sort_values('pnl a', ascending = (self.event == '-table_winners-')).reset_index(drop = True)
			Plot.create([self.values[self.event][0],sorted_df,True])
		elif '+CLICKED+' in self.event:
			table = self.window[self.event[0]].Values
			god = self.event[2][1]
			if god == 0: god = 1
			y = [b[god] for b in table]
			x = [b[0] for b in table]
			plt.clf()
			plt.scatter(x,y,s = data.get_config('Traits marker_size'))
			if self.event[0] == '-table_rolling_traits-':
				x_filler = [i + 1 for i in range(len(table))]
				z = np.polyfit(x_filler[1:], y[1:], 1)
				p = np.poly1d(z)
				plt.plot(x_filler,p(x_filler),"r--")
				plt.xticks(x_filler, x)
			plt.gcf().set_size_inches((data.get_config('Traits chart_size') * data.get_config('Traits chart_aspect_ratio') * 22.5,data.get_config('Traits chart_size') * 25.7))
			plt.savefig(pathlib.Path("C:/Stocks/local/account") / "trait.png",bbox_inches='tight')
		elif self.event == 'Load':
			try: x = self.df_traits[self.values['-input_trait-']]
			except Exception as e: sg.Popup(e)
			else:
				plt.clf()
				plt.hist(x, ec='black', bins=25)
				plt.gcf().set_size_inches((data.get_config('Traits chart_size') * data.get_config('Traits chart_aspect_ratio') * 22.5,data.get_config('Traits chart_size') * 25.7))
				plt.savefig(pathlib.Path("C:/Stocks/local/account") / "trait.png",bbox_inches='tight')
		Traits.update(self)

	def update(self):
		if self.init:
			self.init = False
			rolling_traits_header = ['date  ','gain','loss','win  ','max ','m time','miss','risk','size ','#  ','% a  ']
			biggest_trades_header = ['# ','tick','% a ']
			setup_traits_header = ['setup'] + rolling_traits_header[1:]
			weekday_traits_header = ['weekday'] + rolling_traits_header[1:]
			c1 = [[sg.Table([],headings=biggest_trades_header,key = '-table_winners-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,selected_row_colors='red on yellow')]]
			c3 = [[sg.Table([],headings=setup_traits_header,key = '-table_setups-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,enable_click_events=True)]]
			c4 = [[sg.Table([],headings=rolling_traits_header,key = '-table_rolling_traits-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,enable_click_events=True)]]
			c45 = [[sg.Table([],headings=weekday_traits_header,key = '-table_weekday_traits-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,enable_click_events=True)]]
			c5 = [[sg.Table([],headings=['S%','$'],key = '-table_sell_percent_traits-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,enable_click_events=True)]]
			c6 = [[sg.Table([],headings=['Sa','$'],key = '-table_sell_account_traits-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,enable_click_events=True)]]
			c7 = [[sg.Table([],headings=['S%','$'],key = '-table_stop_percent_traits-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,enable_click_events=True)]]
			c8 = [[sg.Table([],headings=['Sa','$'],key = '-table_stop_account_traits-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,enable_click_events=True)]]
			c9 = []
			c10 = [[sg.Button('Recalc'),sg.Button('Load'),sg.Input(key = '-input_trait-',size = 10)], [sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]
			c11 = [[sg.Image(key = '-CHART-')]]
			layout = [[sg.Column(c1), sg.VSeperator(),  sg.Column(c3), sg.VSeperator(), sg.Column(c4), sg.VSeperator(),sg.Column(c45), sg.VSeperator(),sg.Column(c5), sg.VSeperator(),sg.Column(c6),  sg.VSeperator(), sg.Column(c7),  sg.VSeperator(), sg.Column(c8),  sg.VSeperator(), sg.Column(c9)],[sg.Column(c10),sg.VSeperator(),sg.Column(c11),]]
			self.window = sg.Window('Traits', layout,margins = (10,10),scaling=data.get_config('Traits ui'),finalize = True)
			self.window.maximize()
		sell_percent_table, sell_account_table, stop_percent_table, stop_account_table = Traits.build_optimal_traits_table(self)
		self.window['-table_winners-'].update(Traits.build_trades_table(self))
		self.window['-table_setups-'].update(Traits.build_setup_traits_table(self))
		self.window['-table_rolling_traits-'].update(Traits.build_rolling_traits_table(self))
		self.window['-table_weekday_traits-'].update(Traits.build_weekday_traits_table(self))
		self.window['-table_sell_percent_traits-'].update(sell_percent_table)
		self.window['-table_sell_account_traits-'].update(sell_account_table)
		self.window['-table_stop_percent_traits-'].update(stop_percent_table)
		self.window['-table_stop_account_traits-'].update(stop_account_table)
		if os.path.exists('C:/Stocks/local/account/trait.png'):
			image = PIL.Image.open('C:/Stocks/local/account/trait.png')
			bio = io.BytesIO()
			image.save(bio, format="PNG")
			self.window['-CHART-'].update(data = bio.getvalue())
			
	def build_optimal_traits_table(self):
		current_pnl = sum(self.df_traits['pnl $'])
		traits = self.df_traits.dropna().reset_index(drop = True)
		sell_percent_table = []
		for thresh in [x/8 for x in range(1,161)]:
			df = traits.copy()
			for i in range(len(df)):
				if df.at[i,'max %'] >= thresh: df.at[i,'pnl $'] = df.at[i,'size $'] * thresh / 100
				elif df.at[i,'pnl $'] > 0: df.at[i,'pnl $'] = 0
			sell_percent_table.append([thresh,sum(df['pnl $'].tolist()) - current_pnl])
		sell_account_table = []
		for thresh in [x/8 for x in range(1,161)]:
			df = traits.copy()
			for i in range(len(df)):
				if df.at[i,'max a'] >= thresh: df.at[i,'pnl $'] = df.at[i,'account_size'] * thresh / 100
				elif df.at[i,'pnl $'] > 0: df.at[i,'pnl $'] = 0
			sell_account_table.append([thresh,sum(df['pnl $'].tolist()) - current_pnl])
		stop_percent_table = []
		for thresh in [x/16 for x in range(0,-81,-1)]:
			df = traits.copy()
			for i in range(len(df)):  
				if df.at[i,'min %'] <= thresh: df.at[i,'pnl $'] = df.at[i,'size $'] * thresh / 100
			stop_percent_table.append([thresh,sum(df['pnl $'].tolist()) - current_pnl])
		stop_account_table = []
		for thresh in [x/16 for x in range(0,-81,-1)]:
			df = traits.copy()
			for i in range(len(df)):  
				if df.at[i,'min a'] <= thresh: df.at[i,'pnl $'] = df.at[i,'account_size'] * thresh / 100
			stop_account_table.append([thresh,sum(df['pnl $'].tolist()) - current_pnl])
		return sell_percent_table, sell_account_table, stop_percent_table, stop_account_table

	def calc_trait_values(df,title):
		avg_loss = df[df['pnl a'] <= 0]['pnl a'].mean()
		avg_gain = df[df['pnl a'] > 0]['pnl a'].mean()
		wins = []
		for i in range(len(df)):
			if df.iloc[i]['pnl $'] > 0: wins.append(1)
			else: wins.append(0)
		win = statistics.mean(wins) * 100
		high = df['max %'].mean()
		max_time = df['max time'].mean()
		miss = df['miss %'].mean()
		risk = df[df['risk %'] > 0]['risk %'].mean()
		size = df[df['size %'] > 0]['size %'].mean()
		pnl_list = df['pnl a'].tolist()
		pnl = 1
		print(pnl_list)
		for trade in pnl_list: pnl *= trade/100 + 1

		print(pnl)
		pnl -= 1
		pnl*= 100
		trades = len(df)
		return [title,round(avg_gain,1), round(avg_loss,1), round(win),round(high,1), round(max_time,1), round(miss,1), round(risk,2), round(size), round(trades,0), round(pnl,1)]

	def build_weekday_traits_table(self):
		df = self.df_traits.copy()
		df['datetime'] = df['datetime'].dt.day_name()
		groups = df.groupby(pd.Grouper(key='datetime'))
		dfs = [group for _,group in groups]
		return [Traits.calc_trait_values(df,df.iloc[0]['datetime']) for df in dfs]


	def build_rolling_traits_table(self):
		groups = self.df_traits.groupby(pd.Grouper(key='datetime', freq='3M'))
		dfs = [group for _,group in groups]
		rolling_traits = [Traits.calc_trait_values(self.df_traits,'Overall')]
	
		for df in dfs: rolling_traits.append(Traits.calc_trait_values(df,str(df.iat[0,0])[:-12]))
		return rolling_traits

	def build_setup_traits_table(self):
		groups = self.df_traits.groupby(pd.Grouper(key='setup'))
		dfs = [group for _,group in groups]
		return [Traits.calc_trait_values(df,df.iloc[0]['setup']) for df in dfs]
		
	def build_trades_table(self):
		sorted_df = self.df_traits.sort_values('pnl a', ascending = False).reset_index(drop = True)
		df = pd.DataFrame()
		df['#'] = sorted_df.index + 1
		df['Ticker'] = sorted_df['ticker']
		df['% a'] = sorted_df['pnl a'].round(2)
		return df.values.tolist()


	def estimate_setups(df_traits):

		sort = df_traits[df_traits['setup'] == '']
		if not sort.empty:

			df_traits['score'] = -1

			df_traits = df_traits.set_index('datetime')

			tf = 'd'

			df = pd.DataFrame()
			df['ticker'] = sort['ticker']
			df['dt'] = sort['datetime']
			df['tf'] = tf
			x,t,info,dfs = data.create_arrays(df)
			model_list = [[st,data.load_model(st)] for st in data.get_config('Screener active_setup_list').split(',') if tf in st]
			for st, model in model_list:

				setups = data.score(x,info,dfs,st,model,0)
				for ticker,dt,score,_ in setups: 
					
					
					try: index = data.findex(df_traits,dt)
					except:
						index = 0
					while ticker != df_traits.iloc[index][0]: index += 1

					if score > df_traits.iloc[index]['score']:
						df_traits.iat[index,24] = score
						df_traits.iat[index,2] = st
				

		df_traits = df_traits.drop(columns = 'score')
		df_traits = df_traits.reset_index()
		return df_traits


	def calc(self,changed_logs = pd.DataFrame()):
		if changed_logs.empty: changed_logs = self.queued_recalcs
		dfs = []
		ticker_list = [*set(changed_logs['ticker'])]
		for ticker in ticker_list:
			dfs.append(self.df_log[self.df_log['ticker'] == ticker])
			if not self.df_traits.empty: self.df_traits = self.df_traits[self.df_traits['ticker'] != ticker]
		trades = Traits.calc_trades(pd.concat(dfs))
		arglist = [[trades.iloc[i], self.df_pnl] for i in range(len(trades))]
		new_traits = pd.concat(data.pool(Traits.calc_traits,arglist))
		self.df_traits = pd.concat([self.df_traits,new_traits]).sort_values(by = 'datetime',ascending = True).reset_index(drop = True)
		self.df_traits = Traits.estimate_setups(self.df_traits.copy())
		self.df_traits.to_feather(r'C:\Stocks\local\account\traits.feather')





	def calc_trades(df_log):
		pos = []
		df_log = df_log.sort_values(by='datetime',ascending = True).reset_index(drop = True)
		df_traits = pd.DataFrame()
		for k in range(len(df_log)):
			row = df_log.iloc[k]
			ticker = row[0]
			if ticker != 'Deposit':
				shares = row[2]
				date = row[1]
				index = None
				for i in range(len(pos)):
					if pos[i][0] == ticker:
						index = i
						break
				if index != None: prev_share = pos[index][2]
				else:
					prev_share = 0
					pos.append([ticker,date,shares,[]])
					index = len(pos) - 1
				pos[index][3].append([str(x) for x in row])
				open_shares = prev_share + shares
				if open_shares == 0:
					for i in range(len(pos)):
						if pos[i][0] == ticker:
							index = i
							bar = pos[i]
							add = pd.DataFrame({'ticker': [bar[0]],'datetime':[data.format_date(bar[1])],'trades': [bar[3]]})
							df_traits = pd.concat([df_traits,add])
							del pos[i]
							break
				else: pos[index][2] = open_shares
		for i in range(len(pos)-1,-1,-1):
			index = i
			bar = pos[i]
			add = pd.DataFrame({'ticker': [bar[0]],'datetime':[data.format_date(bar[1])],'trades': [bar[3]]})
			df_traits = pd.concat([df_traits,add])
			del pos[i]
		return df_traits

	def calc_traits(pack):
		bar = pack[0]
		df_pnl = pack[1]
		ticker = bar[0]
		trades = bar[2]
		first_trade = trades[0]
		last_trade = trades[-1]
		open_datetime = data.format_date(first_trade[1])
		close_datetime = data.format_date(last_trade[1])
		try: account_size = df_pnl.iloc[data.findex(df_pnl,open_datetime)]['account']
		except IndexError: account_size = df_pnl.iloc[-1]['account']
		if account_size == 0: account_size = 148.19
		df_1min = data.get(ticker,'1min',close_datetime)
		time = datetime.time(9,30,0)
		rounded_open_datetime = datetime.datetime.combine(open_datetime.date(),time)
		try: 
			index = data.findex(df_1min,rounded_open_datetime)
			df_1min = df_1min[index:]
			data_exists = True
		except IndexError: 
			data_exists = False
		if float(first_trade[2]) > 0: direction = 1
		else:  direction = -1
		arrow_list = []
		current_size = 0
		total_size = 0
		high_dollars = 0
		low_dollars = 0
		pnl_dollars = 0
		max_time = 0
		open_shares = 0
		size_dollars = 0
		total_size = 0
		current_pnl = 0
		setup = ''
		for i in range(len(trades)):
			date = trades[i][1]
			shares = float(trades[i][2])
			price = float(trades[i][3])
			dollars = price * shares
			total_size += abs(dollars)
			current_size += dollars
			pnl_dollars -= dollars
			if setup == '' and trades[i][4] != '': setup = trades[i][4]
			if abs(current_size) > abs(size_dollars): size_dollars = abs(current_size)
			if shares > 0:
				color = 'g'
				symbol = '^'
			else:
				color = 'r'
				symbol = 'v'
			arrow_list.append([str(date),str(price),str(color),str(symbol)])
			if not data_exists:
				if current_pnl < low_dollars: low_dollars = current_pnl
				if current_pnl > high_dollars: high_dollars = current_pnl
			open_shares += shares
		if open_shares != 0:
			if data_exists: pnl_dollars += open_shares * df_1min.iat[-1,3]
			else: pnl_dollars += open_shares * price
			closed = False
		else: closed = True
		size_percent = (size_dollars / account_size) * 100
		if data_exists:
			if direction == 1: 
				low_col = 2
				high_col = 1
			else: 
				low_col = 1
				high_col = 2
			low_dollars = 0
			high_dollars = 0
			lod_price = df_1min.iat[0,2]
			min_percent = 0
			open_shares = 0
			next_trade_date = data.format_date(first_trade[1])
			trade_index = 0
			opened = False
			prev_low = 0
			prev_high = 0
			current_low = 0
			current_high = 0
			size = 0
			min_time = 0
			max_time = 0
			trade_open_price = float(first_trade[3])
			high_price = trade_open_price
			low_price = trade_open_price
			for i in range(len(df_1min)):
				date = df_1min.index[i]
				low = df_1min.iat[i,low_col]
				high = df_1min.iat[i,high_col]
				if opened:
					if high*direction > high_price*direction: 
						high_price = high
						max_time = (data.format_date(date) - open_datetime).days
					if low*direction < low_price*direction: 
						low_price = low
						min_time = (data.format_date(date) - open_datetime).days
				else:
					if direction*low < direction*lod_price:
						lod_price = low
				while date > next_trade_date:
					opened = True
					shares = float(trades[trade_index][2])
					price = float(trades[trade_index][3])
					open_shares += shares
					trade_index += 1
					size += shares*price
					current_low += shares * (prev_low - price)
					current_high += shares * (prev_high - price)
					try: next_trade_date = data.format_date(trades[trade_index][1])
					except IndexError: next_trade_date = datetime.datetime.now()
				current_low += open_shares * (low - prev_low)
				current_high += open_shares * (high - prev_high)
				if current_low < low_dollars: low_dollars = current_low
				if current_high > high_dollars: high_dollars = current_high
				prev_high = high
				prev_low = low
				if pnl_dollars > high_dollars: high_dollars = pnl_dollars
				if pnl_dollars < low_dollars: low_dollars = pnl_dollars
			pnl_percent = ((pnl_dollars / size_dollars)) * 100
			pnl_account = ((pnl_dollars / account_size)) * 100
			min_account = (low_dollars / account_size - 1)*100
			risk_percent = ( trade_open_price / lod_price - 1) * 100 * direction
			max_percent = ((high_price / trade_open_price) - 1) * 100 * direction
			min_percent = ((low_price / trade_open_price) - 1) * 100 * direction
			max_account = (high_dollars / account_size) * 100
			min_account = (low_dollars / account_size) * 100
			miss_percent = max_percent - pnl_percent
			if pnl_percent < min_percent: min_percent = pnl_percent
		else:
			risk_percent = pd.NA
			min_percent = pd.NA
			min_account = pd.NA
			min_time = pd.NA
			max_time = pd.NA
			max_account = pd.NA
			max_percent = pd.NA
			miss_percent = pd.NA
			pnl_percent = ((pnl_dollars / size_dollars)) * 100
			pnl_account = ((pnl_dollars / account_size)) * 100
		def try_round(v):
			try: return round(v,2)
			except: return v
		traits = pd.DataFrame({
		'ticker': [ticker], 'datetime':[open_datetime], 'trades': [trades], 'setup':[setup], 'pnl $':[try_round(pnl_dollars)], 
		'pnl %':[try_round(pnl_percent)], 'pnl a':[try_round(pnl_account)], 'size $':[try_round(size_dollars)], 'size %':[try_round(size_percent)],  
		'max %':[try_round(max_percent)], 'max time':[max_time],'max a':[try_round(max_account)],'miss %':[try_round(miss_percent)],
	   'risk %':[try_round(risk_percent)], 'min %':[try_round(min_percent)], 'min time':[try_round(min_time)],'min a':[try_round(min_account)], 
	   'account_size':[account_size],'arrow_list':[arrow_list], 'closed':[try_round(closed)], 
	   'open':[0], 'high':[try_round(high_dollars)], 'low':[try_round(low_dollars)], 'close':[try_round(pnl_dollars)],'volume':[try_round(total_size)]})
		return traits

class Account:
	
	def account(self):
		if self.event == 'Recalc': 
			Account.calc(self,self.df_log)
			self.queued_recalcs = pd.DataFrame()
			try: os.remove('C:/Stocks/local/account/queued_recalcs.feather')
			except FileNotFoundError: pass
		else: self.pnl_chart_type = self.event
		Account.update(self)

	def update(self):
		if self.init:
			self.init = False
			self.pnl_chart_type = 'Trade'
			layout = [[sg.Image(key = '-CHART-')],
			[sg.Button('Trade'),sg.Button('Periodic Trade'),sg.Button('Real'),sg.Button('Periodic Real'),sg.Button('Recalc')],
			[sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]
			self.window = sg.Window('Account', layout,margins = (10,10),scaling=data.get_config('Account ui_scale'),finalize = True)
		if 'Trade' in self.pnl_chart_type:
			df = self.df_traits.set_index('datetime')[['open','high','low','close','volume']]
			if 'Periodic' not in self.pnl_chart_type:
				pc = 0
				for i in range(len(df)):
					v = df.iat[i,4]
					c = df.iat[i,3] + pc
					o = pc
					h = df.iat[i,1] + pc
					l = df.iat[i,2] + pc
					df.iloc[i] = [o,h,l,c,v]
					pc = c
		elif 'Real' in self.pnl_chart_type:
			df = self.df_pnl
			df = df.resample('d').apply({'open':'first','high':'max','low':'min','close':'last','volume':'sum' }).dropna()
			if 'Periodic' in self.pnl_chart_type:
				pc = 0
				for i in range(len(df)):
					c = df.iat[i,3] - pc
					v = df.iat[i,4]
					o = 0
					h = df.iat[i,1] - pc
					l = df.iat[i,2] - pc
					df.iloc[i] = [o,h,l,c,v]
					pc += c
		mpf.plot(df, type='candle', volume=True, style=mpf.make_mpf_style(marketcolors=mpf.make_marketcolors(up='g',down='r')), warn_too_much_data=100000,returnfig = True,
		figratio = (data.get_config('Account chart_aspect_ratio'),1),figscale=data.get_config('Account chart_size'), panel_ratios = (5,1), mav=(10,20), tight_layout = True)
		plt.savefig(pathlib.Path("C:/Stocks/local/account") / "pnl.png", bbox_inches='tight',dpi = data.get_config('Account chart_dpi'))
		bio1 = io.BytesIO()
		image = PIL.Image.open(r"C:\Stocks\local\account\pnl.png")
		image.save(bio1, format="PNG")
		self.window["-CHART-"].update(bio1.getvalue())
		self.window.maximize()
  
	def calc(self, added_logs = pd.DataFrame()):
		if added_logs.empty: added_logs = self.queued_recalcs
		added_logs = added_logs.sort_values(by='datetime',ascending = True).reset_index(drop = True)
		start_datetime = added_logs.iloc[0]['datetime']
		df = data.get(tf = '1min')
		index = data.findex(df,start_datetime) - 1
		prev_date = df.index[index]
		date_list = df[index:].index.to_list()
		df_list = []
		next_trade_date = added_logs.iloc[1]['datetime']
		log_index = 0
		if self.df_pnl.empty:
			pos = []
			pnl = 0
			deposits = 0
		else:
			if date_list[0] > self.df_pnl.index[-1]: index = len(self.df_pnl)
			else: index = data.findex(self.df_pnl,date_list[0]) 
			self.df_pnl = self.df_pnl[:index]
			bar = self.df_pnl.iloc[-1]
			open_positions_list = bar['positions'].split(',')
			open_shares_list = bar['shares'].split(',')
			pos = []
			for i in range(len(open_shares_list)):
				ticker = open_positions_list[i]
				if ticker != '':
					shares = float(open_shares_list[i])
					df = data.get(ticker,'1min',datetime.datetime.now())#needs to be fixed ebcause if df doesnt exist then it has to set df to price of aevrage which has to be calced zzzzzzzzzzzz
					if df.empty: df = 0
					pos.append([ticker,shares,df])
			pnl = bar['open']
			deposits = bar['deposits']
		pbar = tqdm(total=len(date_list))
		for i in range(len(date_list)):
			date = date_list[i]
			if i > 0: prev_date = date_list[i-1]
			pnlvol = 0
			pnlo = pnl
			pnll = pnlo
			pnlh = pnlo
			while date > next_trade_date:
				remove = False
				ticker = added_logs.iat[log_index,0]
				shares = added_logs.iat[log_index,2]
				price = added_logs.iat[log_index,3]
				if ticker == 'Deposit': deposits += price
				else:
					pos_index = None
					for i in range(len(pos)):
						if pos[i][0] == ticker:
							if not isinstance(pos[i][2], pd.DataFrame):
								prev_shares = pos[i][1]
								avg = pos[i][2]
								if shares / prev_shares > 0: pos[i][2] = ((avg*prev_shares) + (price*shares))/(prev_shares + shares)
								else:
									gosh = (price - avg) * (-shares)
									pnl += gosh
									if gosh > 0: pnlh += gosh
									else: pnll += gosh
							pos_index = i
							pos[i][1] += shares
							if pos[i][1] == 0: remove = True
					if pos_index == None:
						pos_index = len(pos)
						try:
							df = data.get(ticker,'1min')
							if df.empty: raise IndexError
							data.findex(df,date) + 1
						except IndexError: 
							df = price
						pos.append([ticker,shares,df])
					df = pos[pos_index][2]
					if isinstance(df, pd.DataFrame):
						ind = data.findex(df,prev_date)
						c1 = df.iat[ind,3]
						gosh = (c1 - price)*shares
						pnl += gosh
						if gosh > 0: pnlh += gosh
						else: pnll += gosh
					pnlvol += abs(shares*price)
					if remove: del pos[pos_index]
				log_index += 1
				if log_index >= len(added_logs): next_trade_date = datetime.datetime.now() + datetime.timedelta(days=100)
				else: next_trade_date = added_logs.iat[log_index,1]
			positions = ""
			god_shares = ""
			for i in range(len(pos)):
				ticker = pos[i][0]
				shares = pos[i][1]
				df = pos[i][2]
				if isinstance(df, pd.DataFrame):
					index = data.findex(df,date)
					prev_index = data.findex(df,prev_date)
					prevc = df.iat[prev_index,3]
					c = df.iat[index,3] 
					o = df.iat[index,0]
					h = df.iat[index,1]
					l = df.iat[index,2]
					pnl += (c - prevc) * shares
					ch = (h - prevc) * shares
					cl = (l - prevc) * shares
					if shares > 0:
						pnll += cl
						pnlh+= ch
					else:
						pnll += ch
						pnlh += cl
					pnlo += (o - prevc) * shares
				if i >= 1:
					positions += "," + (str(ticker))
					god_shares += "," + (str(shares))
				else:
					positions += str(ticker)
					god_shares += str(shares)
			add = pd.DataFrame({
				'datetime':[pd.Timestamp(date)],
				'open':[pnlo],
				'high':[pnlh],
				'low':[pnll],
				'close':[pnl],
				'volume':[pnlvol],
				'deposits':[deposits],
				'account':[deposits + pnl],
				'positions':[positions],
				'shares':[god_shares]
				}).set_index('datetime')
			df_list.append(add)
			pbar.update(1)
		pbar.close()
		df = pd.concat(df_list)
		df = pd.concat([self.df_pnl,df])
		df = df.sort_values(by='datetime', ascending = True)
		df.reset_index().to_feather(r"C:\Stocks\local\account\pnl.feather")
		self.df_pnl = df

class Plot:
	
	def plot(self):
		if self.event == 'Load': Plot.sort(self)
		elif self.event == 'Next' :
			if self.i == len(self.sorted_traits) - 1: self.i = 0
			else: self.i += 1
			Plot.preload(self)
		elif self.event == 'Prev':
			if self.i == 0: self.i = len(self.sorted_traits) - 1
			else: self.i -= 1
			Plot.preload(self)
		Plot.update(self)

	def update(self):
		trade_headings = ['Date             ','Shares   ','Price  ']
		trait_headings = ['setup','pnl $','pnl %','pnl a', 'max %','min %','miss %','risk %','size %']
		if self.init:
			Plot.sort(self)
			self.init = False
			c2 = [[sg.Image(key = '-IMAGE1-')], [sg.Image(key = '-IMAGE0-')]]
			c1 = [[sg.Image(key = '-IMAGE2-')], [(sg.Text(key = '-number-'))], 
				[sg.Table([],headings = trait_headings,num_rows = 1, key = '-trait_table-',auto_size_columns=True,justification='left', expand_y = False)],
				[sg.Table([],headings = trade_headings, key = '-trade_table-',auto_size_columns=True,justification='left',num_rows = 8, expand_y = False)],
				[sg.Button('Prev'),sg.Button('Next'),sg.Button('Load'),sg.InputText(key = '-input_sort-')],
				[sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]
			layout = [[sg.Column(c1), sg.VSeperator(), sg.Column(c2)],]
			self.window = sg.Window(self.menu, layout,margins = (10,10),scaling=data.get_config('Plot ui_scale'),finalize = True)
		bar = self.sorted_traits.iloc[self.i]
		trades = bar['trades']
		trade_table = [[datetime.datetime.strptime(trades[k][1], '%Y-%m-%d %H:%M:%S'),(float(trades[k][2])),float(trades[k][3])] for k in range(len(trades))]
		trait_table = [[bar[trait] for trait in trait_headings]]
		self.window["-number-"].update(str(f"{self.i + 1} of {len(self.sorted_traits)}"))
		self.window["-trait_table-"].update(trait_table)
		self.window["-trade_table-"].update(trade_table)
		for i in range(3):
			while True:
				try: 
					image = PIL.Image.open(f'C:/Stocks/local/account/charts/{i}_{self.i}.png')
					bio = io.BytesIO()
					image.save(bio, format="PNG")
					self.window[f'-IMAGE{i}-'].update(data = bio.getvalue())
				except (PIL.UnidentifiedImageError, FileNotFoundError, OSError, SyntaxError): pass
				else: break
		self.window.maximize()

	def preload(self):
		helper_list = list(range(len(self.sorted_traits))) + list(range(len(self.sorted_traits)))
		if self.i == 0: index_list = [0,1,-1,2,-2,3,-3,4,-4,5,-5,6,-6,7,-7,8,-8,9,-9]
		else: index_list = [self.i + 9, self.i - 9]
		arglist = [[helper_list[i],self.sorted_traits,False] for i in index_list if abs(i) < len(helper_list) ]
		self.pool.map_async(Plot.create,arglist)

	def sort(self):
		try:
			df = self.df_traits
			sort_val = None
			if not self.init:
				sort = self.values['-input_sort-']
				reqs = sort.split('&')
				if sort != "":
					for req in reqs :
						if '^' in req:
							sort_val = req.split('^')[1]
							if sort_val not in df.columns and sort_val != 'r': raise TimeoutError
						else:
							r = req.split('=')
							trait = r[0]
							if trait not in df.columns or len(r) == 1: raise TimeoutError
							val = r[1]
							if trait == 'annotation': df = df[df[trait].str.contrains(val)]
							else: df = df[df[trait] == val]
				if df.empty: raise TimeoutError
			if sort_val != None:
				if sort_val == 'r': df = df.sample(frac = 1)
				else: df = df.sort_values(sort_val, ascending = False)
			else:df = df.sort_values(by = 'datetime', ascending = True)
			self.sorted_traits = df
			self.i = 0
			if os.path.exists("C:/Stocks/local/account/charts"):
				while True:
					try:
						shutil.rmtree("C:/Stocks/local/account/charts")
						break
					except: pass
			os.mkdir("C:/Stocks/local/account/charts")
			Plot.preload(self)
		except TimeoutError: sg.Popup('no setups found')

	def create(bar):
		i = bar[0]
		df = bar[1]
		from_traits = bar[2]
		if from_traits: 
			tflist = ['d']
			source = 'Traits'
		else: 
			tflist = ['1min','h','d']
			source = 'Plot'
		trait_bar = df.iloc[i]
		ticker = trait_bar['ticker']
		dt = trait_bar['datetime']
		for ii in range(len(tflist)):
			if not from_traits: 
				p = pathlib.Path("C:/Stocks/local/account/charts") / (str(ii) + '_' + str(i)  + ".png")
				if os.path.exists(p): return
			else: p = 'C:/Stocks/local/account/trait.png'
			tf = tflist[ii]
			if tf == 'd': df1 = data.get(ticker,tf,dt,110,30)
			else: df1 = data.get(ticker,tf,dt,110,70)
			if df1.empty: 
				shutil.copy(r"C:\Stocks\sync\files\blank.png",p)
				continue
			datelist = []
			colorlist = []
			trades = []
			for k in range(len(df.iat[i,2])):
				date = datetime.datetime.strptime(df.iat[i,2][k][1], '%Y-%m-%d %H:%M:%S')
				if tf == 'd':
					date = date.date()
				val = float(df.iat[i,2][k][2])
				if val > 0:
					colorlist.append('g')
					add = pd.DataFrame({'Datetime':[df.iat[i,2][k][1]], 'Symbol':[df.iat[i,2][k][0]],'Action':"Buy",'Price':[float(df.iat[i,2][k][3])]})
					trades.append(add)
				else: colorlist.append('r')
				datelist.append(date)
			god = bar[1].iloc[i]['arrow_list']
			god = [list(x) for x in god]
			dfall= pd.DataFrame(god, columns=['Datetime', 'Price', 'Color', 'Marker'])
			dfall['Datetime'] = pd.to_datetime(dfall['Datetime'])
			dfall = dfall.sort_values('Datetime')
			colors = []
			dfsByColor = []
			for zz in range(len(dfall)):
				if(dfall.iloc[zz]['Color'] not in colors): colors.append(dfall.iloc[zz]['Color'])
			for yy in range(len(colors)):
				colordf = dfall.loc[dfall['Color'] == colors[yy]] 
				dfsByColor.append(colordf)
			startdate = dfall.iloc[0]['Datetime']
			enddate = dfall.iloc[-1]['Datetime']
			minmax = 300
			times = df1.index.to_list()
			timesdf = []
			for _ in range(len(df1)):
				nextTime = pd.DataFrame({ 'Datetime':[df1.index[_]]})
				timesdf.append(nextTime)
			mainindidf = pd.concat(timesdf).set_index('Datetime', drop=True)
			apds = [mpf.make_addplot(mainindidf)]
			for datafram in dfsByColor:
				datafram['Datetime'] = pd.to_datetime(datafram['Datetime'])
				tradelist = []
				for t in range(len(datafram)): 
					tradeTime = datafram.iloc[t]['Datetime']
					for q in range(len(times)):
						if(q+1 != len(times)):
							if(times[q+1] >= tradeTime):
								test = pd.DataFrame({'Datetime':[times[q]],'Marker':[datafram.iloc[t]['Marker']],'Price':[float(datafram.iloc[t]['Price'])]})
								tradelist.append(test)
								break
						else:
							test = pd.DataFrame({'Datetime':[times[q]],'Marker':[datafram.iloc[t]['Marker']],'Price':[float(datafram.iloc[t]['Price'])]})
							tradelist.append(test)
							break
				df2 = pd.concat(tradelist).reset_index(drop = True)
				df2['Datetime'] = pd.to_datetime(df2['Datetime'])
				df2 = df2.sort_values(by=['Datetime'])
				df2['TradeDate_count'] = df2.groupby("Datetime").cumcount() + 1
				newdf = (df2.pivot(index='Datetime', columns='TradeDate_count', values="Price").rename(columns="price{}".format).rename_axis(columns=None))
				series = mainindidf.merge(newdf, how='left', left_index=True, right_index=True)[newdf.columns]
				if series.isnull().values.all(axis=0)[0]:pass
				else: apds.append(mpf.make_addplot(series,type='scatter',markersize=50,alpha = .65,marker=datafram.iloc[0]['Marker'],edgecolors='black', color=datafram.iloc[0]['Color']))
			mc = mpf.make_marketcolors(up='g',down='r',wick ='inherit',edge='inherit',volume='inherit')
			s  = mpf.make_mpf_style(base_mpf_style= 'nightclouds',marketcolors=mc)
			_, axlist = mpf.plot(df1, type='candle', volume=True, title=str(f'{ticker} , {tf}'), style=s, warn_too_much_data=100000,returnfig = True,figratio = (data.get_config(f'{source} chart_aspect_ratio'),1),
			figscale=data.get_config(f'{source} chart_size'), panel_ratios = (5,1), tight_layout = True,axisoff = True,addplot=apds)
			ax = axlist[0]
			ax.set_yscale('log')
			ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
			plt.savefig(p, bbox_inches='tight',dpi = data.get_config(f'{source} chart_dpi')) 

if __name__ == '__main__':
	Run.run(Run)