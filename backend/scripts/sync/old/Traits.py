

from Data7 import Data as data
import pandas as pd
import matplotlib as mpl
import mplfinance as mpf
from multiprocessing.pool import Pool
from matplotlib import pyplot as plt
import PySimpleGUI as sg
import matplotlib.ticker as mticker
import datetime
from PIL import Image
import io
import pathlib
import shutil
import os
import numpy as np
import statistics
from tqdm import tqdm
from Data7 import Data as data
import scipy
from sklearn.metrics import r2_score

from Plot import Plot as plot

class Traits:

    def update(bars,df_log,df_traits,df_pnl):
        if not df_traits.empty:
            for bar in bars:
                ticker = bar[0]
                date = bar[1]
                df_traits = df_traits[df_traits['ticker'] != ticker]
                #df_traits = df_traits[df_traits['ticker'] != ticker || df_traits['datetime'] >= date]



                '''
            
                df = df_traits
                df['index'] = df.index
           
                df =df.set_index('datetime',drop = True)
                df = df[df['ticker'] == ticker]
                   
                   
                if not df.empty:
                    cutoff = 0  
                    for i in range(len(df)):
                        if df.index[i] <= date:
                            cutoff = i
                            break
                
                    drop_list = df.reset_index()[:cutoff+1]['index'].to_list()
                    i = df.iloc[cutoff]['index']
                    gosh = df_traits.iloc[i].to_list()
                    df_traits = df_traits.drop(index = drop_list)

                    '''

       


        new_traits = Traits.get_list(df_log)

        old_traits = df_traits

    
        new = pd.concat([old_traits,new_traits]).drop_duplicates('datetime',keep=False)

        new = new.sort_values(by='datetime', ascending = False)


   


        df = Traits.calc(new,df_pnl)
        
        
        df_traits = pd.concat([df_traits,df])
        df_traits = df_traits.sort_values(by='datetime',ascending = False).reset_index(drop = True)
        df_traits.to_feather(r"C:\Screener\sync\traits.feather")
     
        return df_traits






        if bars == 'open':
            bars = ['open']



        pbar = tqdm(total=len(bars))
        for bar in bars:

          



            df_log = df_log.sort_values(by='datetime', ascending = True)
            if bar == 'open':
                open_pos = df_traits[df_traits['closed'] == False]
                tickers = open_pos['ticker'].to_list()
                dates = open_pos['datetime'].to_list()
            else:
                dates = [bar[1]]
                tickers = [bar[0]]
         
            for i in range(len(tickers)):
                ticker = tickers[i]
                date = dates[i]
               
                if ticker != 'Deposit':

                    #find all trades with same ticker and greater than or equal to date
                    df = df_traits
                    df['index'] = df.index
           
                    df =df.set_index('datetime',drop = True)
                    df = df[df['ticker'] == ticker]
                   
                   
                    if not df.empty:
                        cutoff = 0
        
                      
                     
                        for i in range(len(df)):
                            if df.index[i] <= date:
                                cutoff = i
                                break
                
                        drop_list = df.reset_index()[:cutoff+1]['index'].to_list()
                        i = df.iloc[cutoff]['index']
                        gosh = df_traits.iloc[i].to_list()
                        df_traits = df_traits.drop(index = drop_list)
                        ticker = gosh[0]
                        log_date = gosh[1]
                        if log_date > date:
                            log_date = date

                    else:
                        log_date = date

                    logs = df_log
                
                 
                    short_logs = logs[logs['ticker'] == ticker]
                    short_logs = short_logs[short_logs['datetime'] >= log_date]
                    short_logs = short_logs.reset_index(drop = True)
 
                    df = Traits.calc(short_logs,df_pnl)
               
                    df_traits = pd.concat([df_traits,df])
                    df_traits = df_traits.sort_values(by='datetime',ascending = False).reset_index(drop = True)
            pbar.update(1)
        df_traits.to_feather(r"C:\Screener\sync\traits.feather")
        return df_traits
 


    def get_list(df_log):



        pos = []
        df_traits = pd.DataFrame()
       
        for k in range(len(df_log)):
            row = df_log.iloc[k].to_list()
            ticker = row[0]
            if ticker != 'Deposit':
                shares = row[2]
                date = row[1]
                index = None
                for i in range(len(pos)):
                    if pos[i][0] == ticker:
                        index = i
                        break
                if index != None:
                    prev_share = pos[index][2]
                else:
                    prev_share = 0
                    pos.append([ticker,date,shares,[]])
                    index = len(pos) - 1
                pos[index][3].append([str(x) for x in row])
                shares = prev_share + shares
                if shares == 0:
                    for i in range(len(pos)):
                        if pos[i][0] == ticker:
                            index = i
                            bar = pos[i]
                            add = pd.DataFrame({
                            'ticker': [bar[0]],
                            'datetime':[bar[1]],
                            'trades': [bar[3]]
                            })
                            df_traits = pd.concat([df_traits,add])
                            del pos[i]
                            break
                else:
                    pos[index][2] = shares
     
        for i in range(len(pos)-1,-1,-1):
            index = i
            bar = pos[i]
            add = pd.DataFrame({
            'ticker': [bar[0]],
            'datetime':[bar[1]],
            'trades': [bar[3]]
            })
            df_traits = pd.concat([df_traits,add])
            del pos[i]
        df = df_traits

        return df



    def calc(df_traits,df_pnl):

