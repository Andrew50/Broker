from Data import Database, Data
from Match import Match
import Odtw
import math
if __name__ == '__main__':
    np_bars = 10
    db = Database()
    ticker = 'JBL'
    dt = '2023-10-03'
    tf = '1d'
    y = Data(db,ticker, tf, dt,bars = np_bars+1).df
    y = Match.formatArray(y, yValue=True)
    print(y)
    ticker = 'SUN'
    data = db.get_df(ticker)
    data = Match.formatArray(data)
    radius = math.ceil(np_bars/10)
    upper, lower = Odtw.calcBounds(y, radius)
    print(upper)
    print(lower)
    bar = [data, y, ticker, upper, lower, 200, radius]
    print(Match.worker(bar))
    print('test')

