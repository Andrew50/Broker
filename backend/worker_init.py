from rq import Connection, Queue
from redis import Redis
from startup import Worker  # Replace 'custom_worker' with your actual module name

with Connection(Redis(host='redis', port=6379)):
    qs = [Queue('my_queue')]  # List your queues
    w = Worker(qs)
    w.work()
