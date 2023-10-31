from huey import RedisHuey

huey = RedisHuey('myapp')

@huey.task()
def add_numbers(num1, num2):
    try:
        result = num1 + num2
        print(f"The result is: {result}")
        return result
    except:
        print('working')
        return 'gosh'