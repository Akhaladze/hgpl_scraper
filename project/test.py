import sys, os
from time import sleep
app_path='/home/gnet/dev/hgpl_scraper/project/'
sys.path.append(app_path)
from celery import Celery
from celery.result import AsyncResult

app = Celery("tasks",
             broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
             backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis'))
from tasks import add


i = 0
while True and i < 1000000:
    result = add.delay(4 + i^i, 40 * i)

    print(result.ready())
    print(result.get())
    #result.get()
    #sleep(1)
    i += 1
    #print(say_hello.delay("John").get())
   # print(download_sds.delay(1000).get())
    #sleep(5)
    #print(result2.ready())
    #print(result2.get(timeout=1))
    #result2.get(propagate=False)


if __name__ == "__main__":
    app.start()

