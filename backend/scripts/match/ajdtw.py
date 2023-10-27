import numpy as np

def euclidean_distance(a, b):
    return np.sqrt(np.sum((a - b)**2))

def lb_keogh(query_seq, candidate_seq, radius=1):
    lb_sum = 0
    for i in range(len(query_seq)):
        lower_idx = max(0, i - radius)
        upper_idx = min(len(candidate_seq), i + radius + 1)
        
        if upper_idx <= lower_idx:
            continue
            
        lower_bound = np.min(candidate_seq[lower_idx:upper_idx], axis=0)
        upper_bound = np.max(candidate_seq[lower_idx:upper_idx], axis=0)
        
        if query_seq[i] > upper_bound:
            lb_sum += euclidean_distance(query_seq[i], upper_bound)
        elif query_seq[i] < lower_bound:
            lb_sum += euclidean_distance(query_seq[i], lower_bound)
    
    return lb_sum

def subsequence_dtw(query_seq, long_seq, radius=1):
    m, n = len(query_seq), len(long_seq)
    dtw_matrix = np.full((m + 1, n + 1), np.inf)
    dtw_matrix[0, 0] = 0

    for i in range(1, m + 1):
        for j in range(max(1, i - radius), min(n + 1, i + radius + 1)):
            cost = euclidean_distance(query_seq[i - 1], long_seq[j - 1])
            dtw_matrix[i, j] = cost + min(dtw_matrix[i - 1, j], dtw_matrix[i, j - 1], dtw_matrix[i - 1, j - 1])
            
            lb_distance = lb_keogh(query_seq[i - 1:], long_seq[j - 1:], radius)
            current_min_distance = dtw_matrix[m, :].min()
            
            if dtw_matrix[i, j] + lb_distance > current_min_distance:
                return np.inf

    return dtw_matrix[m, :].min()

def find_dtw_distances(query_seq, long_seqs, radius=1):
    distances = []
    for long_seq in long_seqs:
        distance = subsequence_dtw(query_seq, long_seq, radius)
        distances.append(distance)
    return distances

# Example usage
# query_seq = np.array([[1], [2], [3]])
# long_seqs = [
#     np.array([[2], [3], [4], [1], [2], [3], [4]]),
#     np.array([[1], [2], [3], [3], [3], [4], [4]])
# ]

query_seq = y
long_seqs = x



distances = find_dtw_distances(query_seq, long_seqs)
for i, distance in enumerate(distances, start=1):
    print(f"Long Sequence {i}: Minimum DTW distance is {distance}")
