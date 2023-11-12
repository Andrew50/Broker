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


class Plot:
    def plot(self):
        
        if self.event == 'Load':
            scan = pd.read_feather(r"C:\Screener\sync\traits.feather")
            dt = self.values['input-datetime']

            ticker = self.values['input-ticker']
            
            setup = self.values['input-setup']
            sort = self.values['input-sort']
        

            if ticker  != "":
                scan = scan[scan['ticker'] == ticker]
            
            

            if setup  != "":
                scan = scan[scan['setup'] == setup]
     
            if len(scan) < 1:
                sg.Popup('No Setups Found')
                return
            

            if sort != "":
                try:
                    scan = scan.sort_values(by=[sort], ascending=False)
                except KeyError:
                    sg.Popup('Not a Trait')
                    return

            self.df_traits = scan
            if os.path.exists("C:/Screener/tmp/pnl/charts"):
                shutil.rmtree("C:/Screener/tmp/pnl/charts")
            os.mkdir("C:/Screener/tmp/pnl/charts")
            
            if dt != "":

                self.i = data.findex(self.df_traits.set_index('datetime',drop = True),dt,-1)
            else:
                self.i = 0
         
        if self.event == 'Next' :
            if self.i == len(self.df_traits) - 1:
                self.i = 0
            else:
                self.i += 1
        if self.event == 'Prev':
  
            if self.i == 0:
                self.i = len(self.df_traits) - 1
            else:
                self.i -= 1

        
            #i = list(range(len(self.df_traits)))
            #i = list(range(self.preloadamoun))
            
            '''
        if(len(self.df_traits) < self.preloadamount):
            god = len(self.df_traits) - 1
        else:
            god = self.preloadamount
        '''
        i = list(range(self.i,self.preloadamount+self.i))
        if self.i < 5:
            i += list(range(len(self.df_traits) - 1,len(self.df_traits) - self.preloadamount - 1,-1))
        else:
            i += list(range(self.i,self.i - self.preloadamount,-1))
                
        
        i = [x for x in i if x >= 0 and x < len(self.df_traits)]
  
        arglist = []
        for index in i:
            arglist.append([index,self.df_traits])
      
        pool = self.pool
       # pool.map_async(Plot.create,arglist) #--------------------------------------------------------------------------------------------------------------------------------------------------------------------
        pool.map_async(Plot.create,arglist) #--------------------------------------------------------------------------------------------------------------------------------------------------------------------

        image1 = None
        image2 = None
        image3 = None

        start = datetime.datetime.now()
        while image1 == None or image2 == None or image3 == None:
            if (datetime.datetime.now() - start).seconds > 8:
                pool.map_async(Plot.create,[[self.i,self.df_traits]])
            try:
                image1 = Image.open(r"C:\Screener\tmp\pnl\charts" + f"\{self.i}" + "1min.png")
                image2 = Image.open(r"C:\Screener\tmp\pnl\charts" + f"\{self.i}" + "d.png")
                image3 = Image.open(r"C:\Screener\tmp\pnl\charts" + f"\{self.i}" + "h.png")
            except:
                pass


        #########table shit



        table = []
        bar = self.df_traits.iat[self.i,2]

        maxsize = 0
        size = 0
        for k in range(len(bar)):
            shares = float(bar[k][2]) 

            size += shares
           
            if abs(size) > abs(maxsize):
               
                maxsize = size
      
        for k in range(len(bar)):
                     
            startdate = datetime.datetime.strptime(bar[0][1], '%Y-%m-%d %H:%M:%S')
            date  = datetime.datetime.strptime(bar[k][1], '%Y-%m-%d %H:%M:%S')
            
            shares = (float(bar[k][2]))
            price = float(bar[k][3])
            try:
                size = f'{round(shares / maxsize * 100)} %'
            except:
                size = 'NA'
            timedelta = (date - startdate)
            if k == 0:
                percent = ""
            else:
                percent = round(float(bar[0][2])*((price / float(bar[0][3])) - 1) * 100 / abs(float(bar[0][2])),2)
            
            table.append([date,shares,price,percent,timedelta,size])

        #tabel2
        table2 = [[],[]]
       
        for i in range(6,14):
            try:
                string = f'{round(self.df_traits.iat[self.i,i],2)} %'
            except:
                string = str(self.df_traits.iat[self.i,i])
            table2[0].append(string)
        for i in range(14,22):
            try:
                string = f'{round(self.df_traits.iat[self.i,i],2)} %'
            except:
                string = str(self.df_traits.iat[self.i,i])
            table2[1].append(string)
        '''
        pnl = 0
        for i in range(len(bar)):
            price = float(bar[k][3])
            shares = float(bar[k][2])
            dollars = price*shares
            pnl -= dollars
        '''



        bio1 = io.BytesIO()
        image1.save(bio1, format="PNG")
        bio2 = io.BytesIO()
        image2.save(bio2, format="PNG")
        bio3 = io.BytesIO()
        image3.save(bio3, format="PNG")

        self.window["-IMAGE1-"].update(data=bio1.getvalue())
        self.window["-IMAGE2-"].update(data=bio2.getvalue())
        self.window["-IMAGE3-"].update(data=bio3.getvalue())
        self.window["-number-"].update(str(f"{self.i + 1} of {len(self.df_traits)}"))
        self.window["-table2-"].update(table2)
        self.window["-table-"].update(table)

        
    def create(bar):


        i = bar[0]
        
            

        if (os.path.exists(r"C:\Screener\tmp\pnl\charts" + f"\{i}" + "1min.png") == False):
            df = bar[1]


                
            try:
                god = bar[2]
                tflist = ['d']
            except:

                tflist = ['1min','h','d']

            
            
            mc = mpf.make_marketcolors(up='g',down='r')
            s  = mpf.make_mpf_style(marketcolors=mc)

            if os.path.exists("C:/Screener/laptop.txt"): #if laptop
                fw = 22
                fh = 12
                fs = 1.95

            else:
                fw = 26
                fh = 13
                fs = 1.16
                
        
            ticker = df.iat[i,0]
            
            for tf in tflist:
                try:
                    string1 = str(i) + str(tf) + ".png"
                    p1 = pathlib.Path("C:/Screener/tmp/pnl/charts") / string1

        
               
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
                            add = pd.DataFrame({
                                    'Datetime':[df.iat[i,2][k][1]], 
                                    'Symbol':[df.iat[i,2][k][0]],
                                    'Action':"Buy",
                                    'Price':[float(df.iat[i,2][k][3])]
                                    })
                            trades.append(add)
                        else:
                            colorlist.append('r')

                        datelist.append(date)
                    
                    god = bar[1].iloc[i]['arrows']
                    god = [list(x) for x in god]
                    dfall= pd.DataFrame(god, columns=['Datetime', 'Price', 'Color', 'Marker'])
                    dfall['Datetime'] = pd.to_datetime(dfall['Datetime'])
                    dfall = dfall.sort_values('Datetime')
                    colors = []
                    dfsByColor = []
                    for zz in range(len(dfall)):
                        if(dfall.iloc[zz]['Color'] not in colors):
                            colors.append(dfall.iloc[zz]['Color'])
        
                    for yy in range(len(colors)):
                        colordf = dfall.loc[dfall['Color'] == colors[yy]] 
                        dfsByColor.append(colordf)


                    df1 = data.get(ticker,tf,account = True)
                    
                    startdate = dfall.iloc[0]['Datetime']
                    enddate = dfall.iloc[-1]['Datetime']
                    try:

                        l1 = data.findex(df1,startdate) - 50
                    except:
                        if 'd' in tf or 'w' in tf:
                            df1 = df1 = data.get(ticker,tf,account = False)
                            l1 = data.findex(df1,startdate) - 50
                        else:
                            raise Exception()
                    closed = df.iloc[i]['closed']
                    if closed:
                        r1 = data.findex(df1,enddate) + 50
                    else:
                        r1 = len(df1)
                    minmax = 300
                #    if tf == '1min' and r1 - l1 > minmax:
                   #     r1 = l1 + minmax
                    
                    if l1 < 0:
                        l1 = 0
                    df1 = df1[l1:r1]
                    #if ticker == 'FNGU' and tf == 'h':
                    #    print(df1)
                       # print(l1)
                      #  print(r1)
                    times = df1.index.to_list()
                    timesdf = []
                    
                    for _ in range(len(df1)):
                        nextTime = pd.DataFrame({ 
                            'Datetime':[df1.index[_]]
                            })
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
                                        test = pd.DataFrame({
                                            'Datetime':[times[q]],
                                            'Marker':[datafram.iloc[t]['Marker']],
                                            'Price':[float(datafram.iloc[t]['Price'])]
                                            })
                                        tradelist.append(test)
                                        break
