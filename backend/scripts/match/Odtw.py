import math


# Optimized dynamic time warping for match
# Let y denote the timeseries we want to find similarities of
class Odtw: 
    def calcBounds(y, radius):
        u = []
        l = []
        for i in range(len(y)):
            indexLowerBound = y-radius
            indexUpperBound = y+radius
            if indexLowerBound < 0: indexLowerBound = 0
            elif indexUpperBound > len(y)-1: indexUpperBound = len(y)-1
            u.append(max(y[indexLowerBound:indexUpperBound+1]))
            l.append(min(y[indexLowerBound:indexUpperBound+1]))
        return u, l
    
    def calclowerBound(x, upper, lower):
        totalLowerBound = 0
        if(len(x) != len(upper)):
            raise AttributeError
        for i in range(len(x)):
            if (x[i] > upper[i]):
                totalLowerBound += (x[i]-upper[i])^2
            elif(x[i] < lower[i]):
                totalLowerBound += (x[i]-lower[i])^2
        return math.sqrt(totalLowerBound)

    def dtwEqual(x, y, radius):
        pass
            
        
        


if __name__ == "__main__":
    pass
