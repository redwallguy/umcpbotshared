import redis
import celery
import requests
import os

r = redis.from_url(os.environ.get("REDIS_URL"))
app = celery.Celery('umcp_celery', broker=os.environ.get("REDIS_URL"))

@app.task
def remind(aid, message):
    print("Success")
    r.lrem("reminderlist",aid)
    requests.post(os.environ.get("WEBHOOK_URL"),headers={'Content-Type': 'application/json'},
                      data={'content': message})
    return
