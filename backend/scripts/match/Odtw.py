


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
            if indexUpperBound > len(y)-1: indexUpperBound = len(y)-1
            u.append(max(y[indexLowerBound:indexUpperBound+1]))
            l.append(min(y[indexLowerBound:indexUpperBound+1]))
        return u, l
    
    def lowerBound(x, upper, lower):
        totalLowerBound = 0
        if(len(x) != upper):
            raise AttributeError
        for i in range(len(x)):
            if (x[i] > upper[i]):
                totalLowerBound += (x[i]-upper[i])^2
            elif(x[i] < lower[i]):
                totalLowerBound += (x[i]-lower[i])^2
        return totalLowerBound
            
        
        


if __name__ == "__main__":
    pass
