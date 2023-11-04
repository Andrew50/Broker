import json

try:
    from Data import Data, Database
except:
    from .Data import Data, Database
    


def get(ticker,tf,dt=None):
    dt = None
    print(f'ticker {ticker} tf {tf} dt {dt}')
    conn = Database()
    df = Data(conn,ticker,tf,dt).df
    print(df)
    list_of_lists = df.tolist()
    r = json.dumps(list_of_lists)
    return r
if __name__ == '__main__':
    print(get('AAPL','1d'))