########################################################################
                                else:
                                   # time = times[q].to_pydatetime() + (times[q].to_pydatetime() - times[q-1])
                                  #  if time >= tradeTime:
                                    test = pd.DataFrame({
                                            'Datetime':[times[q]],
                                            'Marker':[datafram.iloc[t]['Marker']],
                                            'Price':[float(datafram.iloc[t]['Price'])]
                                            })
                                    tradelist.append(test)
                                    break
#########################################################
                        df2 = pd.concat(tradelist).reset_index(drop = True)
                        df2['Datetime'] = pd.to_datetime(df2['Datetime'])
                        df2 = df2.sort_values(by=['Datetime'])
                        df2['TradeDate_count'] = df2.groupby("Datetime").cumcount() + 1
                        newdf = (df2.pivot(index='Datetime', columns='TradeDate_count', values="Price")
                            .rename(columns="price{}".format)
                            .rename_axis(columns=None))
                        
                        series = mainindidf.merge(newdf, how='left', left_index=True, right_index=True)[newdf.columns]
                        
                        if series.isnull().values.all(axis=0)[0]:
                            pass
                        else: 
                            apds.append(mpf.make_addplot(series,type='scatter',markersize=300,alpha = .4,marker=datafram.iloc[0]['Marker'],edgecolors='black', color=datafram.iloc[0]['Color']))

               
                    '''
                    df2 = pd.concat(tradelist).reset_index(drop = True)
                    buy = df2[df2['Action'] == 'Buy']
                    buy['Datetime'] = pd.to_datetime(buy['Datetime'])
                    buy = buy.sort_values(by=['Datetime'])
                    sell = df2[df2['Action'] == 'Sell']
                    sell['Datetime'] = pd.to_datetime(sell['Datetime'])
                    sell = sell.sort_values(by=['Datetime'])
                    buy["TradeDate_count"] = buy.groupby("Datetime").cumcount() + 1
                    sell["TradeDate_count"] = sell.groupby("Datetime").cumcount() + 1
                    newbuys = (buy.pivot(index='Datetime', columns='TradeDate_count', values="Price")
                            .rename(columns="price{}".format)
                            .rename_axis(columns=None))
                    newsells = (sell.pivot(index='Datetime', columns='TradeDate_count', values="Price")
                            .rename(columns="price{}".format)
                            .rename_axis(columns=None))
                    timesdf = []
                    for _ in range(len(df1)):
                         ad = pd.DataFrame({
                                'Datetime':[df1.index[_]]
                                })
                         timesdf.append(ad)
                    mainindidf = pd.concat(timesdf).set_index('Datetime', drop=True)
                    buyseries = mainindidf.merge(newbuys, how='left', left_index=True, right_index=True)[newbuys.columns]
                    sellseries =  mainindidf.merge(newsells, how='left', left_index=True, right_index=True)[newsells.columns]
                    apds = [mpf.make_addplot(mainindidf)]
                    if buyseries.isnull().values.all(axis=0)[0]:  ## test if all cols have null only
                        pass
                    else:  
                        apds.append(mpf.make_addplot(buyseries,type='scatter',markersize=300,alpha = .6,marker='^',edgecolors='black', color='g'))
                
                    if sellseries.isnull().values.all(axis=0)[0]:  ## test if all cols have null only
                        pass
                    else:  
                        apds.append(mpf.make_addplot(sellseries,type='scatter',markersize=300,alpha = .6,marker='v',edgecolors='black', color='r'))
                    '''


                    if tf == 'h':
                        mav = (10,20,50)
                    elif tf == 'd':
                        mav = (5,10)
                    else:
                        mav = ()


                    fig, axlist = mpf.plot(df1, type='candle', volume=True  , 
                                           title=str(f'{ticker} , {tf}'), 
                                           style=s, warn_too_much_data=100000,returnfig = True,figratio = (fw,fh),
                                           figscale=fs, panel_ratios = (5,1), mav=mav, 
                                           tight_layout = True,
                                        #   vlines=dict(vlines=datelist, 
                                          #colors = colorlist, alpha = .2,linewidths=1),
                                          addplot=apds)
                    ax = axlist[0]
                    #for k in range(len(df.iat[i,2])):
                     #   ax.text()




                    ax.set_yscale('log')
                    ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
                    
                    plt.savefig(p1, bbox_inches='tight') 
                except Exception as e:
                #except TimeoutError as e:
                    
                
                    shutil.copy(r"C:\Screener\tmp\blank.png",p1)
                   
                    
