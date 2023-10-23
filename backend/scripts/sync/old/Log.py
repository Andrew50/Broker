

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

from Traits import Traits as traits
from Account import Account as account

import os
from imbox import Imbox # pip install imbox
import traceback

class Log:



    def pull_mail():

        host = "imap.gmail.com"
        username = "billingsandrewjohn@gmail.com"
        password = 'kqnrpkqscmvkrrnm'
        download_folder = "C:/Screener/tmp/pnl"
        if not os.path.isdir(download_folder):
            os.makedirs(download_folder, exist_ok=True)
        mail = Imbox(host, username=username, password=password, ssl=True, ssl_context=None, starttls=False)
        #messages = mail.messages() # defaults to inbox
        dt = datetime.date.today() - datetime.timedelta(days = 1)
        messages = mail.messages(sent_from='noreply@email.webull.com',date__gt=dt)
        
        for (uid, message) in messages:
            mail.mark_seen(uid) # optional, mark message as read
            for idx, attachment in enumerate(message.attachments):
               
                att_fn = attachment.get('filename')
                print(att_fn)
                if not 'IPO' in att_fn and not  'Options' in att_fn:
                    download_path = f"{download_folder}/{att_fn}"
                        
                    with open(download_path, "wb") as fp:
                        fp.write(attachment.get('content').read())
               
                    

        mail.logout()
        log = pd.read_csv('C:/Screener/tmp/pnl/Webull_Orders_Records.csv')
        log2 = pd.DataFrame()
        log2['ticker'] = log['Symbol']
        log2['datetime']  = pd.to_datetime(log['Filled Time'])
        log2['shares'] = log['Filled']
        for i in range(len(log)):
            if log.at[i,'Side'] != 'Buy':
                log2.at[i,'shares'] *= -1
        log2['price'] = log['Avg Price']
        log2['setup'] = ''
        log2 = log2.dropna()
        log2 = log2[(log2['datetime'] > '2021-12-01')]
        log2 = log2.sort_values(by='datetime', ascending = False).reset_index(drop = True)
        return log2


    def log(self):
        if not self.df_log.empty:
            self.df_log = self.df_log.sort_values(by='datetime', ascending = False)

        if self.event == 'Pull':

            new_log = Log.pull_mail()

            print(new_log)
            #self.df_log = new_log
            
            non_dep = self.df_log[self.df_log['ticker'] != 'Deposit']


            new = pd.concat([non_dep, new_log]).drop_duplicates(keep=False)
            print(new)
            new = new.sort_values(by='datetime', ascending = False)
            dt = new.iloc[-1]['datetime']

            print(new)

            df_log = pd.concat([self.df_log,new])

            df_log = df_log.sort_values(by='datetime', ascending = True).reset_index(drop = True)
            
            self.df_pnl = account.calcaccount(self.df_pnl,df_log,dt)
            #self.df_pnl.reset_index().to_feather(r"C:\Screener\sync\pnl.feather")
            self.df_traits = traits.update(new.values.tolist(), df_log,self.df_traits,self.df_pnl)

            self.df_log = df_log
            if os.path.exists("C:/Screener/tmp/pnl/charts"):
                shutil.rmtree("C:/Screener/tmp/pnl/charts")
            os.mkdir("C:/Screener/tmp/pnl/charts")



        if self.event == '-table-':
            try:
                index = self.values['-table-'][0]
                
                if type(index) == int:
                    self.index = index
                    bar = self.df_log.iloc[index]
                    self.window["input-ticker"].update(bar[0])
                    self.window["input-datetime"].update(bar[1])
                    self.window["input-shares"].update(bar[2])
                    self.window["input-price"].update(bar[3])
                    self.window["input-setup"].update(bar[4])
                    
            except:
                pass

            
        
        if self.event == "Enter":
            
            ticker = str(self.values['input-ticker'])

            if ticker != "":
                try:
                    dt = self.values['input-datetime']
                    dt  = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                    shares = float(self.values['input-shares'])
                    price = float(self.values['input-price'])
                    setup = str(self.values['input-setup'])

                    add = pd.DataFrame({
            
                        'ticker': [ticker],
                        'datetime':[dt],
                        'shares': [shares],
                        'price': [price],
                        'setup': [setup]
                        })
                    df_log = self.df_log
                    if self.index == None:
                        df_log = pd.concat([df_log,add])
                        df_log.reset_index(inplace = True, drop = True)
                    else:
                    
                        df_log.iat[self.index,0] = ticker
                        old_date = df_log.iat[self.index,1]
                        df_log.iat[self.index,1] = dt
                        df_log.iat[self.index,2] = shares
                        df_log.iat[self.index,3] = price
                        df_log.iat[self.index,4] = setup
                        if old_date < dt:
                            dt = old_date
                    df_log = df_log.sort_values(by='datetime', ascending = True).reset_index(drop = True)
                    #if ticker != 'Deposit':
                    self.df_pnl = account.calcaccount(self.df_pnl,df_log,dt)
                    #self.df_pnl.reset_index().to_feather(r"C:\Screener\sync\pnl.feather")
                    #self.df_traits = traits.update(add.values.tolist()[0], df_log,self.df_traits,self.df_pnl)
                    if ticker != 'Deposit':
                        self.df_traits = traits.update(add.values.tolist(), df_log,self.df_traits,self.df_pnl)
                    else:
                        self.df_traits = traits.update([],df_log,pd.DataFrame(),self.df_pnl)
                        self.df_traits.to_feather(r"C:\Screener\sync\traits.feather")
                    self.df_log = df_log
                    if os.path.exists("C:/Screener/tmp/pnl/charts"):
                        shutil.rmtree("C:/Screener/tmp/pnl/charts")
                    os.mkdir("C:/Screener/tmp/pnl/charts")
                    #self.df_log.
                    #self.df_log.to_feather(r"C:\Screener\sync\log.feather")
                except TimeoutError:
                #except Exception as e:
                    sg.Popup(str(e))
                
        if self.event == "Delete":
            if self.index != None:
                bar = self.df_log.iloc[self.index].to_list()
                df_log = self.df_log.drop(self.index).reset_index(drop = True)
                df_log = df_log.sort_values(by='datetime', ascending = True)
                self.df_pnl = account.calcaccount(self.df_pnl,df_log,bar[1])
                #self.df_pnl.reset_index().to_feather(r"C:\Screener\sync\pnl.feather")
                self.df_traits = traits.update([bar], df_log,self.df_traits,self.df_pnl)
                self.df_log = df_log
                self.index = None
                if os.path.exists("C:/Screener/tmp/pnl/charts"):
                    shutil.rmtree("C:/Screener/tmp/pnl/charts")
                os.mkdir("C:/Screener/tmp/pnl/charts")
                

           
        elif self.event == "Clear":
            if self.index == None:
            
                self.window["input-ticker"].update("")
                self.window["input-shares"].update("")
                self.window["input-price"].update("")
                self.window["input-setup"].update("")
                self.window["input-datetime"].update("")
            else:
                self.index = None

        try:
            self.window['-index-'].update(f'Index {self.index}')
        except:
            pass
        
        self.df_log = self.df_log.reset_index(drop = True)
        if not self.df_log.empty:
            self.df_log.to_feather(r"C:\Screener\sync\log.feather")
            table = self.df_log.sort_values(by='datetime', ascending = False).values.tolist()

       
            self.window["-table-"].update(table)



#if __name__ == '__main__':
   # Log.pull_mail()