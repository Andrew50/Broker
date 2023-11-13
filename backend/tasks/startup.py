from Data import Database, Dataset, Cache

db = Database()
ds = Dataset(db,'full').dfs

cache_startup = [[ds,'ds']]

cache = Cache()
[ cache.set(data,key) for data, key in cache_startup]