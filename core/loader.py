from .constants import DEFAULT_URL_SCHEME, SUPPORTED_URL_SCHEMES, UTF8_BOM


def normalize_url(raw_url):
    url = raw_url.strip()
    url = url.lstrip(UTF8_BOM)

    if not url:
        return ""

    if not url.startswith(SUPPORTED_URL_SCHEMES):
        url = DEFAULT_URL_SCHEME + url

    return url

def load_urls(input_file):
    urls = []
    seen = set()

    with open(input_file, "r", encoding="utf-8") as file_obj:
        for line in file_obj:
            url = normalize_url(line)

            if not url:
                continue

            if url in seen:
                continue

            seen.add(url)
            urls.append(url)

    return urls
