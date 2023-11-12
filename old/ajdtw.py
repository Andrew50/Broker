import numpy as np
import os
import pandas as pd
from tqdm import tqdm
import datetime

class Match:
    @staticmethod
    def euclidean_distance(a, b):
        return np.sqrt(np.sum((a - b)**2))

    @staticmethod
    def lb_keogh(query_seq, candidate_seq, radius=2):
        lb_sum = 0
        for i in range(len(query_seq)):
            lower_idx = max(0, i - radius)
            upper_idx = min(len(candidate_seq), i + radius + 1)
            if upper_idx <= lower_idx:
                continue
            lower_bound = np.min(candidate_seq[lower_idx:upper_idx], axis=0)
            upper_bound = np.max(candidate_seq[lower_idx:upper_idx], axis=0)
            if query_seq[i] > upper_bound:
                lb_sum += Match.euclidean_distance(query_seq[i], upper_bound)
            elif query_seq[i] < lower_bound:
                lb_sum += Match.euclidean_distance(query_seq[i], lower_bound)
        return lb_sum

    @staticmethod
    def subsequence_dtw(query_seq, long_seq, radius=1):
        m, n = len(query_seq), len(long_seq)
        dtw_matrix = np.full((m + 1, n + 1), np.inf)
        dtw_matrix[0, 0] = 0
        for i in range(1, m + 1):
            for j in range(max(1, i - radius), min(n + 1, i + radius + 1)):
                cost = Match.euclidean_distance(query_seq[i - 1], long_seq[j - 1])
                dtw_matrix[i, j] = cost + min(dtw_matrix[i - 1, j], dtw_matrix[i, j - 1], dtw_matrix[i - 1, j - 1])
        return dtw_matrix[m, :].min()

    @staticmethod
    def find_dtw_distances(query_seq, long_seqs, radius=1, lb_radius=1):
        distances = []
        pbar = tqdm(total=len(long_seqs))
        for i in range(len(long_seqs)): #long_seq in long_seqs:
            long_seq = long_seqs[i]
            lb_distance = Match.lb_keogh(query_seq, long_seq, lb_radius)
            if lb_distance < np.inf:  # If the lower bound is below infinity, we proceed with DTW
                distance = Match.subsequence_dtw(query_seq, long_seq, radius)
                print(distance)
                print(f'{distance.shape} <= distacne shape')
                distances.append([distance,i])
            else:
                distances.append([np.inf,i])  # If LB_Keogh already tells us the sequences are far apart, we don't compute DTW
            pbar.update(1)
        pbar.close()
        return distances

    @staticmethod
    def normalize(data):
        min_val = np.min(data)
        max_val = np.max(data)
        range_val = max_val - min_val
        if range_val != 0:
            normalized_data = (data - min_val) / range_val
        else:
            normalized_data = data - min_val
        return normalized_data
    
    @staticmethod
    def run(query_ticker, tf):
        folder = 'C:/dev/Broker/backend/tasks/d/'
        dir_list = os.listdir(folder)[:200]
        x = []

        def get(ticker, tf):
            path = folder + ticker + '.feather'
            df = pd.read_feather(path)
            if len(df) < 10:
                raise TimeoutError
            close_array = df['close'].to_numpy().reshape(-1, 1)
            normalized_data = Match.normalize(close_array)
            return normalized_data

        try:
            y = get(query_ticker, tf)
        except IndexError:
            print(f'y failed {query_ticker}')
            return

        start = datetime.datetime.now()
        tickers = []
        for d in dir_list:
            try:
                ticker = d.split('.')[0]
                tf = '1d'
                x.append(get(ticker, tf))
                tickers.append(ticker)
            except TimeoutError:
                # print(f'{ticker} failed')
                pass

        print(f'loaded in {datetime.datetime.now() - start}')
        query_seq = y
        long_seqs = x
        start = datetime.datetime.now()

        print(len(long_seqs))
        distances = Match.find_dtw_distances(query_seq, long_seqs)
        #matches = distances.sort
        print(f'loaded in {datetime.datetime.now() - start}')
        for i in range(len(distances)):
            distances[i] += [tickers[i]]
            


        sorted_list = sorted(distances, key=lambda x: x[0])[:20]
        
        for i in range(len(sorted_list)):
            folder = 'C:/dev/Broker/backend/tasks/d/'
            path = folder + query_ticker + '.feather'
            df = pd.read_feather(path)
            print(df)
            date = df['datetime'].to_list()[sorted_list[i][1]]
            sorted_list[i] += [date]
        
        return sorted_list
    
        # for i, distance in enumerate(distances, start=1):
        #     print(f"Long Sequence {i}: Minimum DTW distance is {distance}")

