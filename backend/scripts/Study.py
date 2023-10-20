import pandas as pd
import mplfinance as mpf
import PySimpleGUI as sg
import datetime
import matplotlib.ticker as mticker
from matplotlib import pyplot as plt
from multiprocessing.pool import Pool
import os, pathlib, shutil, math, PIL, io

class Study:

	def run(self,current):
		self.current = current
		if not self.current:
			self.sub_st_list = {}
			setups_df = pd.read_feather(r"local\study\historical_setups.feather")
			for st in data.get_setups_list():
				df = setups_df[setups_df['st'] == st]
				sub_st_list = [*set(df['sub_st'].to_list())]
				self.sub_st_list.update({st:[s for s in sub_st_list if s != st]})
		with Pool(int(data.get_config('Data cpu_cores'))) as self.pool:
			self.init = True
			self.filter(self)
			while True:
				self.event, self.values = self.window.read()
				if self.event in ['Yes','No']:
					if self.event == 'Yes': v = 1
					else: v = 0
					bar = self.setups_data.iloc[math.floor(self.i)]
					ticker = bar['ticker']
					dt = bar['dt']
					if data.is_pre_market(dt): dt = dt.replace(hour=9, minute=30)
					st = bar['st']
					data.add_setup(ticker,dt,st,v,1)
					self.event = 'Next'
				if self.event == 'Next' and (self.i < len(self.setups_data) - 1 or (self.i < len(self.setups_data) - .5 and not self.current)): 
					self.previ = self.i
					if self.current: self.i += 1
					else: self.i += .5
					self.update(self)
					self.window.refresh()
					self.preload(self)
				elif self.event == 'Prev' and self.i > 0: 
					self.previ = self.i
					if self.current: self.i -= 1
					else: self.i -= .5
					self.update(self)
				elif self.event == 'Load':
					self.previ = self.i 
					self.update(self)
					self.filter(self)
				if self.event == sg.WIN_CLOSED:
					self.previ = self.i
					self.update(self)
					self.window.close()

	def preload(self):
		preload_amount = 10
		if self.i == 0:
			if self.current: index_list = [float(i) for i in range(preload_amount)]
			else: index_list = [float(i/2) for i in range(preload_amount*2)]
		else: index_list = [preload_amount-1 + self.i]
		arglist = [[self.setups_data,i,self.current] for i in index_list if i < len(self.setups_data)]
		self.pool.map_async(self.plot,arglist)
		
	def filter(self):
		try:
			if self.current: 
				try: df = pd.read_feather(r"local\study\current_setups.feather").sort_values(by=['z'], ascending=False)
				except: raise Exception('No current setups found')
			else:
				df = pd.read_feather(r"local\study\historical_setups.feather")
				sort_by = None
				if not self.init:
					input_filter = self.values['-input_filter-']
					reqs = input_filter.split('&')
					if input_filter != "":
						for req in reqs:
							if '^' in req:
								sort_by = req.split('^')[1]
								if sort_by not in df.columns: raise TimeoutError
							else:
								r = req.split('=')
								trait = r[0]
								if trait not in df.columns or len(r) == 1: raise TimeoutError
								val = r[1]
								if 'annotation' in trait: df = df[df[trait].str.contains(val)]
								else: df = df[df[trait] == val]
				if sort_by != None: df = df.sort_values(by = [sort_by], ascending = False)
				else: df = df.sample(frac = 1)
			if df.empty: raise TimeoutError
			self.setups_data = df
			self.i = 0.0
			self.previ = None
			while os.path.exists("local/study/charts"):
				try:shutil.rmtree("local/study/charts")
				except: pass
			os.mkdir("local/study/charts")
			self.preload(self)
			self.update(self)
		except TimeoutError: sg.Popup('no setups found')

	def plot(bar):
		setups_data = bar[0]
		i = bar[1]
		current = bar[2]
		if int(i) != i: revealed = True
		else: revealed = False
		bar = setups_data.iloc[math.floor(i)]
		dt = data.format_date(bar['dt'])
		ticker = bar['ticker']
		st = bar['st']
		z = bar['z']
		tf = st.split('_')[0]
		tf_list = []
		if 'w' in tf or 'd' in tf or 'h' in tf:
			intraday = False
			req_tf = ['1min','h','d','w']
			for t in req_tf:
				if t in tf: tf_list.append(tf)
				else: tf_list.append(t)
		else:
			intraday == True
			if tf == '1min': tf_list = ['d','h','5min','1min']
			else: tf_list = ['d','h',tf,'1min']
		plt.rcParams.update({'font.size': 30})
		ii = len(tf_list)
		first_minute_high = 1
		first_minute_low = 1
		first_minute_close = 1
		first_minute_volume = 0
		s = mpf.make_mpf_style(base_mpf_style= 'nightclouds',marketcolors=mpf.make_marketcolors(up='g',down='r',wick ='inherit',edge='inherit',volume='inherit'))
		for tf in tf_list:
			p = pathlib.Path("local/study/charts") / f'{ii}_{i}.png'
			try:
				chart_size = 100
				if 'min' in tf: chart_offset = chart_size - 1
				else: chart_offset = 20
				if not revealed: chart_offset = 0
				df = data.get(ticker,tf,dt,chart_size,chart_offset)
				if df.empty: raise TimeoutError
				if not revealed and not intraday:
					if tf == '1min':
						open = df.iat[-1,0]
						first_minute_high = df.iat[-1,1]/open
						first_minute_low = df.iat[-1,2]/open
						first_minute_close = df.iat[-1,3]/open
						first_minute_volume = df.iat[-1,4]
					else:
						open = df.iat[-1,0]
						df.iat[-1,1] = open * first_minute_high
						df.iat[-1,2] = open * first_minute_low
						df.iat[-1,3] = open * first_minute_close
						df.iat[-1,4] = first_minute_volume
				if (current or revealed) and ii == 1: title = f'{ticker} {dt} {st} {z} {tf}' 
				else: title = str(tf)
				#if revealed: _, axlist = mpf.plot(df, type='candle', axisoff=True,volume=True, style=s, returnfig = True, title = title, figratio = (data.get_config('Study chart_aspect_ratio'),1),figscale=data.get_config('Study chart_size'), panel_ratios = (5,1), mav=(10,20), tight_layout = True,vlines=dict(vlines=[dt], alpha = .25))
				#else: _, axlist =  mpf.plot(df, type='candle', volume=True,axisoff=True,style=s, returnfig = True, title = title, figratio = (data.get_config('Study chart_aspect_ratio'),1),figscale=data.get_config('Study chart_size'), panel_ratios = (5,1), mav=(10,20), tight_layout = True)
				if revealed: _, axlist = mpf.plot(df, type='candle', axisoff=True,volume=True, style=s, returnfig = True, title = title, figratio = (data.get_config('Study chart_aspect_ratio'),1),figscale=data.get_config('Study chart_size'), panel_ratios = (5,1),  tight_layout = True,vlines=dict(vlines=[dt], alpha = .25))
				else: _, axlist =  mpf.plot(df, type='candle', volume=True,axisoff=True,style=s, returnfig = True, title = title, figratio = (data.get_config('Study chart_aspect_ratio'),1),figscale=data.get_config('Study chart_size'), panel_ratios = (5,1),  tight_layout = True)
				
				ax = axlist[0]
				ax.set_yscale('log')
				ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
				plt.savefig(p, bbox_inches='tight',dpi = data.get_config('Study chart_dpi'))
			except: shutil.copy(r"sync\files\blank.png",p)
			ii -= 1

	def update(self):
		if self.init:
			sg.theme('Black')
			layout = [[sg.Image(key = '-chart1-'),sg.Image(key = '-chart2-')],
			[sg.Image(key = '-chart3-'),sg.Image(key = '-chart4-')],
			[(sg.Text(key = '-counter-'))]]
			if self.current: layout += [[sg.Button('Prev'), sg.Button('Next')]]
			#if self.current: layout += [[sg.Button('Prev'), sg.Button('Next'), sg.Button('Yes'),sg.Button('No')]]
			else: 
				df = pd.read_feather(r"local\study\historical_setups.feather")
				self.annotated = len(df[df['pre_annotation'] != ''])
				layout += [[sg.Multiline(size=(150, 5), key='-annotation-')],[sg.Combo([],key = '-sub_st-', size = (20,10))],[sg.Button('Prev'), sg.Button('Next'),sg.Button('Yes'),sg.Button('No'),sg.Button('Load'),sg.InputText(key = '-input_filter-'),sg.Text(key='annotated')]]
			self.window = sg.Window('Study', layout,margins = (10,10),scaling = data.get_config('Study ui_scale'),finalize = True)
			self.init = False
		for i in range(1,5):
			while True:
				try: 
					image = PIL.Image.open(f'local\study\charts\{i}_{self.i}.png')
					bio = io.BytesIO()
					image.save(bio,format="PNG")
					self.window[f'-chart{i}-'].update(data = bio.getvalue())
					break
				except (PIL.UnidentifiedImageError, FileNotFoundError, OSError): pass
		self.window['-counter-'].update(str(f"{math.floor(self.i + 1)} of {len(self.setups_data)}"))
		if not self.current:
			if self.previ != None:
				df = pd.read_feather(r"local\study\historical_setups.feather")
				annotation = self.values["-annotation-"]
				sub_st = self.values['-sub_st-']
				st = self.setups_data.iloc[math.floor(self.i)]['st']
				if sub_st != st and sub_st not in self.sub_st_list[st]: self.sub_st_list[st].append(sub_st)
				if int(self.previ) == self.previ: col = 'pre_annotation'
				else: col = 'post_annotation'
				index = self.setups_data.index[math.floor(self.previ)]
				self.setups_data.at[index, col] = annotation
				df.at[index, col] = annotation
				self.setups_data.at[index,'sub_st'] = sub_st
				df.at[index,'sub_st'] = sub_st
				df.to_feather(r"local\study\historical_setups.feather")
			if int(self.i) == self.i: 
				self.annotated += 1
				self.window['annotated'].update(str(self.annotated))
				col = 'pre_annotation'
			else: col = 'post_annotation'
			bar = self.setups_data.iloc[math.floor(self.i)]
			self.window["-annotation-"].update(bar[col])
			ss = list(self.sub_st_list[bar['st']])
			self.window['-sub_st-'].update(values = ss, value = bar['sub_st'])
		self.window.maximize()
		




