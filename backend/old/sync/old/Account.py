
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
import numpy
import statistics
from tqdm import tqdm

from Traits import Traits as traits

class Account:

    def calcaccount(df_pnl,df_log,startdate = None,tf = None,bars = None,account_type = None, df_traits = None):

        if account_type == 'Trade':

            df = traits.update('open',df_log,df_traits,df_pnl)
            return [df,tf,bars,account_type]



        df_log = df_log.sort_values(by='datetime', ascending = True)



        #if date is a datetime object then it is coming from the log updater
        #floor the datetime to nearest minute so that trades that happen in the same minute are not ignored
        if startdate != None and not isinstance(startdate, str):
            startdate = str(startdate)[:-2] + '00'
            startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d %H:%M:%S')
          



        #wether to concat at end
        #true if you are pushing a certain date because before that date will be saved and 
        #concatted to the new calculation
        conct = True
        if startdate == None:
            conct = False

        #if realtime than pull conacted file + tvscraper
        #account = False
        #if startdate == 'now':
        account = True

        df_aapl = data.get('NFLX','1min',account = account)
        



        #if farther than sooner than now 
        if startdate != 'now' and startdate != None and startdate > df_aapl.index[-1]:
            return df_pnl
        

        #if realtime then only recalc one day
        #otherwise trim to the date
        if startdate != None:
            if startdate == 'now':
                df_pnl = df_pnl[:-1]
                startdate = df_pnl.index[-1]
                index = -1
            else:
                del_index = data.findex(df_pnl,startdate) 
                df_pnl = df_pnl[:del_index]
            
                index = data.findex(df_pnl,startdate)

   
        #initial conditions
       
            
            
            #index = 0
      
            if index == None or index >= len(df_pnl):
                index = -1
            bar = df_pnl.iloc[index]
  
            pnl = bar['close']
            deposits = bar['deposits']
            positions = bar['positions'].split(',')
            shares = bar['shares'].split(',')
       
            pos = []
         
            for i in range(len(shares)):
               
                ticker = positions[i]
                if ticker != '':
                    share = float(shares[i])
                    df = data.get(ticker,'1min',account = account)
                  
                    pos.append([ticker,share,df])

          
            gud = df_log.set_index('datetime')
       
            #add one because 
            log_index = data.findex(gud,startdate) 

            if log_index != None and log_index < len(df_log):
                nex = df_log.iloc[log_index]['datetime']
                

            
            else:
                nex = datetime.datetime.now() + datetime.timedelta(days = 100)
            
            
            if nex < startdate:
                try:
                    log_index += 1
                    nex = df_log.iloc[log_index]['datetime']
                except:
                    nex = datetime.datetime.now() + datetime.timedelta(days = 100)

           
    

        else:
            startdate = df_log.iat[0,1] - datetime.timedelta(days = 1)
            
            pnl = 0
            deposits = 0
            pos = []
            index = 0
            log_index = 0
            nex = df_log.iat[0,1]
 

        #get list of all dates
        start_index = data.findex(df_aapl,startdate)
        prev_date = df_aapl.index[start_index - 1]
        date_list = df_aapl[start_index:].index.to_list()
  
        df_list = []
        pbar = tqdm(total=len(date_list))
        

        #iterate over date list
     
        
      
        ##for date in date_list:
       
        for i in range(len(date_list)):
            date = date_list[i]
            if i > 0:
                prev_date = date_list[i-1]
            pnlvol = 0
            pnlo = pnl
            pnll = pnlo
            pnlh = pnlo
   
            while date > nex:
                remove = False
                ticker = df_log.iat[log_index,0]
                shares = df_log.iat[log_index,2]
                price = df_log.iat[log_index,3]
               
                if ticker == 'Deposit':
                    deposits += price
                else:
                    pos_index = None
                    #if ticker is already a position
                    for i in range(len(pos)):
                        if pos[i][0] == ticker:
                            #if ticker didnt have data when it first became a potiions
                            #the 'df' index will instead represent the average and will therefore be a float
                            #if the trade is a buy then calculate new avg
                            #if trade is a sell calculate the change to pnl
                            if not isinstance(pos[i][2], pd.DataFrame):
                                prev_shares = pos[i][1]
                                avg = pos[i][2]
                                if shares / prev_shares > 0:
                                    pos[i][2] = ((avg*prev_shares) + (price*shares))/(prev_shares + shares)
                                #if trade is a sell
                                else:
                                    gosh = (price - avg) * (-shares)
                                    pnl += gosh
                                    if gosh > 0:
                                        pnlh += gosh
                                    else:
                                        pnll += gosh
                                    
                            pos_index = i
                            pos[i][1] += shares
                            #if the new shares is 0 the ticker will be removed later
                            if pos[i][1] == 0:
                                remove = True
                    #if ticker isnt already a position
                    if pos_index == None:
                        pos_index = len(pos)
                        try:
                            df = data.get(ticker,'1min',account = account)
                            #check if findex doesnt give None
                            data.findex(df,date) + 1
                        except:
                            df = price
                        pos.append([ticker,shares,df])
                    #subtract the amount missed out on from prev close on these new shares
                    df = pos[pos_index][2]
                    if isinstance(df, pd.DataFrame):
                        ind = data.findex(df,prev_date)
                     
                        c1 = df.iat[ind,3]
                        gosh = (c1 - price)*shares
                        pnl += gosh
                        if gosh > 0:
                            pnlh += gosh
                        else:
                            pnll += gosh
                    pnlvol += abs(shares*price)
                    #if the pos was closed then remove ticker from positions
                    if remove:
                        del pos[pos_index]
                log_index += 1
                if log_index >= len(df_log):
                    
                    nex = datetime.datetime.now() + datetime.timedelta(days=100)
                else:
                    nex = df_log.iat[log_index,1]
                   
            
            positions = ""
            god_shares = ""
            #iterate open positions to find change in candle price since last candle multiplied by shares to calc how much
            #each position changed the pnl
            for i in range(len(pos)):
                ticker = pos[i][0]
                shares = pos[i][1]
                df = pos[i][2]
                if isinstance(df, pd.DataFrame):
                    index = data.findex(df,date)
                    prev_index = data.findex(df,prev_date)
                    prevc = df.iat[prev_index,3]
                    #prevc = df.iat[index - 1,3]
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
                })
            df_list.append(add)
            pbar.update(1)
        df = pd.concat(df_list)
     
        
        if conct:
            df = pd.concat([df_pnl.reset_index(),df])
           
       
        
        df = df.reset_index(drop = True)
        df = df.sort_values(by='datetime')
        
        df = df.set_index('datetime',drop = True)
        df.reset_index().to_feather(r"C:\Screener\sync\pnl.feather")
        if tf == None:
            return df 
        else:
            return [df,tf,bars,account_type]
        

    def account(self,date = None):

        if self.event == 'Trade' or 'Real':
            self.account_type = self.event

      
        if self.event == "Load" or self.event == "Recalc":
            tf = self.values['input-timeframe']
            bars = self.values['input-bars']
            if tf == "":
                tf = 'd'
            if bars == "":
                bars = 375
        else:
            tf = 'd'
            bars = 375

        if self.df_pnl.empty or self.event == "Recalc":
            df = Account.calcaccount(self.df_pnl,self.df_log,date)
            
            self.df_pnl = df
          

        if self.account_type == 'Trade':
            df = self.df_traits
        else:
            df = self.df_pnl
        
        bar = [df,tf,bars,self.account_type]
        Account.account_plot(bar)
        Account.plot_update(self)
    
    def account_plot(bar):
        try:
            df = bar[0]
            tf = bar[1]
            bars = int(bar[2])
            account_type = bar[3]

            if account_type == 'Trade':
                
                df = df.sort_values(by='datetime',ascending = True)
                df = df.set_index('datetime')
                
                df = df[['open','high','low','close','volume']]

             
                pc = 0
              
                
                for i in range(len(df)):
                    v = df.iat[i,4]
                    c = df.iat[i,3] + pc
                    o = pc
                    h = df.iat[i,1] + pc
                    l = df.iat[i,2] + pc
                    df.iloc[i] = [o,h,l,c,v]
                    pc = c
                
              
                    
            else:
               
            
                if tf == '':
                    tf = 'd'
                if tf != "1min":
                    logic = {'open'  : 'first','high'  : 'max','low'   : 'min','close' : 'last','volume': 'sum' }
                    df = df.resample(tf).apply(logic).dropna()
                df = df[-bars:]
         
            mc = mpf.make_marketcolors(up='g',down='r')
            s  = mpf.make_mpf_style(marketcolors=mc)
            if os.path.exists("C:/Screener/laptop.txt"): #if laptop
                fw = 30
                fh = 13.8
                fs = 3.4
            else:
                fw = 42
                fh = 18
                fs = 2.1
            string1 = "pnl.png"
            p1 = pathlib.Path("C:/Screener/tmp/pnl") / string1
            
            fig, axlist = mpf.plot(df, type='candle', volume=True, style=s, warn_too_much_data=100000,returnfig = True,figratio = (fw,fh),figscale=fs, panel_ratios = (5,1), mav=(10,20), tight_layout = True)
            plt.savefig(p1, bbox_inches='tight')
            #plt.plot()
        except TimeoutError:# Exception as e:
            pass
           
        #plt.show()
        
        
        
        
    def plot_update(self):
        bio1 = io.BytesIO()
        image1 = Image.open(r"C:\Screener\tmp\pnl\pnl.png")
        image1.save(bio1, format="PNG")
        self.window["-CHART-"].update(bio1.getvalue())






        