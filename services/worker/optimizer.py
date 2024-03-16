

from sddtw_test import SDDTW
from multiprocessing import Pool
import statistics

if __name__ == '__main__':
    ticker, tf, dt = 'MRK', '1d', '2022-11-17'
    ticker2, dt2 = 'EGY', '2022-02-28'

    #ticker, tf, dt, ticker_2, dt2 = 'FREY', '1d', '2022-10-04', 'FSLR', '2022-10-04'

    # rank = SDDTW.score_instance((ticker,tf,dt,ticker2,dt2,50,7,2))[0]
    # print(rank)
    # input()


    bars_pool = [25,50]
    smoothing_window_pool = [5,7,9,11,15,19,23,27]
    poly_order_pool = [2,3]

    args = []
    for bars in bars_pool:
        for smoothing_window in smoothing_window_pool:
            for poly_order in poly_order_pool:
                if smoothing_window > poly_order and bars > smoothing_window:
                    args.append((ticker,tf,dt,ticker2,dt2,bars,smoothing_window,poly_order))

    with Pool() as p:
        results = p.map(SDDTW.score_instance, args)

    sorted_results = sorted(results, key=lambda x: x[0])
    print(sorted_results[:20])
    print(statistics.mean([x[0] for x in sorted_results[:20]]))

    