class Screener:

	def run(dt = None, ticker = None, tf = 'd',browser = None, fpath = None):
		with Pool() as pool:
			dt = main.format_date(dt)
			path = 0
			if ticker == None:
				if dt == None: 
					path = 0
					ticker_list = Screener.get('full')
				else:
					if 'd' in tf or 'w' in tf: 
						ticker_list, browser = Screener.get('current',False,browser)#
						path = 1
					else: 
						ticker_list, browser = Screener.get('intraday',False,browser)#
						path = 2
			else:
				path = 1
				if not isinstance(ticker,list): ticker = [ticker]
				ticker_list = ticker
			if fpath != None: path = fpath
			if path == 1: 
				try: os.remove(r"local\study\current_setups.feather")
				except FileNotFoundError: pass
			df = pd.DataFrame()
			df['ticker'] = ticker_list
			df['dt'] = dt
			df['tf'] = tf
			st = main.get_config('Screener active_setup_list').split(',')
			setups = main.score_dataset(df,st)
			for ticker, dt, st, score in setups:
				if path == 3: print(f'{ticker} {dt} {score} {st}')
				elif path == 2:
					mpf.plot(df[-100:], type='candle', mav=(10, 20), volume=True, title=f'{ticker}, {st}, {score}, {tf}', style=mpf.make_mpf_style(marketcolors=mpf.make_marketcolors(up='g',down='r')), savefig = pathlib.Path("local/screener")/ 'intraday.png')
					Discord(url="https://discord.com/api/webhooks/1071667193709858847/qwHcqShmotkEPkml8BSMTTnSp38xL1-bw9ESFRhBe5jPB9o5wcE9oikfAbt-EKEt7d3c").post(file={"intraday": open('local/screener/intraday.png', "rb")})
				elif path == 1:
					d = r"local\study\current_setups.feather"
					try: setups = pd.read_feather(d)
					except: setups = pd.DataFrame()
					setups = pd.concat([setups,pd.DataFrame({'ticker': [ticker],'dt':[dt],'st': [st],'z':[score]})]).reset_index(drop = True)
					setups.to_feather(d)
				elif path == 0:
					d = r"local\study\historical_setups.feather"
					try: setups = pd.read_feather(d)
					except: setups = pd.DataFrame()
					setups = pd.concat([setups,pd.DataFrame({'ticker':[ticker], 'dt': [dt],'st': [st], 'z': [score], 'sub_st':[st], 'pre_annotation': [""], 'post_annotation': [""] })]) .reset_index(drop = True)
					setups.to_feather(d)

	def get(type = 'full', refresh = False, browser = None):

		def start_firefox():
			options = webdriver.FirefoxOptions()
			options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
			#options.headless = True##
			service = Service(executable_path=os.path.join(os.getcwd(), 'Drivers', 'geckodriver.exe'))
			FireFoxProfile = webdriver.FirefoxProfile()
			FireFoxProfile.set_preference("General.useragent.override", 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0')
			browser = webdriver.Firefox(options=options, service=service)
			browser.implicitly_wait(7)
			browser.set_window_size(2560, 1440)
			browser.get("https://www.tradingview.com/screener/")
			time.sleep(1.5)
			browser.find_element(By.XPATH, '//button[@aria-label="Open user menu"]').click()
			time.sleep(1)
			browser.find_element(By.XPATH, '//button[@data-name="header-user-menu-sign-in"]').click()
			time.sleep(1)
			browser.find_element(By.XPATH, '//button[@class="emailButton-nKAw8Hvt light-button-bYDQcOkp with-start-icon-bYDQcOkp variant-secondary-bYDQcOkp color-gray-bYDQcOkp size-medium-bYDQcOkp typography-regular16px-bYDQcOkp"]').click()
			browser.find_element(By.XPATH, '//input[@name="id_username"]').send_keys("cs.benliu@gmail.com")
			time.sleep(0.5)
			browser.find_element(By.XPATH, '//input[@name="id_password"]').send_keys("tltShort!1")
			time.sleep(0.5)
			browser.find_element(By.XPATH, '//button[@class="submitButton-LQwxK8Bm button-D4RPB3ZC size-large-D4RPB3ZC color-brand-D4RPB3ZC variant-primary-D4RPB3ZC stretch-D4RPB3ZC apply-overflow-tooltip apply-overflow-tooltip--check-children-recursively apply-overflow-tooltip--allow-text"]').click()
			time.sleep(3)
			browser.refresh()
			time.sleep(5)
			browser.find_element(By.XPATH, '//div[@data-name="screener-field-sets"]').click()
			time.sleep(0.1)
			browser.find_element(By.XPATH, '//div[@title="Python Screener"]').click()
			filter_tab = browser.find_element(By.XPATH, '//div[@class="tv-screener-sticky-header-wrapper__fields-button-wrap"]')
			try: filter_tab.click()
			except: pass
			time.sleep(0.5)
			browser.find_element(By.XPATH, '//div[@class="tv-screener__standalone-title-wrap"]').click()
			time.sleep(0.5) 
			browser.find_element(By.XPATH, '//div[@data-name="screener-filter-sets"]').click()
			time.sleep(0.25)
			browser.find_element(By.XPATH, '//span[@class="js-filter-set-name"]').click()
			time.sleep(0.25)
			browser.find_element(By.XPATH, '//div[@data-field="relative_volume_intraday.5"]').click()
			return browser

		def get_full(refresh):
			df1 = pd.read_feather("sync/files/full_scan.feather")
			if not refresh: return df1['ticker'].tolist()
			df2 = pd.read_feather("sync/files/current_scan.feather")
			df3 = pd.concat([df1,df2]).drop_duplicates(subset = ['ticker'])		
			not_in_current = (pd.concat([df3,df2]).drop_duplicates(subset = ['ticker'],keep = False))['ticker'].tolist()
			removelist = []
			for ticker in not_in_current:
				if pd.isna(ticker) or not os.path.exists('local/data/1min/' + ticker + '.feather'):
					removelist.append(ticker)
			df3 = df3.set_index('ticker',drop = True)
			df3.drop(removelist, inplace = True)
			df3 = df3.reset_index()
			df3.to_feather("sync/files/full_scan.feather")
			return df3['ticker'].tolist()

		def get_current(refresh,browser = None):
			if not refresh:
				try: return pd.read_feather("sync/files/current_scan.feather")['ticker'].tolist(), browser
				except FileNotFoundError: pass
			try:
				if browser == None: browser = start_firefox()
				time.sleep(0.5) 
				browser.find_element(By.XPATH, '//div[@data-name="screener-filter-sets"]').click()
				time.sleep(0.25)
				browser.find_element(By.XPATH, '//span[@class="js-filter-set-name"]').click()
				time.sleep(0.25)
				browser.find_element(By.XPATH, '//div[@data-field="relative_volume_intraday.5"]').click()
				browser.find_element(By.XPATH, '//div[@data-name="screener-export-data"]').click()
			except Exception as e: 
				print(e)
				print('manual csv fetch required')
			found = False
			today = str(datetime.date.today())
			while True:
				path = r'C:/Downloads/'
				dir_list = os.listdir(path)
				for direct in dir_list:
					if today in direct:
						downloaded_file = path + direct
						found = True
						time.sleep(1)
						break
				if found:
					break
			df = pd.read_csv(downloaded_file)
			os.remove(downloaded_file)
			for i in range(len(df)-1,-1,-1):
				bar = df.loc[i]
				ticker = bar['Ticker']
				if  isinstance(ticker,str) and '.' not in ticker and '/' not in ticker and not ticker == 'nan':
					if str(bar['Exchange']) == "NYSE ARCA": df.at[i,'Exchange'] = "AMEX"
				else: df = df.drop(i)
			df = df.drop('Description', axis = 1)
			df = df.fillna(0)
			df = df.rename(columns={'Ticker':'ticker','Exchange':'exchange','Pre-market Change':'pm change','Pre-market Volume':'pm volume','Relative Volume at Time':'rvol'})
			df = df.reset_index(drop = True)
			df.to_feather(r"sync\files\current_scan.feather")
			return df['ticker'].tolist() , browser

		def get_intraday(browser = None):
			while True:
				try:
					get_current(True,browser)
					df = pd.read_feather("sync/files/current_scan.feather")
					break
				except (selenium.common.exceptions.NoSuchElementException, AttributeError):
					try: browser.find_element(By.XPATH, '//button[@class="close-button-FuMQAaGA closeButton-zCsHEeYj defaultClose-zCsHEeYj"]').click()
					except (selenium.common.exceptions.NoSuchElementException, AttributeError): pass
			df = df.sort_values('rvol', ascending = False)
			df = df[:100].reset_index(drop = True)
			return df['ticker'].tolist(), browser

		if type == 'full': return get_full(refresh)
		elif type == 'current': return get_current(refresh,browser)
		elif type == 'intraday': return get_intraday(browser)

if __name__ == '__main__':
	if datetime.datetime.now().hour == 9:    
		Screener.run('current',fpath = 3)
		Screener.show(Screener)
	else:
		Screener.show(Screener)
	