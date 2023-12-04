from sync_Data import data
from Screener import Screener

class Study:
    

    def update(user_id,st):
        total = data
        ticker_list = data.get_ticker_list('full')
        current_tickers = data.get_finished_study_tickers(user_id,st)
        for ticker in ticker_list:
            if ticker not in current_tickers:
                new_instances = Screener.screen(user_id,st,'study',ticker)
                data.set_study(user_id,st,new_instances)
                total += len(new_instances)
                if total > 2500:
                    break
                current_tickers.append(ticker)




def get(args,user_id):
    st, = args
    Study.update(user_id,st)

if __name__ == '__main__':
    
    Study.update(6,'EP')