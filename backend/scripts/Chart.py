import json

try:
    from Data import Data, Database
except:
    from .Data import Data, Database
def get():
    conn = Database()
    df = Data(conn,'AAPL').df
    list_of_lists = df.tolist()
    return json.dumps(list_of_lists)

if __name__ == '__main__':
    print(get('AMZN','d',None))