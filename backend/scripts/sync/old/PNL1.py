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



#from accountcalculator import accountcalculator as account
from Account import Account as account


from Log import Log as log

from Traits import Traits as traits
from Plot import Plot as plot


class PNL():

   

    def update(self):
        
        if self.menu == None:
            sg.theme('DarkGrey')
            try:
                self.df_log = pd.read_feather(r"C:\Screener\sync\log.feather").sort_values(by='datetime',ascending = False)
            except:
                self.df_log = pd.DataFrame()
            try:
                self.df_traits = pd.read_feather(r"C:\Screener\sync\traits.feather").sort_values(by='datetime',ascending = False)
            except FileNotFoundError:
                self.df_traits = pd.DataFrame()
            try:
                self.df_pnl = pd.read_feather(r"C:\Screener\sync\pnl.feather").set_index('datetime', drop = True)
            except:
                self.df_pnl = pd.DataFrame()
          
            self.menu = "Log"
        else:
            self.window.close()
     

        if os.path.exists("C:/Screener/laptop.txt"): #if laptop

            scalelog = 6
            scaleplot = 4.5
            scaleaccount = 5
            scaletraits = 4
            
        else:
            scalelog = 3.7
            scaleplot = 2.98
            scaleaccount = 3
            scaletraits = 3
       
        if self.menu == "Log":



            toprow = ['Ticker        ','Datetime        ','Shares ', 'Price   ','Setup    ']
            c1 = [  
            [(sg.Text("Ticker    ")),sg.InputText(key = 'input-ticker')],
            [(sg.Text("Datetime")),sg.InputText(key = 'input-datetime')],
            [(sg.Text("Shares   ")),sg.InputText(key = 'input-shares')],
            [(sg.Text("Price     ")),sg.InputText(key = 'input-price')],
            [(sg.Text("Setup    ")),sg.InputText(key = 'input-setup')],
            [sg.Text("",key = '-index-')],
            [sg.Button('Delete'),sg.Button('Clear'),sg.Button('Enter')],
            [sg.Button('Pull')],
            [sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]
    
            c2 = [[sg.Table([],headings=toprow,key = '-table-',auto_size_columns=True,num_rows = 30,justification='left',enable_events=True,selected_row_colors='red on yellow')]]
         

            layout = [
            [sg.Column(c1),
             sg.VSeperator(),
             sg.Column(c2),]]
            self.window = sg.Window(self.menu, layout,margins = (10,10),scaling=scalelog,finalize = True)
            log.log(self)
        if self.menu == "Account":
            layout =[
            [sg.Image(key = '-CHART-')],
            [(sg.Text("Timeframe")),sg.InputText(key = 'input-timeframe')],
            #[(sg.Text("Datetime  ")),sg.InputText(key = 'input-datetime')],
            [(sg.Text("Bars  ")),sg.InputText(key = 'input-bars')],
            [sg.Button('Trade'),sg.Button('Real'),sg.Button('Recalc'),sg.Button('Load')],
            [sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]
            self.window = sg.Window(self.menu, layout,margins = (10,10),scaling=scaleaccount,finalize = True)
            account.account(self)
        if self.menu == "Traits":
             
            toprow = ['    ','Ticker  ','$      ']
            c1 = [[sg.Table([],headings=toprow,key = '-table_gainers-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,selected_row_colors='red on yellow')]]
            c2 = [[sg.Table([],headings=toprow,key = '-table_losers-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,selected_row_colors='red on yellow')]]

            toprow = [' Trait ', 'Value ', 'Residual ']
            c3 = [[sg.Table([],headings=toprow,key = '-table_traits-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,selected_row_colors='red on yellow')]]
            toprow = ['Month    ', 'Avg Gain    ', 'Avg Loss    ', 'Win %    ', 'Trades     ', 'PNL     ']
            c4 = [[sg.Table([],headings=toprow,key = '-table_monthly-',auto_size_columns=True,num_rows = 10,justification='left',enable_events=True,enable_click_events=True)]]


            c5 = [[sg.Button('Recalc')],
                [sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]

            c6 = [[sg.Image(key = '-CHART-')]]


            layout = [
            [sg.Column(c1),
             sg.VSeperator(),
             sg.Column(c2),
             sg.VSeperator(),
             sg.Column(c3),
             sg.VSeperator(),
             sg.Column(c4),
             sg.VSeperator(),
             ],
             [sg.Column(c5),
             sg.VSeperator(),
             sg.Column(c6),
             ]]
             
             
            
            '''
            layout = [
            [sg.Image(key = '-CHART-')],
            [(sg.Text("Trait  ")),sg.InputText(key = 'input-trait')],
            [sg.Button('Recalc'),sg.Button('Enter')],
            [sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]


            '''
            self.window = sg.Window(self.menu, layout,margins = (10,10),scaling=scaletraits,finalize = True)
            traits.traits(self)
        if self.menu == "Plot":
            toprow = ['Date             ','Shares   ','Price  ', 'Percent  ',' Timedelta   ','Size  ']
            toprow2 = ['Actual  ','Fsell  ','Fbuy   ', '10h     ','20h     ','50h     ','5d     ','10d     ']
            c2 = [  
             [sg.Image(key = '-IMAGE3-')],
             [sg.Image(key = '-IMAGE1-')]]
            c1 = [
             [sg.Image(key = '-IMAGE2-')],
             [(sg.Text((str(f"{self.i + 1} of {len(self.df_traits)}")), key = '-number-'))], 
             [sg.Table([],headings=toprow2,num_rows = 2, key = '-table2-',auto_size_columns=True,justification='left', 
                       expand_y = False)],
              [sg.Table([],headings=toprow,key = '-table-',auto_size_columns=True,justification='left',num_rows = 5, 
                       expand_y = False)],
            [(sg.Text("Ticker  ")),sg.InputText(key = 'input-ticker')],
            [(sg.Text("Date   ")),sg.InputText(key = 'input-datetime')],
            [(sg.Text("Setup  ")),sg.InputText(key = 'input-setup')],
            [(sg.Text("Sort    ")),sg.InputText(key = 'input-sort')],
            [sg.Button('Prev'),sg.Button('Next'),sg.Button('Load')],
            [sg.Button('Account'), sg.Button('Log'),sg.Button('Traits'),sg.Button('Plot')]]


            layout = [
            [sg.Column(c1),
             sg.VSeperator(),
             sg.Column(c2)],]

            self.window = sg.Window(self.menu, layout,margins = (10,10),scaling=scaleplot,finalize = True)
            plot.plot(self)


        self.window.maximize()


    def loop(self):

        with Pool(6) as self.pool:
            if os.path.exists("C:/Screener/tmp/pnl/charts"):
                shutil.rmtree("C:/Screener/tmp/pnl/charts")
            os.mkdir("C:/Screener/tmp/pnl/charts")
            self.preloadamount = 7
            self.i = 0
            self.menu = None
            self.event = [None]
            self.index = None
            self.update(self)
            self.account_type = 'Real'
            lap = datetime.datetime.now()
            while True:
                
                self.event, self.values = self.window.read(timeout=15000)
               
                if self.event == "Traits" or self.event == "Plot" or self.event == "Account" or self.event == "Log":
                    self.index = None
                    self.menu = self.event
                    self.update(self)
                elif self.event != '__TIMEOUT__':
                    
                    if self.menu == "Traits":

                        traits.traits(self)
                    elif self.menu == "Plot":
                        plot.plot(self)
                    elif self.menu == "Account":
                        account.account(self)
                    elif self.menu == "Log":
                        log.log(self)

                else:
                  
                    if self.menu == "Account": #and (data.isMarketOpen()):
                        print('refresh')
                        self.df_pnl = pd.read_feather(r"C:\Screener\sync\pnl.feather").set_index('datetime',drop = True)
                        account.plot_update(self)
                        pool = self.pool
                        tf = self.values['input-timeframe']
                        bars = self.values['input-bars']
                    
                        if tf == '':
                            tf = 'd'
                        if bars == '':
                            bars = '375'
                        pool.apply_async(account.calcaccount,args = (self.df_pnl,self.df_log,'now',tf,bars,self.account_type, self.df_traits), callback = account.account_plot)
                        
                        
if __name__ == "__main__":
    PNL.loop(PNL)




