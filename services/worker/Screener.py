import tensorflow as tf
import numpy as np

class Screener:
    
    def load_model(user_id,st):
        return tf.keras.models.load_model(f'./models/{user_id}_{st}')

    def screen(data,user_id,setup_types,threshold = .25):
        assert len(setup_types) > 0
        args_by_tf = {}
        for st in setup_types:
            tf, bars, dolvol_req, adr_req = data.get_st_info(user_id,st)
            args_by_tf[tf] += [st,bars,dolvol_req,adr_req, mcap_req]
        results = []
        for tf, args in args_by_tf.items():
            args.sort(lambda x: x[1], reverse = True)
            min_dolvol = min([x[2] for x in args])
            min_adr = min([x[3] for x in args])
            min_mcap = min([x[4] for x in args])
            tickers = data.get_tickers(min_dolvol,min_adr,min_mcap)
            data.set_current_prices(tickers)
            ds = []
            for ticker, dolvol, adr, mcap in tickers:
                ds.append(data.get_df('screener',ticker,tf))
            ds = np.array(ds)

            for st, bars, dolvol_req, adr_req, mcap_req in args:
                ds = ds[:,=bars:,:]
                model = load_model(user_id,st)
                map = np.array([dolvol > dolvol_req and adr > adr_req and mcap > mcap_req] for ticker, dolvol, adr, mcap in tickers],dtype = bool)
                scores = model.predict(ds[map])
                results += [ticker,st,score] for ticker,score in zip(tickers[:,0],scores[0] if score > threshold
                
        return results
    
def get(data, user_id, setup_types):
    return Screener.screen(data,user_id,setup_types,'screener')
            
if __name__ == '__main__':
    from sync_Data import Data
    print(get(Data(),1,['d_EP'],'screener'))
                                                                     
#        if _format == 'screener':
#            for st in setup_types:
#                dolvol_req, adr_req = data.get_screener_req(user_id,st)
#                for df, adr, dol
#
#                model = Screener.load_model(user_id,st)
#                tf, setup_length = data.get_setup_info(user_id,st)
#                ds, ticker_list = data.get_ds('screener','full',tf,setup_length,dollar_volume = 5*1000000,adr=2)
#                ds = ds[:,:,1:5]
#                scores = model.predict(ds)[:,0]
#                i = 0
#                for score in scores:
#                    if score > threshold:
#                        ticker = ticker_list[i]
#                        results.append([ticker,st,int(100*score)])
#                    i += 1
#            results.sort(key=lambda x: x[1],reverse=True)
#            return results
#        
#        elif _format == 'trainer':
#            st = setup_types
#            tf, setup_length = data.get_setup_info(user_id,st)
#            ds, ticker_list = data.get_ds('screener',query,tf,setup_length)
#            dt_list = ds[:,-1,0]
#            ds = ds[:,:,1:]
#            scores = model.predict(ds)[:,0]
#            i = 0
#            for score in scores:
#                if score > threshold and score < 1 - threshold:
#                    ticker = ticker_list[i]
#                    results.append([ticker,tf,dt_list[i]])
#                i += 1
#            return results
#        
#        elif _format == 'study':
#            query = [[query,None]]
#            st = setup_types
#            #for st in setup_types:
#            tf, setup_length = data.get_setup_info(user_id,st)
#            ds, ticker_list = data.get_ds('screener',query,tf,None)
#            model = Screener.load_model(user_id,st)
#            dt_list = ds[:,:,0]
#            ds = ds[:,:,1:]
#            scores = model.predict(ds)[:,0]
#            i = 0
#            for score in scores:
#                if score > threshold:
#                    dt = dt_list[i]
#                    results.append([dt,int(100*score)])
#                i += 1
#            
#            return results
