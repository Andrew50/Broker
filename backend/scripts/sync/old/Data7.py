


from pyarrow import feather
from tqdm import tqdm
import pandas as pd
import datetime
from tvDatafeed import TvDatafeed, Interval
import os 
import datetime
import numpy

from multiprocessing  import Pool
import warnings
#from Create import Create as create

import yfinance as yf
import shutil
warnings.filterwarnings("ignore")
import Scan


class Data:


    path = ""
    if os.path.exists("F:/Screener/Ffile.txt"):
        path = "F:/Screener"
    else: 
        path = "C:/Screener"





    def pool(deff,arg,nodes = 5):
          
            pool = Pool(processes = nodes)
            data = list(tqdm(pool.imap(deff, arg), total=len(arg)))
            return(data)


 



    def convert_date(dt):
        if type(dt) == str:
            try:
                dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
            except:
                dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        if type(dt) == datetime.date:
            time = datetime.time(9,30,0)
            dt = datetime.datetime.combine(dt,time)
        if dt.time() == datetime.time(0):
            time = datetime.time(9,30,0)
            dt = datetime.datetime.combine(dt.date(),time)
        return(dt)






    def isToday(dt):
       
        if dt == 'now':
            return True
        if dt == None:
            return False
        if dt == 'Today' or dt == '0' or dt == 0:
            return True
        time = datetime.time(0,0,0)
        today = datetime.date.today()
        today = datetime.datetime.combine(today,time)
        dt = Data.convert_date(dt)
       
        if dt >= today:
            return True
        return False


    def findex(df,dt,order = 1):
     
        try:
            if dt == '0' or dt == 0:
                return len(df) - 1

            #if Data.isToday(dt):
           #     return len(df) - 1
             
            dt = Data.convert_date(dt)
        
            i = int(len(df)/2)
            k = i
           
            while True:
                k = int(k/2)
                date = df.index[i].to_pydatetime()
                if date > dt:
                    i -= k*order
                elif date < dt:
                    i += k*order
                if k == 0:
                    break
   
            while True:

                if df.index[i].to_pydatetime() < dt:
       
                    i += 1*order
                else:
                    break
            while True:
                if df.index[i].to_pydatetime() > dt:
                    i -= 1*order
                else:
                    break
            return i
        except IndexError:
        #except TimeoutError:
            if i >= len(df):
            #if i == len(df):
                #return i
                return len(df) - 1
           
            return None




    def get(ticker = 'AAPL',tf = 'd',date = None,premarket = False,account = False,old = False):    
        try:
            path = Data.path
            if account:
                date = 'now'

            current = Data.isToday(date)
          

            if tf == 'daily':
                tf = 'd'
            if tf == 'minute':
                tf = '1min'


            if account:# and 'd' not in tf and 'w' not in tf:
                
                try:
                   # if tf == 'd' or tf == 'w' or tf == 'm':
                 #       dff = feather.read_feather(r"" + path + "/daily/" + ticker + ".feather")
                    #fetch file
                  #  else:
                    dff = feather.read_feather(r"" + path + "/minute/" + ticker + ".feather")
                    dff = dff.between_time('09:30' , '15:59')

                    tvr = TvDatafeed(username="billingsandrewjohn@gmail.com",password="Steprapt04")
                    screener_data = feather.read_feather(r"C:\Screener\sync\full_ticker_list.feather")
                    screener_data.set_index('Ticker', inplace = True)
            
                    exchange = str(screener_data.loc[ticker]['Exchange'])
                    df = tvr.get_hist(ticker, exchange, interval=Interval.in_1_minute, n_bars=10000, extended_session = premarket)
                    df.drop('symbol', axis = 1, inplace = True)
                    df.index = df.index + pd.Timedelta(hours=4)
                    lastday = dff.index[-1]   
                    scrapped_data_index = Data.findex(df,lastday) 
                    if scrapped_data_index == None:     
                        pass     
                    else:    
                
                        df = df[scrapped_data_index + 1:]
                        df = pd.concat([dff,df])
                except:
                    df = dff
                
            else:
                if tf == 'd' or tf == 'w' or tf == 'm':
                    if ticker == "^VIX" or old:
                        df = feather.read_feather(r"" + path + "/daily/" + ticker + ".feather")
                    else:
                        #df = feather.read_feather(r"" + path + "/minute/" + ticker + ".feather")
                   
                        df = feather.read_feather(r"" + path + "/daily/" + ticker + ".feather")
                else:
                    if current and not (datetime.datetime.now().hour < 5 or (datetime.datetime.now().hour < 6 and datetime.datetime.now().minute < 30)):
                        
                        tvr = TvDatafeed(username="cs.benliu@gmail.com",password="tltShort!1")
                        screener_data = feather.read_feather(r"C:\Screener\sync\full_ticker_list.feather")
                        screener_data.set_index('Ticker', inplace = True)
                        exchange = str(screener_data.loc[ticker]['Exchange'])
                        df = tvr.get_hist(ticker, exchange, interval=Interval.in_1_minute, n_bars=10000, extended_session = premarket)
                        df.drop('symbol', axis = 1, inplace = True)
                        df.index = df.index + pd.Timedelta(hours=4)
                        seconds = datetime.datetime.now().second
                        bar = df.iloc[-1]
                        df.drop(df.tail(1).index,inplace = True)
                        if seconds > 30:
                            mult = pow((60 / seconds),.6)
                            openn = bar['open']
                            high = bar['high']
                            low = bar['low']
                            close = bar['close']
                            vol = bar['volume']
                            new_open = openn
                            new_close = close + (close - openn) * mult 
                            new_vol = vol*mult 
                            new_high = high
                            new_low = low
                            if new_close > high:
                                new_high = new_close
                            if new_close < low:
                                new_low = new_close
                            now = datetime.datetime.now()
                            new = pd.DataFrame({'datetime':[now],
                                                'open':[new_open],
                                                'high':[new_high],
                                                'low':[new_low],
                                                'close':[new_close],
                                                'volume':[new_vol]}).set_index("datetime")
                            df = pd.concat([df,new])
                    else:
                        df = feather.read_feather(r"" + path + "/minute/" + ticker + ".feather")
                        if not premarket:
                            df = df.between_time('09:30' , '15:59')
        
            if 'h' in tf:
                df.index = df.index + pd.Timedelta(minutes = -30)
            if (tf != '1min' and tf != 'd' ) or (account ):
                logic = {'open'  : 'first',
                            'high'  : 'max',
                            'low'   : 'min',
                            'close' : 'last',
                            'volume': 'sum' }
                df = df.resample(tf).apply(logic)
            if 'h' in tf:
                df.index = df.index + pd.Timedelta(minutes = 30)
            if current and not account:# and (datetime.datetime.now().hour < 5 or (datetime.datetime.now().hour < 6 and datetime.datetime.now().minute < 30)):
                
                screenbar = Scan.Scan.get('0','d').loc[ticker]
                pmchange =  screenbar['Pre-market Change']
                if numpy.isnan(pmchange):
                    pmchange = 0
                try:
                    pm = df.iat[-1,3] + pmchange
                    date = pd.Timestamp(datetime.datetime.today())
                    row  =pd.DataFrame({'datetime': [date],
                           'open': [pm],
                           'high': [pm],
                           'low': [pm],
                           'close': [pm],
                           'volume': [0]}).set_index("datetime")
                    df = pd.concat([df, row])
                    
                except IndexError:
                    
                    pass
            df.dropna(inplace = True)
            return (df)
        except TimeoutError:
            pass
    def update(bar):
        path = Data.path
        try:
            ticker = bar[0]
            lastDStock = bar[1]
            tf = bar[2]

            if ticker == None or "/" in ticker  or '.' in ticker:
                return

            exists = True
            try:
                cs = Data.get(ticker,tf)
                
                lastDay = cs.index[-1]
             
                if (lastDay == lastDStock):
                    return
            
            except: #df is empty or doesnt exist
                exists = False

            if tf == 'daily':
                ytf = '1d'
                period = '25y'
            else:
                ytf = '1m'
                period = '5d'
        
            ydf = yf.download(tickers =  ticker,  
                period = period,  group_by='ticker',      
                interval = ytf,      
                ignore_tz = True,  
                progress=False,
                show_errors = False,
                threads = False,
                prepost = False) 
        
        
            ydf = ydf.drop(axis=1, labels="Adj Close")
            ydf.rename(columns={'Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'}, inplace = True)
            if Data.isMarketOpen() == 1 :
                ydf.drop(ydf.tail(1).index,inplace=True)
            ydf.dropna(inplace = True)
            if not exists:
                df = ydf
          
            else:
 
                scrapped_data_index = Data.findex(ydf, lastDay) 
                if scrapped_data_index == None:
                    return
                ydf = ydf[scrapped_data_index + 1:]
                df = pd.concat([cs, ydf])

            df.index.rename('datetime', inplace = True)


            #testing function //////////
            #df.to_csv("C:/Screener/data_test/" + ticker + tf+".csv")
            feather.write_feather(df, path + "/"+tf+"/" + ticker + ".feather")
        except Exception as e:
            print(e)
            
    
    def runUpdate():
        tv = TvDatafeed()
        daily = tv.get_hist('NFLX', 'NASDAQ', n_bars=2)
        daily_last = daily.index[Data.isMarketOpen()]



        minute = tv.get_hist('NFLX', 'NASDAQ', n_bars=2, interval=Interval.in_1_minute, extended_session = False)

        
        minute_last = minute.index
        
        minute_last = minute_last[Data.isMarketOpen()]
       
        


        screener_data = Scan.Scan.get()
        
        
        #screener_data = pd.DataFrame({'Ticker': ['^VIX']
                               #       }).set_index('Ticker')
    
        batches = []
        for i in range(len(screener_data)):
           ticker = screener_data.index[i]
           batches.append([ticker, daily_last, 'daily'])
           batches.append([ticker, minute_last, 'minute'])
        
        
        Data.pool(Data.update, batches)

        from Create import Create as create
        from modelTest import modelTest
        
        #setup_list = ['EP', 'NEP' , 'P','NP' , 'MR' , 'F','NF']
        setup_list = create.get_setups_list()

        epochs = 200
        new = True
        prcnt_setup = .05
        

        if os.path.exists("C:/Screener/desktop.txt"):
            for s in setup_list:
                try:
                    modelTest.combine(new,s)

                    create.run(s,prcnt_setup,epochs,False)
                except:
                    print(s + ' failed')


            if datetime.datetime.now().weekday() == 4:
                Data.backup()
        


    def backup():
        print('backing up data')
        date = datetime.date.today()
        src = r'C:/Screener'
        dst = r'D:/Screener Backups/' + str(date)


        shutil.copytree(src, dst)



        path = "D:/Screener Backups/"

        dir_list = os.listdir(path)

        for b in dir_list:
            dt = datetime.datetime.strptime(b, '%Y-%m-%d')
            if (datetime.datetime.now() - dt).days > 30:
                shutil.rmtree((path + b))




    def isMarketOpen():
        dayOfWeek = datetime.datetime.now().weekday()
        if(dayOfWeek == 5 or dayOfWeek == 6):
            return 0
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        if(hour > 5 and hour < 12):
            return 1
        elif(hour == 5):
            if(minute >= 30):
                return 1
        elif(hour == 12):
            if(minute <= 15): 
                return 1
        
        return 0

    def isBen():
        if(os.path.exists("C:/Screener/ben.txt")):
            return True
        return False


    def isLaptop():
        if(os.path.exists("C:/Screener/laptop.txt")):
            return True
        return False


    def isTae():
        if(os.path.exists("C:/Screener/tae.txt")):
            return True
        return False

if __name__ == '__main__':
    #Data.backup()
  
    Data.runUpdate()
    






