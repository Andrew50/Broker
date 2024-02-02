def run_generator(data,st,user_id):
		i = 0
		model = Screener.load_model(user_id,st)
		prev_length = None
		while True:
			print('in generator',flush=True)
			length = data.get_trainer_queue_size(user_id,st)
			print('trainer queue length: ',length,flush=True)
			if length != prev_length:
				start = datetime.datetime.now()
				print('generator timeout reset',flush=True)
			if (datetime.datetime.now() - start).seconds > 60:
				break
			if length < 20:
				print('running trainer screener',flush=True)
				if i == 0:
					sample,_,_ = data.get_setup_sample(user_id,st)
					sample = [[ticker,dt] for ticker,dt,val in sample]
					query = sample
					i = 1
				elif i == 1:
					raise Warning('to code')
				# elif i == 1:
				# 	query = []
				# 	for setup in sample:
				# 		#get neihgbor
				# 		neighbors = get_neighbors(setup)
				# 		for neighbor in neighbors:
				# 			if neighbor not in sample:
				# 				query.append(neighbor)
				#	i = 2
				#elif i == 2:
					#random
				instances = Screener.screen(user_id,st,'trainer',query,.3,model)
				[data.set_trainer_queue(user_id,st,instance) for instance in instances]
			prev_length = length
			time.sleep(10)
		return