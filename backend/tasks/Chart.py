import json

try:
    from Data import Data, Database
except:
    from .Data import Data, Database
    


def get(args):
    ticker = args[0]
    tf = args[1]
    tf = args[2]
    dt = None
    print(f'ticker {ticker} tf {tf} dt {dt}')
    db = Database()
    #df = Data(db,ticker,tf,dt).df
    df = db.get_df(ticker)
    print(df)
    list_of_lists = df.tolist()
    r = json.dumps(list_of_lists)
    return r
if __name__ == '__main__':
    print(get('AAPL','1d'))