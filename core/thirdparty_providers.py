def import_python_wappalyzer():
    try:
        from Wappalyzer import Wappalyzer, WebPage
    except ImportError:
        return None, None
    return Wappalyzer, WebPage


def map_confidence_level(value):
    try:
        score = int(value)
    except (TypeError, ValueError):
        return "medium"

    if score >= 75:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def build_provider_headers(result, evidence):
    headers = {}

    server = str(evidence.get("server", "")).strip()
    if server and server != "-":
        headers["Server"] = server

    x_powered_by = str(result.get("x_powered_by", "")).strip()
    if x_powered_by and x_powered_by != "-":
        headers["X-Powered-By"] = x_powered_by

    www_authenticate = str(result.get("www_authenticate", "")).strip()
    if www_authenticate and www_authenticate != "-":
        headers["WWW-Authenticate"] = www_authenticate

    return headers


def detect_with_python_wappalyzer(result, evidence):
    Wappalyzer, WebPage = import_python_wappalyzer()
    if not Wappalyzer or not WebPage:
        return []

    page_url = str(result.get("final_url") or result.get("url") or "").strip()
    page_html = str(evidence.get("preview_text", ""))
    page_headers = build_provider_headers(result, evidence)

    if not page_url or not page_html:
        return []

    try:
        webpage = WebPage(page_url, page_html, page_headers)
        analyzer = Wappalyzer.latest()
    except Exception:
        return []

    details = []
    try:
        if hasattr(analyzer, "analyze_with_versions_and_categories"):
            matches = analyzer.analyze_with_versions_and_categories(webpage)
        elif hasattr(analyzer, "analyze_with_categories"):
            matches = analyzer.analyze_with_categories(webpage)
        else:
            matches = {name: {} for name in analyzer.analyze(webpage)}
    except Exception:
        return []

    for technology_name, match_data in (matches or {}).items():
        categories = match_data.get("categories", []) if isinstance(match_data, dict) else []
        versions = match_data.get("versions", []) if isinstance(match_data, dict) else []
        confidence_value = None
        if hasattr(analyzer, "get_confidence"):
            try:
                confidence_value = analyzer.get_confidence(technology_name)
            except Exception:
                confidence_value = None

        matched_text = "wappalyzer"
        if versions:
            matched_text = f"versions:{','.join(str(item) for item in versions if item)}"

        details.append(
            {
                "name": str(technology_name),
                "category": normalize_provider_category(categories),
                "confidence": map_confidence_level(confidence_value),
                "source": "external:python-wappalyzer",
                "matched": matched_text,
            }
        )

    return details


def normalize_provider_category(categories):
    if not categories:
        return "unknown"

    first_category = str(categories[0]).strip().lower()
    if "cms" in first_category:
        return "cms"
    if "server" in first_category or "proxy" in first_category:
        return "server"
    if "framework" in first_category:
        return "framework"
    if "language" in first_category:
        return "language"
    if "panel" in first_category or "admin" in first_category:
        return "panel"
    return first_category.replace(" ", "-") or "unknown"


def get_default_providers():
    return [detect_with_python_wappalyzer]


def detect_with_providers(result, evidence, providers=None):
    if providers is None:
        providers = get_default_providers()

    detected_items = []
    for provider in providers:
        try:
            provider_items = provider(result, evidence) or []
        except Exception:
            provider_items = []
        for item in provider_items:
            if isinstance(item, dict):
                detected_items.append(item)

    return detected_items
