import json
import os
import requests
import charset_normalizer

COOKIE_JAR_PATH = os.path.join(os.path.dirname(__file__), ".cookies")


def load_cookie_jar() -> requests.cookies.RequestsCookieJar:
    jar = requests.cookies.RequestsCookieJar()
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

        # FIX: assign SameSite to the actual cookie object
        obj = next(c for c in jar if c.name == cookie["name"])
        obj.samesite = cookie.get("samesite", "Lax")

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
            "samesite": getattr(cookie, "samesite", "Lax"),
        })

    with open(COOKIE_JAR_PATH, "w", encoding="utf-8") as fh:
        json.dump(cookies, fh)


COOKIE_JAR = load_cookie_jar()


def is_same_site(host_a: str, host_b: str) -> bool:
    """Compare registrable domains."""
    def base(h: str):
        parts = h.split(".")
        return ".".join(parts[-2:]) if len(parts) >= 2 else h
    return base(host_a) == base(host_b)


def filter_cookies_for_request(url_obj: "URL", cross_origin: bool) -> requests.cookies.RequestsCookieJar:
    allowed = requests.cookies.RequestsCookieJar()

    for cookie in COOKIE_JAR:
        samesite = getattr(cookie, "samesite", "Lax")
        same_site = is_same_site(url_obj.host, cookie.domain or url_obj.host)

        if samesite.lower() == "strict":
            if same_site:
                allowed.set_cookie(cookie)

        elif samesite.lower() == "lax":
            if same_site or (not cross_origin and url_obj.method == "get"):
                allowed.set_cookie(cookie)

        elif samesite.lower() == "none":
            if cookie.secure:
                allowed.set_cookie(cookie)

        else:
            # Default = Lax
            if same_site or (not cross_origin and url_obj.method == "get"):
                allowed.set_cookie(cookie)

    return allowed


class URL:
    def __init__(self, url: str, params: dict[str, str] = {}, method: str = "get"):
        self.scheme, url = url.split("://", 1)
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url
        self.params: dict[str, str] = params
        self.method: str = method.lower()

    def request(self, cross_origin: bool = False) -> tuple[dict, str]:
        global COOKIE_JAR

        if self.scheme == "file":
            return {}, open(self.path, "rb").read()

        send_cookies = filter_cookies_for_request(self, cross_origin)

        match self.method:
            case "get":
                resp = requests.get(str(self), params=self.params, cookies=send_cookies)
            case "post":
                resp = requests.post(str(self), data=self.params, cookies=send_cookies)

        result = charset_normalizer.from_bytes(resp.content).best()
        content = result.output() if result else resp.content

        COOKIE_JAR.update(resp.cookies)
        save_cookie_jar(COOKIE_JAR)

        return resp.headers, content

    def resolve(self, url: str) -> "URL":
        if "://" in url:
            return URL(url)
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

    def origin(self):
        return self.host

    def __str__(self) -> str:
        return f"{self.scheme}://{self.host}{self.path}"
