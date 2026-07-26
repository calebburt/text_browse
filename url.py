import json
import os
import requests
import charset_normalizer

COOKIE_JAR_PATH = os.path.join(os.path.dirname(__file__), ".cookies")


def load_cookie_jar() -> requests.cookies.RequestsCookieJar:
    jar: requests.cookies.RequestsCookieJar = requests.cookies.RequestsCookieJar()
    if not os.path.exists(COOKIE_JAR_PATH):
        return jar

    try:
        with open(COOKIE_JAR_PATH, "r", encoding="utf-8") as fh:
            cookies = json.load(fh)
    except (OSError, ValueError, TypeError):
        return jar

    for cookie in cookies:
        jar.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path", "/"),
            secure=cookie.get("secure", False),
            expires=cookie.get("expires"),
        )
    return jar


def save_cookie_jar(jar: requests.cookies.RequestsCookieJar) -> None:
    cookies: list[dict[str, str]] = []
    for cookie in jar:
        cookies.append({
            "name": cookie.name,
            "value": cookie.value,
            "domain": cookie.domain,
            "path": cookie.path,
            "secure": cookie.secure,
            "expires": cookie.expires,
        })

    with open(COOKIE_JAR_PATH, "w", encoding="utf-8") as fh:
        json.dump(cookies, fh)


COOKIE_JAR = load_cookie_jar()

class URL:
    def __init__(self, url: str, params: dict[str, str] | None = None, method: str = "get"):
        if params is None:
            params = {}
        self.scheme, url = url.split("://", 1)
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        self.params: dict[str, str] = params
        self.method: str = method.lower()
    
    def request(self) -> str:
        global COOKIE_JAR
        if self.scheme == "file":
            content = open(self.path).read()
            return content
        match self.method:
            case "get":
                resp = requests.get(str(self), params=self.params, cookies=COOKIE_JAR) # , verify=False)
            case "post":
                resp = requests.post(str(self), data=self.params, cookies=COOKIE_JAR) # , verify=False)

        result = charset_normalizer.from_bytes(resp.content).best()
        content = resp.content
        
        if result:
            # Decode safely using the detected encoding
            content = result.output()

        content = content.decode('utf-8', errors='replace')  # Fallback to UTF-8 with replacement for undecodable bytes

        COOKIE_JAR.update(resp.cookies)
        save_cookie_jar(COOKIE_JAR)

        return content
    
    def resolve(self, url: str) -> "URL":
        if "://" in url: return URL(url)
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url
        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            url = dir + "/" + url
        if url.startswith("//"):
            return URL(self.scheme + ":" + url)
        else:
            return URL(self.scheme + "://" + self.host + url)
    
    def __str__(self) -> str:
        return f"{self.scheme}://{self.host}{self.path}"