#trades///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        
        
        if not df_traits.empty:
            df_traits = df_traits.sort_values(by='datetime', ascending = False).reset_index(drop = True)


     

    #traits///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

      
            #pbar = tqdm(total=len(df_traits))
            df_vix = data.get('^VIX','d')
            df_qqq = data.get('QQQ','d')
            arg_list = []
        
            for i in range(len(df_traits)):
                bar = df_traits.iloc[i]
                
                arg_list.append([bar,df_pnl,df_vix,df_qqq])

            if len(arg_list) > 30:
                df_list = data.pool(Traits.trait_calc,arg_list)
            else:
                df_list = []
                for i in range(len(arg_list)):
                    df_list.append(Traits.trait_calc(arg_list[i]))


            try:
                df = pd.concat(df_list)
                df = df.reset_index(drop = True).sort_values(by='datetime',ascending = False)
            except:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
        return df



    def trait_calc(pack):
        bar = pack[0]
        df_pnl = pack[1]
        df_vix = pack[2]
        df_qqq = pack[3]
        #for k in range(len(df_traits)):
            
        #unpack row
        #bar = df_traits.iloc[k]
        ticker = bar[0]
        date = bar[1]
        trades = bar[2]
       
        openprice = float(trades[0][3])
        lastdate = datetime.datetime.strptime(trades[-1][1],'%Y-%m-%d %H:%M:%S')

        #try to pull dfs

        if (datetime.datetime.now() - lastdate).days > 10:
            acnt = False
        else:
            acnt = True

        run = False
        try:
            df_1min = data.get(ticker,'1min',account = acnt)
            hourly = data.get(ticker,'h',account = acnt)
            daily = data.get(ticker,'d',account = acnt)
            startd = data.findex(daily,date)
            start = data.findex(hourly,date)
            open_date = daily.index[data.findex(daily,date)]
            recent_price = df_1min.iat[-1,3]
            if startd != None and start != None:
                run = True
        except:
            recent_price = float(trades[-1][3])

        ###direction
        if float(trades[0][2]) > 0:
            direction = 1
        else: 
            direction = -1

        #main trades iterator
        trade_pnl = 0
        maxshares = sum([abs(float(s)) for d,d,s,d,d in trades])/2
        maxshares = maxshares * direction
         
        fb = float(trades[0][3])  *   maxshares
        pnl = -fb 
     
        buys = 0
        fs = None
        arrow_list = []
        trade_setup = 'None'
        size = 0
        maxsize = 0
        shg = 0
        total_size = 0
        pnl_high = -10000000000
        pnl_low = 1000000000000
            
            

        for i in range(len(trades)):
            sdate = trades[i][1]
            sh = float(trades[i][2])
            price = float(trades[i][3])
            setup = trades[i][4]
            dollars = price * sh

            #total size
            total_size += abs(dollars)

            #maxsize
            size += dollars
            shg += sh
            if abs(size) > abs(maxsize):
                maxsize = (size)
                

            #setup
            if  setup != 'None' and "":
                trade_setup = setup

            #arrow list
            if sh > 0:
                color = 'g'
                symbol = '^'
            else:
                color = 'r'
                symbol = 'v'
            arrow_list.append([str(sdate),str(price),str(color),str(symbol)])
                    
            #first buy first sell calc
            if sh*direction > 0:
                last_open_date = datetime.datetime.strptime(trades[i][1],'%Y-%m-%d %H:%M:%S')
            if dollars*direction < 0:
                if fs == None:
                    fs = price
                pnl -= dollars
            else:
                buys -= dollars

            #pnl
            trade_pnl -= dollars


            #ohlc if no data
            if not run:
                pnlc = trade_pnl + price * shg
                if pnlc < pnl_low:
                    pnl_low = pnlc
                if pnlc > pnl_high:
                    pnl_high = pnlc

                
        
        try:
            account_val = df_pnl.iloc[data.findex(df_pnl,date)]['account']
        except:
            try:
                account_val = df_pnl.iloc[-1]['account']
            except:
                account_val = 10000

        maxloss = -2
        if shg != 0:
            closed = False
            if not run:
                  
                trade_pnl += recent_price * shg
                pnl_pcnt = ((trade_pnl / abs(maxsize)) ) *100
                pnl_account = (trade_pnl/ account_val ) * 100
        else:
            closed = True
            pnl_pcnt = ((trade_pnl / abs(maxsize)) ) *100
            pnl_account = (trade_pnl/ account_val ) * 100
            if pnl_pcnt < maxloss:
                maxloss = pnl_pcnt
        if closed:
            fbuy = (pnl/fb) * 100 * direction
            fsell = (fs*maxshares + buys)/maxsize * 100 * direction
            rfsell = fsell - pnl_pcnt
            rfbuy = fbuy - pnl_pcnt
        else:
            fbuy = pd.NA
            fsell = pd.NA
            rfsell = pd.NA
            rfbuy = pd.NA
            
        size = maxsize
        h10 = pd.NA
        h20 = pd.NA
        h50 = pd.NA
        d5 = pd.NA
        d10 = pd.NA
        h10time = pd.NA
        h20time = pd.NA
        h50time = pd.NA
        d5time = pd.NA
        d10time = pd.NA

        #vix
        try:
            ivix = data.findex(df_vix,date)
            vix = df_vix.iat[ivix,0]
        except:
            vix = 0

            
            

