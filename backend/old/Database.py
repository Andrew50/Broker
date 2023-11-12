

if __name__ == '__main__':
	db = Database()
	ticker_list = db.get_ticker_list('full')
	for ticker in tqdm(ticker_list):
		db.get_df(ticker)
	db.close_pool()

