import html
import re

import requests


def extract_title(html_text):
    match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if match:
        title = match.group(1).strip()
        title = html.unescape(title)
        title = re.sub(r"\s+", " ", title)
        return title
    return "-"


def check_url(url, timeout):
    try:
        response = requests.get(
            url,
            timeout=timeout,
            verify=False,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )

        if not response.encoding or response.encoding.lower() == "iso-8859-1":
            response.encoding = response.apparent_encoding

        status_code = response.status_code
        title = extract_title(response.text)
        length = len(response.content)
        server = response.headers.get("Server", "-")
        final_url = response.url
        content_type = response.headers.get("Content-Type", "-")

        return {
            "url": url,
            "status": str(status_code),
            "title": title,
            "length": str(length),
            "server": server,
            "final_url": final_url,
            "content_type": content_type,
        }

    except requests.exceptions.Timeout:
        return {
            "url": url,
            "status": "ERROR",
            "title": "timeout",
            "length": "0",
            "server": "-",
            "final_url": "-",
            "content_type": "-",
        }

    except requests.exceptions.ConnectionError:
        return {
            "url": url,
            "status": "ERROR",
            "title": "connection_error",
            "length": "0",
            "server": "-",
            "final_url": "-",
            "content_type": "-",
        }

    except requests.exceptions.RequestException as exc:
        return {
            "url": url,
            "status": "ERROR",
            "title": str(exc),
            "length": "0",
            "server": "-",
            "final_url": "-",
            "content_type": "-",
        }
