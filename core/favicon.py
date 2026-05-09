import base64
import hashlib
import re
from urllib.parse import urljoin

from .http_client import get_session, build_request_options


BASE_HREF_PATTERN = re.compile(r"<base[^>]+href=['\"]([^'\"]+)['\"]", re.IGNORECASE)
FAVICON_LINK_PATTERN = re.compile(
    r"<link[^>]+rel=['\"][^'\"]*icon[^'\"]*['\"][^>]*href=['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)


def extract_favicon_candidates(html_text):
    if not html_text:
        return [], ""

    hrefs = FAVICON_LINK_PATTERN.findall(html_text)
    base_match = BASE_HREF_PATTERN.search(html_text)
    base_href = base_match.group(1).strip() if base_match else ""
    return hrefs, base_href


def decode_data_icon(data_url):
    if not data_url.lower().startswith("data:"):
        return b""

    if "," not in data_url:
        return b""

    _, encoded = data_url.split(",", 1)
    try:
        return base64.b64decode(encoded, validate=False)
    except Exception:
        return b""


def murmurhash3_32(data, seed=0):
    data = bytearray(data)
    length = len(data)
    nblocks = length // 4

    c1 = 0xcc9e2d51
    c2 = 0x1b873593
    h1 = seed & 0xFFFFFFFF

    for block_start in range(0, nblocks * 4, 4):
        k1 = (
            data[block_start]
            | (data[block_start + 1] << 8)
            | (data[block_start + 2] << 16)
            | (data[block_start + 3] << 24)
        )
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF

        h1 ^= k1
        h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
        h1 = (h1 * 5 + 0xe6546b64) & 0xFFFFFFFF

    tail = data[nblocks * 4 :]
    k1 = 0

    if len(tail) == 3:
        k1 ^= tail[2] << 16
    if len(tail) >= 2:
        k1 ^= tail[1] << 8
    if len(tail) >= 1:
        k1 ^= tail[0]
        k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF
        h1 ^= k1

    h1 ^= length
    h1 ^= (h1 >> 16)
    h1 = (h1 * 0x85ebca6b) & 0xFFFFFFFF
    h1 ^= (h1 >> 13)
    h1 = (h1 * 0xc2b2ae35) & 0xFFFFFFFF
    h1 ^= (h1 >> 16)

    if h1 & 0x80000000:
        return -((~h1 + 1) & 0xFFFFFFFF)
    return h1


def calculate_favicon_hashes(data):
    return str(murmurhash3_32(data)), hashlib.md5(data).hexdigest()


def _fetch_bytes(url, timeout, request_options=None):
    session = get_session()
    request_kwargs = build_request_options(timeout, request_options)
    request_kwargs["stream"] = False
    response = session.get(url, **request_kwargs)
    try:
        return response.content
    finally:
        response.close()


def resolve_favicon_fingerprint(page_url, final_url, html_text, timeout, request_options=None):
    hrefs, base_href = extract_favicon_candidates(html_text)
    if not hrefs:
        hrefs = ["/favicon.ico"]

    base_url = final_url or page_url
    if base_href:
        base_url = urljoin(base_url, base_href)

    for href in hrefs[:3]:
        if not href:
            continue

        if href.lower().startswith("data:"):
            data = decode_data_icon(href)
            if not data:
                continue
            favicon_hash, favicon_md5 = calculate_favicon_hashes(data)
            return {
                "favicon_hash": favicon_hash,
                "favicon_md5": favicon_md5,
                "favicon_path": "data:",
                "favicon_url": "",
                "favicon_data": data,
            }

        resolved_url = urljoin(base_url, href)
        try:
            data = _fetch_bytes(resolved_url, timeout, request_options)
        except Exception:
            continue

        if not data:
            continue

        favicon_hash, favicon_md5 = calculate_favicon_hashes(data)
        return {
            "favicon_hash": favicon_hash,
            "favicon_md5": favicon_md5,
            "favicon_path": href,
            "favicon_url": resolved_url,
            "favicon_data": data,
        }

    return {
        "favicon_hash": "",
        "favicon_md5": "",
        "favicon_path": "",
        "favicon_url": "",
        "favicon_data": b"",
    }