#if there is data////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        if run:

            #qqq traits
            iqqq = data.findex(df_qqq,date)
            ma = []
            for i in range(51):
                ma.append(df_qqq.iat[iqqq+i-50,3])
                if i == 49:
                    ma50 = statistics.mean(ma)
            m50 = (statistics.mean(ma[-50:])/ma50 - 1) * 100


            #theoretical or1 entry and max amount down after trade
                
            open_index = data.findex(df_1min,open_date)
            low = 1000000000*direction
            entered = False
            i = open_index
            stopped = False
            stop = ((maxloss/100)*direction + 1) * openprice
            stopdate = datetime.datetime.now() + datetime.timedelta(days = 100)
            max_days = 3
            before_max = True
                
            shares = 0

            nex = date
            trade_index = 0
            pnl = 0
            pnl_low = 10000000
            pnl_high = -1000000
            exit = False
            while True:
                    
                #stop and risk
                if i >= len(df_1min) or (exit and not before_max and closed):
                    break
                if direction > 0:
                    clow = df_1min.iat[i,2] 
                else:
                    clow = df_1min.iat[i,1] 
                cdate = df_1min.index[i]
                if  (cdate - date).days > max_days or i - open_index > 390*max_days :
                    before_max = False
                if clow*direction < low*direction and before_max:
                    low = clow
                if cdate >= date and not entered:
                    entered = True
                    risk = (direction*(low - openprice))/openprice * 100
                    low = 1000000000*direction
                if cdate > last_open_date and  direction*clow < stop*direction and not stopped:
                    stopped = True
                    copen = df_1min.iat[i,0]
                    if direction*copen < direction*stop:
                        stop = copen
                    stopdate = df_1min.index[i+1]
                    arrow_list.append([str(stopdate),str(stop),'k',symbol]) 

                #pnl
                while cdate > nex:
                    sh = float(trades[trade_index][2])
                    price = float(trades[trade_index][3])
                    pnl += (df_1min.iat[i-1,3] - price)*sh
                    shares += sh
                    trade_index += 1
                    if trade_index >= len(trades):
                        nex = datetime.datetime.now() + datetime.timedelta(days=100)
                        exit = True
                    else:
                        nex = datetime.datetime.strptime(trades[trade_index][1],'%Y-%m-%d %H:%M:%S')

                index = data.findex(df_1min,cdate)
                prevc = df_1min.iat[index - 1,3]
                c = df_1min.iat[index,3] 
                h = df_1min.iat[index,1]
                l = df_1min.iat[index,2]
                pnlh =  pnl + (h - prevc) * shares
                pnll = pnl + (l - prevc) * shares
                pnl = pnl + (c - prevc) * shares
                if pnll < pnl_low:
                    pnl_low = pnll
                if pnlh > pnl_high:
                    pnl_high = pnlh

                i += 1
            
            if not closed:
                trade_pnl = pnl
                pnl_pcnt = ((trade_pnl / abs(maxsize)) ) *100
                pnl_account = (trade_pnl/ account_val ) * 100
            low = (direction*(low - openprice)/openprice) * 100

            #hourly exit calculator
            if direction > 0:
                symbol = 'v'
            else:
                symbol = '^'
            prices = []
            for i in range(50):
                prices.append(hourly.iat[i + start - 50,3])
            i = 0
            try:
                while True:
                    close = hourly.iat[start+i,3]
                    cdate = hourly.index[start + i] + datetime.timedelta(hours = 1)

                    if cdate > stopdate:
                        if pd.isna(h10):
                            h10 = maxloss
                            h10time = ( cdate- date).total_seconds() / 3600
                        if pd.isna(h20):
                            h20 = maxloss
                            h20time = (hourly.index[start + i + 1] - date).total_seconds() / 3600
                        if pd.isna(h50):
                            h50 = maxloss
                            h50time = (hourly.index[start + i + 1] - date).total_seconds() / 3600

                    if (not pd.isna(h20) and not pd.isna(h10) and pd.isna(h50)):
                        break

                    if direction * close < direction * statistics.mean(prices[-10:]) and pd.isna(h10):
                        h10 = direction*(close/openprice - 1)*100
                        h10time = ((hourly.index[start + i] - date)+datetime.timedelta(hours=1)).total_seconds() / 3600
                        arrow_list.append([str(cdate),str(close),'m',str(symbol)])
                    if direction * close < direction * statistics.mean(prices[-20:]) and pd.isna(h20):
                        h20 = direction*(close/openprice - 1)*100
                        h20time = ((hourly.index[start + i] - date)+datetime.timedelta(hours=1)).total_seconds() / 3600
                        arrow_list.append([str(cdate),str(close),'b',str(symbol)])
                    if direction * close < direction * statistics.mean(prices[-50:]) and pd.isna(h50):
                        h50 = direction*(close/openprice - 1)*100
                        h50time = ((hourly.index[start + i] - date)+datetime.timedelta(hours=1)).total_seconds() / 3600
                        arrow_list.append([str(cdate),str(close),'c',str(symbol)]) 

                    i += 1
                    if i + start >= len(hourly):
                        break
                    prices.append(hourly.iat[start + i,3])
            
            except:
                pass

            #daily exit calculator
            start = startd 
            prices = []
            for i in range(10):
                prices.append(daily.iat[i + start - 10,3])
            i = 0
            try:
                while True:
                    close = daily.iat[start+i,3]
                    cdate = daily.index[start + i ] + datetime.timedelta(days = 1)

                    if cdate > stopdate:
                        if pd.isna(d5):
                            d5 = maxloss
                            d5time = (daily.index[start+i+1] - date).total_seconds() / 3600
                        if pd.isna(d10):
                            d10 = maxloss
                            d10time = (daily.index[start+i+1] - date).total_seconds() / 3600

                    if (not pd.isna(d10) and not pd.isna(d5)):
                        break

                    if direction * close < direction * statistics.mean(prices[-5:]) and pd.isna(d5):
                        d5 = direction*(close/openprice - 1)*100
                        d5time = ((daily.index[start+i] - date)+datetime.timedelta(days=1)).total_seconds() / 3600
                        arrow_list.append([str(cdate),str(close),'y',str(symbol)])
                    if direction * close < direction * statistics.mean(prices[-10:]) and pd.isna(d10):
                        d10 = direction*(close/openprice - 1)*100
                        d10time = ((daily.index[start+i] - date)+datetime.timedelta(days=1)).total_seconds() / 3600
                        arrow_list.append([str(cdate),str(close),'w',str(symbol)])

                    i += 1
                    if i + start + 1 >= len(daily):
                        break
                    prices.append(daily.iat[start+i,3])

            except:
                pass

            #set theoretical exits to stop loss if they are lower than max stop
            '''
            if h10 < maxloss:
                h10 = maxloss
            if h20 < maxloss:
                h20 = maxloss
            if h50 < maxloss:
                h50 = maxloss
            if d5 < maxloss:
                d5 = maxloss
            if d10 < maxloss:
                d10 = maxloss
            '''
            #relative performance
            r10 = h10 - pnl_pcnt
            r20 = h20 - pnl_pcnt
            r50 = h50 - pnl_pcnt
            r5d = d5 - pnl_pcnt
            r10d = d10 - pnl_pcnt
            rfsell = fsell - pnl_pcnt
            rfbuy = fbuy - pnl_pcnt
                

                

        #if ticker doesnt have data then fill uncalcable traits
        else:
            h10  = pd.NA
            h20 = pd.NA
            h50 = pd.NA
            d5 = pd.NA
            d10 = pd.NA
            r10 = pd.NA
            r20 = pd.NA
            r50 = pd.NA
            r5d = pd.NA
            r10d = pd.NA
            d10time = pd.NA
            h10time  = pd.NA
            h20time = pd.NA
            h50time = pd.NA
            d5time = pd.NA
            low  = pd.NA
            risk  = pd.NA
            m50 = pd.NA
                
                
        try:
            gudddd = risk
        except:
            risk = pd.NA
      

        #final df row
        add = pd.DataFrame({
        'ticker': [ticker],
        'datetime':[date],
        
        'trades': [trades],
        'setup':[trade_setup],
        'pnl':[trade_pnl],
        'account':[pnl_account],
        'percent':[pnl_pcnt],
        'fsell':[fsell],
        'fbuy':[fbuy],
        'p10':[h10],
        'p20':[h20],
        'p50':[h50],
        'p5d':[d5],
        'p10d':[d10],
        'rpercent':[0],
        'rfsell':[rfsell],
        'rfbuy':[rfbuy],
        'r10':[r10],
        'r20':[r20],
        'r50':[r50],
        'r5d':[r5d],
        'r10d':[r10d],
        'vix':[vix], 
        'm50':[m50],
        'arrows':[arrow_list],
        'closed':[closed],
        't10d':[d10time],
        't20':[h20time],
        't10':[h10time],
        't50':[h50time],
        't5d':[d5time],
        'min':[low],
        'risk':[risk],
        'open':[0],
        'high':[pnl_high],
        'low':[pnl_low],
        'close':[trade_pnl],
        'volume':[total_size],
        })
        return add


    def build_monthly(self):

        df = self.df_traits
        g = df.groupby(pd.Grouper(key='datetime', freq='M'))
        # groups to a list of dataframes with list comprehension
        dfs = [group for _,group in g]


        god = []

        date = 'Overall'

        loss = df[df['account'] <= 0]
        avg_loss = loss['account'].mean()

        gain = df[df['account'] > 0]
        avg_gain = gain['account'].mean()

        wins = []
        for i in range(len(df)):
            if df.iloc[i]['account'] > 0:
                wins.append(1)
            else:
                wins.append(0)


        win = statistics.mean(wins) * 100

        pnl = ((df['account'] / 100) + 1).tolist()

        gud = 1
        for i in pnl:
            gud *= i

        pnl = gud

        trades = len(df)


        god.append([date,round(avg_gain,2), round(avg_loss,2), round(win,2), round(trades,2), round(pnl,2)])


        
        for df in dfs:
           
            date = str(df.iat[0,1])
      
            date = date[:-12]
         
            

            loss = df[df['account'] <= 0]
            avg_loss = loss['account'].mean()

            gain = df[df['account'] > 0]
            avg_gain = gain['account'].mean()

            wins = []
            for i in range(len(df)):
                if df.iloc[i]['account'] > 0:
                    wins.append(1)
                else:
                    wins.append(0)


            win = statistics.mean(wins) * 100

            trades = len(df)

            pnl = ((df['account'] / 100) + 1).tolist()

            gud = 1
            for i in pnl:
                gud *= i

            pnl = (gud - 1) *100

            god.append([date,round(avg_gain,2), round(avg_loss,2), round(win,2), round(trades,2), round(pnl,2)])

        

        
        return god


    def build_traits(self):


        traits = self.df_traits
        god = []


        traits_list = [6,7,8,9,10,11,12,13]

        for i in traits_list:

            t = traits.columns[i]
            tn = traits.columns[i+8]
            n = round(traits[t].mean(),2)
            r = round(traits[tn].mean(),2)
            god.append([t,n,r])


        self.traits_table = god

        return god


    def traits(self):
        print(self.event)
        '''
        pp = 0
        for i in range(len(self.df_log)):
            price = self.df_log.iat[i,3]
            shares = self.df_log.iat[i,2]
            dollars = price*shares
            pp -= dollars
        pint(pp)
        '''
        inp = False
       

        if self.df_traits.empty or self.event == 'Recalc':

            self.df_traits = pd.DataFrame()
            
            #df = self.df_log.sort_values(by='Datetime')
            self.df_log = self.df_log.sort_values(by='datetime', ascending = True)
            self.df_traits = Traits.update([],self.df_log,pd.DataFrame(),self.df_pnl)
            self.df_traits.to_feather(r"C:\Screener\sync\traits.feather")
        
      


        if '+CLICKED+' in self.event:
            if os.path.exists("C:/Screener/laptop.txt"): #if laptop
                size = (49,25)
            else:
                size = (25,10)
              
            c = self.event[2][1]

            if c == 0:
                return


            plt.clf()
    
            y = [p[5] for p in self.monthly[1:] if not np.isnan(p[c])]
            x = [p[c] for p in self.monthly[1:] if not np.isnan(p[c])]

            
            
            plt.scatter(x,y)
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x,p(x),"r--")

            plt.gcf().set_size_inches(size)
 
            string1 = "traits.png"
            p1 = pathlib.Path("C:/Screener/tmp/pnl") / string1
                
            plt.savefig(p1,bbox_inches='tight')
                
            bio1 = io.BytesIO()
            image1 = Image.open(r"C:\Screener\tmp\pnl\traits.png")
            image1.save(bio1, format="PNG")
            self.window["-CHART-"].update(data=bio1.getvalue())
                

        elif self.event == '-table_traits-':
                
            i = self.values['-table_traits-'][0]
            inp = self.traits_table[i][0]



        elif self.event == '-table_gainers-' or self.event == '-table_losers-':

            if self.event == '-table_gainers-':
                df = self.gainers
                i = self.values['-table_gainers-'][0]
            else:
                df = self.losers
                i = self.values['-table_losers-'][0]
                
               
            print('god')

            bar = [i,df,1]
            if os.path.exists("C:/Screener/tmp/pnl/charts"):
                shutil.rmtree("C:/Screener/tmp/pnl/charts")
            os.mkdir("C:/Screener/tmp/pnl/charts")
            plot.create(bar)
                
            bio1 = io.BytesIO()
            image1 = Image.open(f'C:/Screener/tmp/pnl/charts/{i}d.png')
            image1.save(bio1, format="PNG")
            self.window["-CHART-"].update(data=bio1.getvalue())


        elif self.event == 'Traits':

            inp = 'account'

            gainers2 = self.df_traits.sort_values(by = ['pnl'])[:10].reset_index(drop = True)

            gainers = pd.DataFrame()
           
            gainers['#'] = gainers2.index + 1
            gainers['Ticker'] = gainers2['ticker']
            gainers['$'] = gainers2['pnl'].round(2)

            losers2 = self.df_traits.sort_values(by = ['pnl'] , ascending = False)[:10].reset_index(drop = True)
            losers = pd.DataFrame()
            losers['#'] = losers2.index + 1
            losers['Ticker'] = losers2['ticker']
            losers['$'] = losers2['pnl'].round(2)


            self.losers = losers2
            self.gainers = gainers2


            self.monthly = Traits.build_monthly(self)

            traits = Traits.build_traits(self)


          

            self.window["-table_gainers-"].update(gainers.values.tolist())
            self.window["-table_losers-"].update(losers.values.tolist())
            self.window["-table_traits-"].update(traits)
            self.window["-table_monthly-"].update(self.monthly)


        
 
        if inp != False:
           
            bins = 50
            if os.path.exists("C:/Screener/laptop.txt"): #if laptop
                size = (49,25)
            else:
                size = (25,10)
        
            if inp == "":
                inp = 'p10'
       

            try:
                plt.clf()
                if ':'  in inp:
                    inp = inp.split(':')
                    inp1 = inp[0]
                    inp2 = inp[1]
                    x = self.df_traits[inp1].to_list()
                    y = self.df_traits[inp2].to_list()
                    plt.scatter(x,y)
                    z = np.polyfit(x, y, 1)
                    p = np.poly1d(z)
                    plt.plot(x,p(x),"r--")
                else:
                    fifty = self.df_traits[inp].dropna().to_list()
                    plt.hist(fifty, bins, alpha=1, ec='black',label='Percent') 
                plt.gcf().set_size_inches(size)
 
                string1 = "traits.png"
                p1 = pathlib.Path("C:/Screener/tmp/pnl") / string1
                
                plt.savefig(p1,bbox_inches='tight')
                
                bio1 = io.BytesIO()
                image1 = Image.open(r"C:\Screener\tmp\pnl\traits.png")
                image1.save(bio1, format="PNG")
                self.window["-CHART-"].update(data=bio1.getvalue())
            except:
                pass
      