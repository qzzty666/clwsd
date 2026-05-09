import requests
from .constants import MAX_TIMEOUT_RETRIES
from .favicon import resolve_favicon_fingerprint
from .http_client import make_head_request, make_request, should_try_head_first
from .response_parser import (
    decode_preview_text,
    extract_title,
    read_response_preview,
    should_fallback_to_get,
)


def flatten_headers(headers):
    parts = []
    for key, value in headers.items():
        parts.append(f"{key}: {value}")
    return " | ".join(parts)


def build_success_result(url, response, preview_bytes, timeout, request_options=None):
    preview_text = decode_preview_text(response, preview_bytes)
    content_length = response.headers.get("Content-Length")
    enable_thirdparty_fingerprints = bool(
        (request_options or {}).get("enable_thirdparty_fingerprints", False)
    )
    favicon_info = resolve_favicon_fingerprint(
        url,
        response.url,
        preview_text,
        timeout,
        request_options,
    )

    return {
        "url": url,
        "status": str(response.status_code),
        "title": extract_title(preview_text),
        "length": content_length if content_length else str(len(preview_bytes)),
        "server": response.headers.get("Server", "-"),
        "final_url": response.url,
        "content_type": response.headers.get("Content-Type", "-"),
        "x_powered_by": response.headers.get("X-Powered-By", "-"),
        "www_authenticate": response.headers.get("WWW-Authenticate", "-"),
        "header_text": flatten_headers(response.headers),
        "preview_text": preview_text,
        "favicon_hash": favicon_info["favicon_hash"],
        "favicon_md5": favicon_info["favicon_md5"],
        "favicon_path": favicon_info["favicon_path"],
        "favicon_url": favicon_info["favicon_url"],
        "error_type": "-",
        "enable_thirdparty_fingerprints": enable_thirdparty_fingerprints,
    }


def build_head_only_result(url, response):
    content_length = response.headers.get("Content-Length")

    return {
        "url": url,
        "status": str(response.status_code),
        "title": "-",
        "length": content_length if content_length else "0",
        "server": response.headers.get("Server", "-"),
        "final_url": response.url,
        "content_type": response.headers.get("Content-Type", "-"),
        "x_powered_by": response.headers.get("X-Powered-By", "-"),
        "www_authenticate": response.headers.get("WWW-Authenticate", "-"),
        "header_text": flatten_headers(response.headers),
        "preview_text": "",
        "favicon_hash": "",
        "favicon_md5": "",
        "favicon_path": "",
        "favicon_url": "",
        "error_type": "-",
        "enable_thirdparty_fingerprints": False,
    }


def build_error_result(url, error_title, error_type=None):
    return {
        "url": url,
        "status": "ERROR",
        "title": error_title,
        "length": "0",
        "server": "-",
        "final_url": "-",
        "content_type": "-",
        "x_powered_by": "-",
        "www_authenticate": "-",
        "header_text": "",
        "preview_text": "",
        "favicon_hash": "",
        "favicon_md5": "",
        "favicon_path": "",
        "favicon_url": "",
        "error_type": error_type if error_type else error_title,
        "enable_thirdparty_fingerprints": False,
    }


def check_url(url, timeout, request_options=None):
    for attempt in range(MAX_TIMEOUT_RETRIES):
        response = None
        head_response = None
        try:
            if should_try_head_first(url):
                head_response = make_head_request(url, timeout, request_options)
                if not should_fallback_to_get(head_response):
                    return build_head_only_result(url, head_response)

            response = make_request(url, timeout, request_options)
            preview_bytes = read_response_preview(response)
            return build_success_result(
                url,
                response,
                preview_bytes,
                timeout,
                request_options,
            )

        except requests.exceptions.Timeout:
            if attempt == MAX_TIMEOUT_RETRIES - 1:
                return build_error_result(url, "timeout", "timeout")

        except requests.exceptions.SSLError:
            return build_error_result(url, "ssl_error", "ssl_error")

        except requests.exceptions.ConnectionError:
            return build_error_result(url, "connection_error", "connection_error")

        except requests.exceptions.TooManyRedirects:
            return build_error_result(url, "too_many_redirects", "too_many_redirects")

        except requests.exceptions.RequestException as exc:
            return build_error_result(url, str(exc), "request_exception")

        finally:
            if head_response is not None:
                head_response.close()
            if response is not None:
                response.close()
