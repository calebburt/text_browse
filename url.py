import requests

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
    
    def request(self):
        resp = requests.get(f"{self.scheme}://{self.host}/{self.path}")
        headers = resp.headers
        content = resp.text

        return content