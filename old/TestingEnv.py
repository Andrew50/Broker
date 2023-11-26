def test(db):
        ticker = 'CELH'
        tf = '1d'
        dt = '2023-10-03'
        
        dt = Database.format_datetime(dt)
        y = Data(db,ticker, tf, dt,bars=np_bars+1).df###################
        y = Match.formatArray(y, yValue=True)
        print(testDtw(y, y, 1))
        
    def testDtw(a, b, r):

        m = len(a)
        k = 0

        # Instead of using matrix of size O(m^2) or O(mr), we will reuse two arrays of size O(r)
        cost = [float('inf')] * (2 * r + 1)
        cost_prev = [float('inf')] * (2 * r + 1)

        for i in range(0, m):
            k = max(0, r - i)

            for j in range(max(0, i - r), min(m - 1, i + r) + 1):
                # Initialize all row and column
                if i == 0 and j == 0:
                    c = a[0] - b[0]
                    cost[k] = c * c

                    k += 1
                    continue

                y = float('inf') if j - 1 < 0 or k - 1 < 0 else cost[k - 1]
                x = float('inf') if i < 1 or k > 2 * r - 1 else cost_prev[k + 1]
                z = float('inf') if i < 1 or j < 1 else cost_prev[k]

                # Classic DTW calculation
                d = a[i] - b[j]
                cost[k] = min(x, y, z) + d * d

                k += 1

            # Move current array to previous array
            cost, cost_prev = cost_prev, cost

        # The DTW distance is in the last cell in the matrix of size O(m^2) or at the middle of our array
        k -= 1
        return cost_prev[k]
