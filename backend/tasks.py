from huey_instance import huey
import os
from scripts import Match
Match = Match.Match
from scripts import Data
Data = Data.Data
from multiprocessing import Pool as pool


Data(k

def add_numbers(num1, num2):
    print('Task is running...')
    path = 'C:/dev/Broker/backend/working'
    os.mkdir(path)
    
    try:
        result = num1 + num2
        print(f"The result is: {result}")
        return result
    except Exception as e:
        print('An error occurred:', str(e))
        return 'An error occurred'
