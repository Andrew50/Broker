

from re import T
import pandas as pd
import datetime
import os
import time
from tqdm import tqdm
from Data7 import Data as data

from Detection2 import Detection as detection

from Scan import Scan as scan

from UI5 import UI as ui

from Consolidator import consolidate









class Screener:


    def queue(date = None,days = 1, ticker = None, tf = 'd',browser = None, fpath = None):
       
        path = 0
    

        consolidate.consolidate()

        
        df ={'Date': [],
                    'Ticker':[],
                    'Setup': [],
                    'Z': [],
                    'tf':[]}
        pd.DataFrame(df).to_feather("C:/Screener/sync/todays_setups.feather")
        if ticker == None:
            ticker_list = scan.get(date,tf,True,browser).index.tolist()
           
            if date == None:
                i = 0
                try:
                    df = pd.read_feather(r"C:\Screener\sync\setups.feather")

                    
                    god = df['Ticker'].tolist()
                    
                    for ticker in god:
                        try:
                            ticker_list.remove(ticker)
                            i += 1
                        except TimeoutError:
                            pass
                    
                except:
                    pass
                print(f'{i} tickers already completed')

        elif type(ticker) is str:
            path = 1
            ticker_list = [ticker]
	       
        else:
            path = 1
            ticker_list = ticker
        if date == '0':
            if tf == 'd' or tf == 'w' or tf == 'm':
                path = 1
            else:
                path = 2
            date_list = [date]
        else:
            sample = data.get('NFLX',tf)
            if date == None:
              
                date_list =sample.index.tolist()
                

            else:
                path = 1
            
                
                start_index = data.findex(sample,date)  
                end_index = start_index + days

                trim = sample[start_index:end_index]
                
                date_list = trim.index.tolist()
              
            
        if fpath != None:
            path = fpath

        Screener.run(date_list, ticker_list, tf,path)
        consolidate.consolidate()

    
    def run(date_list,ticker_list,tf,path):
        length = len(ticker_list)*len(date_list)
        print('packaging')
        pbar = tqdm(total=length)
        container = []
       
      


        
      #  #setuplist = ['EP','NEP','P', 'NP', 'NF', 'MR']
      #  setuplist = ['EP']#,'NEP','P', 'NP', 'NF', 'MR']
      ##  setuplist = ['EP','NEP','P', 'NP', 'F', 'NF', 'MR']


      #  model_list = []

      #  print('loading models')
      #  for setup in setuplist:
        
      #      model = load_model('C:/Screener/sync/models/model_' + str(setup))
      #      model = 'god'
      #      model_list.append([model, str(setup)])


        

        for i in  range(len( ticker_list)):


            

            
            ticker = ticker_list[i]
            
           # container.append([ticker, tf , path, [], model_list])
            container.append([ticker, tf , path, []])

            for date in date_list:
                    
                container[i][3].append(date)





                pbar.update(1)
                    
        

#repackage as a list of 5 lists
        if os.path.exists("C:/Screener/laptop.txt"):
            nodes = 8
        else:
            
            nodes = 4
        pbar.close()
        print('spliting')
        pbar = tqdm(total=len(container))
        ii = 0
        package = []
        for _ in range(nodes):
            package.append([])
        for bar in container:
            package[ii].append(bar)
            ii += 1
            if ii == nodes:
                ii = 0

            pbar.update(1)

        pbar.close()
     
        
      
        data.pool(detection.check, package,nodes = nodes)

       # pbar = tqdm(total=len(container))
     ##   for bar in container:

     #       detection.check(bar)
     #       pbar.update(1)




        

if __name__ == '__main__':
    #if   ((datetime.datetime.now().hour) < 5 or (datetime.datetime.now().hour == 5 and datetime.datetime.now().minute < 40)) and not os.path.exists("C:/Screener/laptop.txt"):
    if   ((datetime.datetime.now().hour) < 5 or (datetime.datetime.now().hour == 5 and datetime.datetime.now().minute < 40)) or not os.path.exists("C:/Screener/laptop.txt"):
    
        Screener.queue('0')

         
        ui.loop(ui,True)
         
        browser = scan.startFirefoxSession()
        while datetime.datetime.now().hour < 13:
           
            Screener.queue(tf = '1min', date = '0',browser = browser)

    else:
        if False:
            i = 0
            path = "C:/Screener/tmp/subtickerlists/"
            while True:
                print('enter cycle length (x50)')
                cycles = int(input())
                for _ in range(cycles):
                    dir_list = os.listdir(path)

                    direct = path + dir_list[0]

                    #tickers = pd.read_feather('C:/Screener/tmp/subtickerlists/' + str(i) + '.feather')['Ticker'].to_list()
                    tickers = pd.read_feather(direct)['Ticker'].to_list()


                    Screener.queue(ticker = tickers,fpath = 0)
          

            
                   # os.remove('C:/Screener/tmp/subtickerlists/' + str(i) + '.feather')
               
                    os.remove(direct)
                   # i += 1
        
            
        else:

            Screener.queue(fpath = 1)
        '''
        browser = scan.startFirefoxSession()
        while datetime.datetime.now().hour < 13:
           
            Screener.queue(tf = '1min', date = '0',browser = browser)
       
        #Screener.queue(date = '2022-01-01',fpath = 0,days = 5)
        Screener.queue(date = '2023-04-25', tf = '5min')
        ui.loop(ui,True)
       
       '''
       










                     



