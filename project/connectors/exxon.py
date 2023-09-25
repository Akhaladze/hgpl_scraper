from project.connectors.tasks2 import getResult
import time
from time import sleep

records = [
        (1, 'John', 10, 20),
        (2, 'Jane', 20, 30),
        (3, 'Joe', 30, 40),
        (4, 'Jake', 40, 50),
        (5, 'Jess', 50, 60),
        (6, 'Jill', 60, 70),
        (7, 'Jenn', 70, 80),
        (8, 'Jeff', 80, 90),
        (9, 'Judy', 90, 100),
        (10, 'Jade', 100, 110),
        (11, 'Jade', 100, 110)
    ]

for record in records:
        # Send each record as a Celery task with the name "getResult"
    getResult.apply_async(args=(record,), queue='exxon')

    # Save the results from RabbitMQ
while True:
    result = getResult.AsyncResult()
    if result.ready():
        print(result.result)
        time.sleep(1)

