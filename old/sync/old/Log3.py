
from discordwebhook import Discord
import pathlib
import mplfinance as mpf
import statistics
import pandas as pd
import datetime
from Data7 import Data
import pyarrow
import multiprocessing
import os

discordtopGainers = Discord(url="https://discord.com/api/webhooks/1071666210514669648/dSLYGAB5CWQuulV46ePmExwgljauPexCG10R2ZqZctTl7lyya-Zs7lJ7ecLjQEruAfYw")
discordintraday = Discord(url="https://discord.com/api/webhooks/1071667193709858847/qwHcqShmotkEPkml8BSMTTnSp38xL1-bw9ESFRhBe5jPB9o5wcE9oikfAbt-EKEt7d3c")
discord = Discord(url="https://discord.com/api/webhooks/1071506429229416519/41ps0qlsiiFRDLxnZVCF5KuDtb_SWBHCwB5scK-YUf96mrBpzZRydsT2C4GiGPDAEmKW")

class Log:
    def sendDiscordEmbedGainers(ticker, description):
        discordtopGainers.post(
            embeds=[
            {

                "title": ticker,
                "description": description,
            }
            ],
        )
    def sendDiscordEmbedIntraday(ticker, description):
        discordintraday.post(
            embeds=[
            {

                "title": ticker,
                "description": description,
            }
            ],
        )
        

    def sendDiscordEmbed(ticker, description):
        discord.post(
            embeds=[
            {

                "title": ticker,
                "description": description,
            }
            ],
        )
    def sendDiscordPost(f):
        discord.post(file={"test": open(f, "rb")})
    def sendDiscordIntradayPost(f):
        
        discordintraday.post(file={"test": open(f, "rb")})
        
    def sendDiscordGainersPost(f):
        discordtopGainers.post(file={"test": open(f, "rb")})



    def intraday(df,currentday, tf, ticker, z, path, st):
        
        mc = mpf.make_marketcolors(up='g',down='r')
        s  = mpf.make_mpf_style(marketcolors=mc)
        ourpath = pathlib.Path("C:/Screener/tmp")/ 'test.png'
       
        z = round(z, 3)
        df = df[-100:]
        #df.set_index('datetime', inplace = True)
        mpf.plot(df, type='candle', mav=(10, 20), volume=True, title=f'{ticker}, {st}, {z}, {tf}', style=s, savefig=ourpath)
        Log.sendDiscordIntradayPost('tmp/test.png')

    def log(df,currentday, tf, ticker, z, path, st):
  
        if path == 2:
            
            
            Log.intraday(df,currentday, tf, ticker, z, path, st)
            
        if path == 1:

           
            file_path = "C:/Screener/tmp/subsetups/today" + str(os.getpid()) + ".feather"
            '''
            if df.index[currentday] == datetime.date.today(): 
                date = '0'
            else:
                date = df.index[currentday]
            '''
            #if date == '0':
                #date = df.index[currentday]
            date = df.index[currentday]
            data ={'Date': [date],
                    'Ticker':[ticker],
                    'Setup': [st],
                    'Z': [z],
                    'tf':[tf]}
        
            dfadd = pd.DataFrame(data)
            try:
                old = pd.read_feather(file_path)
            except:
                old = pd.DataFrame()
            new = pd.concat([old,dfadd])
            
            new = new.reset_index(drop = True)
           
            new.to_feather(file_path)

        if path == 0:



            
            
            cooldown = 0

            #gap percent
            #adr
            #vol %
            #q risin 10 > rising 20
            # 1 dperf
            # 2 d perf
            #3 d perf
            #10 ma perf
            #10 am perf time
       
            
            date = df.index[currentday]

            file_path = "C:/Screener/tmp/subsetups/" + str(os.getpid()) + ".feather"

            exlude = False
            if cooldown > 0:
                try:
                    full = pd.read_feather(file_path)
                    
                    scan = full
                   

            
                    scanholder = pd.DataFrame()
                    for k in range(len(scan)):
                        if scan.iat[k,1] == ticker:
                            scanholder = pd.concat([scanholder,scan.iloc[[k]]])
                    scan = scanholder

              
                    scanholder = pd.DataFrame()
                    for k in range(len(scan)):
                        if scan.iat[k,2] == st:
                            scanholder = pd.concat([scanholder,scan.iloc[[k]]])
                    scan = scanholder
                
            
                    if len(scan) > 0:
                    
                        recent_date = scan.iloc[-1]['Date']
                        delta = (date - recent_date).days
                        if abs(delta) <= cooldown:
                            exclude = True
                    
                        else:
                            exclude = False
                    else:
                        exclude = False
                except FileNotFoundError:
                    full = pd.DataFrame()
                    exclude = False
                except IndexError:
                    exclude = False
                except pyarrow.lib.ArrowInvalid:

                    #full = pd.DataFrame()
                    exclude = True
                except OSError:
                    exclude = True
                
            
            if not exclude:

                data = pd.DataFrame({'Date': [date],
                        'Ticker':[ticker],
                        'Setup': [st],
                        'Z': [z],
                        'timeframe': [tf],
                        'annotation': [""]
                        
                        })
 
                df = pd.concat([full,data])
                
                
                df = df.reset_index(drop = True)
              
                df.to_feather(file_path)


                '''












            #
                gap = round( (df.iat[currentday,0]/df.iat[currentday-1,3] - 1)*100,2)

                volma = []
                for i in range(10):
                    volma.append(df.iat[currentday-1-i,4])
                vol = round((df.iat[currentday,4]/statistics.mean(volma) ),2)

                q_data = Data.get('QQQ')
                qcurrentday = Data.findex(q_data, date)
                q10 = []
                q20 = []

                for i in range(21):
                    close = q_data.iat[qcurrentday - 1-i,3]

                    q20.append(close)
                    if i >= 9:
                        q10.append(close)

                    if i == 19:
                        prev10 = statistics.mean(q10)
                        prev20 = statistics.mean(q20)

                current10 = statistics.mean(q10)
                current20 = statistics.mean(q20)
            
                if current10 > prev10 and current20 > prev20 and current10 > current20:
                    q = True
                else:
                    q = False
            
                one = round((df.iat[currentday,3] / df.iat[currentday,0] - 1) * 100,2)
                two =   round((df.iat[currentday+1,3] / df.iat[currentday,0] - 1) * 100,2)
                three =  round((df.iat[currentday+2,3] / df.iat[currentday,0] - 1) * 100,2)
                four = round((df.iat[currentday+3,3] / df.iat[currentday,0] - 1) * 100,2)
                five = round((df.iat[currentday+4,3] / df.iat[currentday,0] - 1) * 100,2)

                change10 = 0
                change20 = 0
                change60 = 0
                change250 = 0

                try:
                    change10 = round((df.iat[currentday-1,3] / df.iat[currentday-11,3] - 1) * 100,2)

                    change20 = round((df.iat[currentday-1,3] / df.iat[currentday-21,3] - 1) * 100,2)
                    change60 = round((df.iat[currentday-1,3] / df.iat[currentday-61,3] - 1) * 100,2)
                    change250 = round((df.iat[currentday-1,3] / df.iat[currentday-251,3] - 1) * 100,2)
                except:
                    pass
                            
              


                adr = []
                for j in range(20): 
                    high = df.iat[currentday-j-1,1]
                    low = df.iat[currentday-j-1,2]
                    val = (high/low - 1) * 100
                    adr.append(val)
                        
                adr = round(statistics.mean(adr) ,2)
           
                i = 0

                
                while True:

                    ma10 = []
                    for j in range(10):
                        ma10.append((df.iat[currentday-j+i,3]))
                    ma10 = statistics.mean(ma10)
                    close = df.iat[currentday+i,3]

                    if i == 0:
                        if close > ma10:
                            short = False
                        else:
                            short = True

                    if short:
                        if close > ma10:
                            break
                    else:
                        if ma10 > close:
                            break
                   
                    
                    if i == len(df):
                        break

                    i += 1
                

                ten = round( (df.iat[currentday+i,3] / df.iat[currentday,0] - 1)*100,2)
                time = i 


                data = pd.DataFrame({'Date': [date],
                        'Ticker':[ticker],
                        'Setup': [st],
                        'Z': [z],
                        'timeframe': [tf],
                        'gap': [gap],
                        'adr': [adr],
                        'vol': [vol],
                        'q': [q],
                        '1': [one],
                        '2': [two],
                        '3': [three],
                        '10': [ten],
                        'annotation': [""],
                        'time': [time]
 
                        })
 
                df = pd.concat([full,data])
                
                
                df = df.reset_index(drop = True)
            
                df.to_feather(file_path)
            
            

            
                '''