if __name__ == '__main__':
    df = Match.run('JBL', 'd')
    print(df)




# import numpy as np
# import os
# import datetime
# import pandas as pd
# from tqdm import tqdm



# class Match:

#     def euclidean_distance(a, b):
#         return np.sqrt(np.sum((a - b)**2))

#     def lb_keogh(query_seq, candidate_seq, radius=1):
#         lb_sum = 0
#         for i in range(len(query_seq)):
#             lower_idx = max(0, i - radius)
#             upper_idx = min(len(candidate_seq), i + radius + 1)
#             if upper_idx <= lower_idx:
#                 continue
#             lower_bound = np.min(candidate_seq[lower_idx:upper_idx], axis=0)
#             upper_bound = np.max(candidate_seq[lower_idx:upper_idx], axis=0)
#             if query_seq[i] > upper_bound:
#                 lb_sum += Match.euclidean_distance(query_seq[i], upper_bound)
#             elif query_seq[i] < lower_bound:
#                 lb_sum += Match.euclidean_distance(query_seq[i], lower_bound)
#         return lb_sum

#     def subsequence_dtw(query_seq, long_seq, radius=1):
#         m, n = len(query_seq), len(long_seq)
#         dtw_matrix = np.full((m + 1, n + 1), np.inf)
#         dtw_matrix[0, 0] = 0
#         for i in range(1, m + 1):
#             print('god')
#             for j in range(max(1, i - radius), min(n + 1, i + radius + 1)):
#                 cost = Match.euclidean_distance(query_seq[i - 1], long_seq[j - 1])
#                 dtw_matrix[i, j] = cost + min(dtw_matrix[i - 1, j], dtw_matrix[i, j - 1], dtw_matrix[i - 1, j - 1])
#                 lb_distance = Match.lb_keogh(query_seq[i - 1:], long_seq[j - 1:], radius)
#                 current_min_distance = dtw_matrix[m, :].min()
#                 if dtw_matrix[i, j] + lb_distance > current_min_distance:
#                     return np.inf
#         return dtw_matrix[m, :].min()

#     def find_dtw_distances(query_seq, long_seqs, radius=1):
#         distances = []
#         pbar = tqdm(total = len(long_seqs))
#         for long_seq in long_seqs:
#             distance = Match.subsequence_dtw(query_seq, long_seq, radius)
#             distances.append(distance)
#             pbar.update(1)
#         pbar.close()
#         return distances
#     # Example usage
#     # query_seq = np.array([[1], [2], [3]])
#     # long_seqs = [
#     #     np.array([[2], [3], [4], [1], [2], [3], [4]]),
#     #     np.array([[1], [2], [3], [3], [3], [4], [4]])
#     # ]


#     def normalize(data):
#         min_val = np.min(data)
#         max_val = np.max(data)
#         range_val = max_val - min_val
#         if range_val != 0:
#             normalized_data = (data - min_val) / range_val
#         else:
#             normalized_data = data - min_val
#         return normalized_data
#     def run(query_ticker,tf):
        
#         folder = 'C:/dev/Broker/backend/tasks/d/'
#         dir_list = os.listdir(folder)
#         x = []
#         def get(ticker,tf):
#             path = folder + ticker + '.feather'
            
#             df = pd.read_feather(path)
#             if len(df) < 10:
#                 raise TimeoutError
#             close_array = df['close'].to_numpy().reshape(-1, 1)
#            # close_array = df['close'].to_numpy()
#             x = Match.normalize(close_array)
#             return x
#         try:
#             y = get(query_ticker,tf)a
#         except IndexError:
#             print(f'y failed {query_ticker}')
#             return




#         start = datetime.datetime.now()
#         for d in dir_list:
#             try:
#                 ticker = d.split('.')[0]
#                 tf = '1d'
#                 x.append(get(ticker,tf)   ) 
#             except TimeoutError:
#                 #print(f'{ticker} failed')
#                 pass
       
#         print(f'loaded in {datetime.datetime.now() - start}')
#         query_seq = y
#         long_seqs = x
#         start = datetime.datetime.now()
        
#         print(len(long_seqs))
#         distances = Match.find_dtw_distances(query_seq, long_seqs)
#        # for i, distance in enumerate(distances, start=1):
#         #    print(f"Long Sequence {i}: Minimum DTW distance is {distance}")
#         print(f'loaded in {datetime.datetime.now() - start}')

# if __name__ == '__main__':
#     Match.run('JBL','d')




    