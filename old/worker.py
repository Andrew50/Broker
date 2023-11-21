from rq import Worker as Worker, Connection, Queue
from redis import Redis
from Data import Data  # Import your Data class

data = Data()

#class Worker(_Worker):
    #def work(self, burst=False, *args, **kwargs):
        # Initialize the database connection when the worker starts working
      #  global data
     #   data = Data()
     #   super().work(burst=burst, *args, **kwargs)

    #def perform_job(self, job, *args, **kwargs):
        # Create a wrapper function to include the data connection
        #original_func = job.func
       # job_args = job.args

       # def wrapped_func(*args, **kwargs):
          #  return original_func(*args, *job_args, db_connection=self.data_, **kwargs)

        #job._instance = wrapped_func
       # return super().perform_job(job, self.data_, **kwargs)
        #return super().perform_job(job, *args, **kwargs)

if __name__ == '__main__':
    with Connection(Redis(host='redis', port=6379)):
        qs = [Queue('my_queue')]  # List your queues
        w = Worker(qs)  # Ensure this is your custom Worker
        w.work()




# from rq import Worker as _Worker, Connection, Queue
# from redis import Redis
# from Data import Data  # Import your Data class

# class Worker(_Worker):
#     def work(self, burst=False, *args, **kwargs):
#         # Initialize the database connection when the worker starts working
#         self.data_ = Data()
#         super().work(burst=burst, *args, **kwargs)

#     def perform_job(self, job, *args, **kwargs):
#         # Wrap the job function to include the data connection
#         job.func = self.wrap_job_func(job.func, self.data_)
#         return super().perform_job(job, *args, **kwargs)

#     def wrap_job_func(self, func, data):
#         # Wrapper function that injects the database connection
#         def wrapped(*args, **kwargs):
#             return func(data, *args, **kwargs)
#         return wrapped

# if __name__ == '__main__':
#     with Connection(Redis(host='redis', port=6379)):
#         qs = [Queue('my_queue')]  # List your queues
#         w = Worker(qs)  # Ensure this is your custom Worker
#         w.work()



# from Data import Data
# from rq.worker import Worker as _Worker
# from redis import Redis
# from rq import Connection, Queue

# #_pools = LocalStack()

# # class Worker(_Worker):
# # 	def work(self, *args, **kwargs):
# # 		Data()
# # 		#_pools.push({'data':Data()})
# # 		return super(Worker, self).work(*args, **kwargs)

# class Worker(_Worker):
#     def work(self, burst=False, *args, **kwargs):
#         # Initialize the database connection when the worker starts working
#         self.data_ = Data()
#         super().work(burst=burst, *args, **kwargs)

#     def perform_job(self, job, *args, **kwargs):
#         # Pass the database connection to the job
#         global data
#         data = self.data_
#         return super().perform_job(job, *args, **kwargs)



# if __name__ == '__main__':
# 	with Connection(Redis(host='redis', port=6379)):
# 		qs = [Queue('my_queue')]  # List your queues
# 		w = Worker(qs)
# 		w.work()