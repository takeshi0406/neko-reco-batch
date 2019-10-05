import os
import twitter as tw
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler


class Client(object):
    def __init__(self, token, token_secret, consumer_key, consumer_secret):
        self.client = TwitterClient(token, token_secret, consumer_key, consumer_secret)

    def get_reply_user(self):
        return self.client.get_reply_user()


class TwitterClient(object):
    last_id = None

    def __init__(self, token, token_secret, consumer_key, consumer_secret):
        oauth = tw.OAuth(
            token,
            token_secret,
            consumer_key,
            consumer_secret
            )
        self.client = tw.Twitter(auth=oauth)
        
    def get_reply_user(self):
        if not self.last_id:
            tweets = self.client.statuses.mentions_timeline()
        else:
            tweets = self.client.statuses.mentions_timeline(since_id=self.last_id)
        if not tweets:
            return set()
        self.last_id = max(x["id"] for x in tweets)
        return {(x['user']['screen_name'], x["id"]) for x in tweets}

sc = Client(*[os.environ[x] for x in ["TOKEN", "TOKEN_SECRET", "CONSUMER_KEY", "CONSUMER_SECRET"]])

def main():
    """ Function for test purposes. """
    users = sc.get_reply_user()
    for u in users:
        result = requests.post("http://54.65.177.130:5000/fetch/",
            data=json.dumps({"screen_name": u[0], "id": u[1]}), headers={"Content-Type": "application/json"})
        print(f"posted: {result.text}")
    print(f"Scheduler is alive!")



if __name__ == "__main__":
    sched = BackgroundScheduler(daemon=False)
    sched.add_job(main,'interval', seconds=3)
    sched.start()