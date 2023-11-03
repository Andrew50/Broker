try:
    from Data import Data, Database
except:
    from .Data import Data, Database
def get(ticker,tf,dt):
    conn = Database()
    return Data(conn,ticker).df

if __name__ == '__main__':
    print(get('AMZN','d',None))