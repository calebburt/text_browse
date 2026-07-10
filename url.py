import requests

class URL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
    
    def request(self):
        if self.scheme == "file":
            content = open(self.path).read()
            return content
        resp = requests.get(f"{self.scheme}://{self.host}{self.path}")

        # Detect encoding
        encoding = resp.apparent_encoding

        # Decode using the chosen encoding
        content = resp.content.decode(encoding, errors="replace")

        return content
    
    def resolve(self, url: str):
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        if "://" in url: return URL(url)
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            url = dir + "/" + url
        if url.startswith("//"):
            return URL(self.scheme + ":" + url)
        else:
            return URL(self.scheme + "://" + self.host + url)