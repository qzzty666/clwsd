import threading
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter


DEFAULT_HEADERS = {"User-Agent": "Mozilla/5.0"}
SESSION_POOL_SIZE = 100
MAX_REDIRECTS = 5
CONNECT_TIMEOUT_CAP = 2.5
MIN_READ_TIMEOUT = 3.0

HEAD_FIRST_EXTENSIONS = {
    ".7z",
    ".apk",
    ".avi",
    ".doc",
    ".docx",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".ipa",
    ".jar",
    ".jpeg",
    ".jpg",
    ".js",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".msi",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".rar",
    ".svg",
    ".tar",
    ".ttf",
    ".wav",
    ".webp",
    ".woff",
    ".woff2",
    ".xls",
    ".xlsx",
    ".xml",
    ".zip",
}

_thread_local = threading.local()


def get_session():
    session = getattr(_thread_local, "session", None)
    if session is not None:
        return session

    session = requests.Session()
    adapter = HTTPAdapter(
        pool_connections=SESSION_POOL_SIZE,
        pool_maxsize=SESSION_POOL_SIZE,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(DEFAULT_HEADERS)
    session.max_redirects = MAX_REDIRECTS
    _thread_local.session = session
    return session


def build_timeout(timeout):
    base_timeout = float(timeout)
    connect_timeout = min(base_timeout, CONNECT_TIMEOUT_CAP)
    read_timeout = max(base_timeout, MIN_READ_TIMEOUT)
    return (connect_timeout, read_timeout)


def build_request_options(timeout, request_options=None):
    request_headers = dict(DEFAULT_HEADERS)
    proxies = None

    if request_options:
        request_headers.update(request_options.get("headers", {}))
        cookie_value = str(request_options.get("cookie", "")).strip()
        if cookie_value:
            request_headers["Cookie"] = cookie_value

        proxy_value = str(request_options.get("proxy", "")).strip()
        if proxy_value:
            proxies = {"http": proxy_value, "https": proxy_value}

    request_kwargs = {
        "timeout": build_timeout(timeout),
        "verify": False,
        "allow_redirects": True,
        "stream": True,
        "headers": request_headers,
    }

    if proxies is not None:
        request_kwargs["proxies"] = proxies

    return request_kwargs


def make_request(url, timeout, request_options=None):
    session = get_session()
    return session.get(url, **build_request_options(timeout, request_options))


def make_head_request(url, timeout, request_options=None):
    session = get_session()
    return session.head(url, **build_request_options(timeout, request_options))


def should_try_head_first(url):
    path = urlsplit(url).path.lower()
    if not path or path.endswith("/"):
        return False

    for extension in HEAD_FIRST_EXTENSIONS:
        if path.endswith(extension):
            return True

    return False
