import numpy as np
from scipy.spatial.distance import euclidean
from scipy.signal import savgol_filter

def derivative(seq, window_length=5, polyorder=2):
    """Compute the derivative of a sequence using Savitzky-Golay filter."""
    return savgol_filter(seq, window_length, polyorder, deriv=1)

def ddtw_distance(seq1, seq2, window_length=5, polyorder=2):
    """Compute the DDTW distance between two sequences."""
    # Compute derivatives
    d_seq1 = derivative(seq1, window_length, polyorder)
    d_seq2 = derivative(seq2, window_length, polyorder)

    # Initialize distance matrix
    n, m = len(d_seq1), len(d_seq2)
    dtw_matrix = np.zeros((n+1, m+1))
    dtw_matrix[0, :] = np.inf
    dtw_matrix[:, 0] = np.inf
    dtw_matrix[0, 0] = 0

    # Populate distance matrix
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = euclidean(d_seq1[i-1], d_seq2[j-1])
            dtw_matrix[i, j] = cost + min(dtw_matrix[i-1, j],    # insertion
                                          dtw_matrix[i, j-1],    # deletion
                                          dtw_matrix[i-1, j-1])  # match

    return dtw_matrix[n, m]

# Example usage
seq1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
seq2 = np.array([1, 1, 2, 3, 5, 8, 13, 21, 34])

distance = ddtw_distance(seq1, seq2)
print("DDTW Distance:", distance)
