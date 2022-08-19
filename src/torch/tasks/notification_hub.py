import requests

class Notification:
    def __init__(self,config):
        self.app_url = config["APP_URL"]

    def send(self, data):
        r = requests.post(url=self.app_url + "/notificationshub",headers={"Content-Type":"application/json"},json=data)
        print(r.status_code, r.reason)

