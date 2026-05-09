import html
import re
from .constants import HTML_CONTENT_TYPES


PREVIEW_BYTES_LIMIT = 32768
POST_TITLE_SAMPLE_LIMIT = 12288
CHUNK_SIZE = 4096
TITLE_END_MARKER = b"</title>"
BODY_END_MARKERS = (b"</body>", b"</form>")

TITLE_PATTERN = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
HEADER_CHARSET_PATTERN = re.compile(r"charset=([\w.-]+)", re.IGNORECASE)
META_CHARSET_PATTERN = re.compile(r"charset=['\"]?([\w.-]+)", re.IGNORECASE)


def extract_title(html_text):
    match = TITLE_PATTERN.search(html_text)
    if match:
        title = match.group(1).strip()
        title = html.unescape(title)
        title = re.sub(r"\s+", " ", title)
        return title
    return "-"


def is_binary_content(content_type):
    lowered_content_type = content_type.lower()
    binary_prefixes = (
        "image/",
        "video/",
        "audio/",
        "font/",
    )
    binary_types = (
        "application/octet-stream",
        "application/pdf",
        "application/zip",
        "application/x-rar-compressed",
        "application/vnd",
    )

    if lowered_content_type.startswith(binary_prefixes):
        return True

    for item in binary_types:
        if item in lowered_content_type:
            return True

    return False


def should_read_preview(content_type):
    lowered_content_type = content_type.lower()

    if not lowered_content_type:
        return True

    if any(item in lowered_content_type for item in HTML_CONTENT_TYPES):
        return True

    likely_non_html_types = (
        "application/json",
        "application/xml",
        "text/xml",
        "text/plain",
        "text/css",
        "application/javascript",
        "text/javascript",
    )

    for item in likely_non_html_types:
        if item in lowered_content_type:
            return False

    return not is_binary_content(lowered_content_type)


def should_fallback_to_get(head_response):
    status_code = head_response.status_code
    content_type = head_response.headers.get("Content-Type", "")

    if status_code in {405, 501}:
        return True

    if should_read_preview(content_type):
        return True

    return False


def read_response_preview(response, limit=PREVIEW_BYTES_LIMIT):
    content_type = response.headers.get("Content-Type", "")
    if not should_read_preview(content_type):
        return b""

    preview_bytes = bytearray()
    total_size = 0
    saw_title_end = False

    for chunk in response.iter_content(chunk_size=CHUNK_SIZE, decode_unicode=False):
        if not chunk:
            continue

        remaining = limit - total_size
        if remaining <= 0:
            break

        chunk_part = chunk[:remaining]
        preview_bytes.extend(chunk_part)
        total_size += len(chunk_part)

        tail = bytes(preview_bytes[-128:]).lower()
        if TITLE_END_MARKER in tail:
            saw_title_end = True

        if total_size >= limit:
            break

        if saw_title_end and total_size >= POST_TITLE_SAMPLE_LIMIT:
            break

        if saw_title_end and any(marker in tail for marker in BODY_END_MARKERS):
            break

    return bytes(preview_bytes)


def detect_encoding(response, preview_bytes):
    if response.encoding and response.encoding.lower() != "iso-8859-1":
        return response.encoding

    content_type = response.headers.get("Content-Type", "")
    header_match = HEADER_CHARSET_PATTERN.search(content_type)
    if header_match:
        return header_match.group(1)

    if preview_bytes:
        preview_head = preview_bytes[:2048].decode("ascii", errors="ignore")
        meta_match = META_CHARSET_PATTERN.search(preview_head)
        if meta_match:
            return meta_match.group(1)

    return "utf-8"


def decode_preview_text(response, preview_bytes):
    if not preview_bytes:
        return ""

    encoding = detect_encoding(response, preview_bytes)
    try:
        return preview_bytes.decode(encoding, errors="ignore")
    except LookupError:
        return preview_bytes.decode("utf-8", errors="ignore")
