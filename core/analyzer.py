from .constants import (
    ALIVE_STATUS_CODES,
    HTML_CONTENT_TYPES,
    PRIORITY_ORDER,
    STATUS_BASE_SCORES,
    TITLE_KEYWORD_SCORES,
    URL_KEYWORD_SCORES,
)
from .fingerprinter import identify_fingerprints, is_generic_auth_gateway_profile


def collect_keyword_score(text, rules, source_name):
    lowered_text = text.lower()
    total_score = 0
    reasons = []
    matched_keywords = set()

    for keyword, score in rules:
        if keyword in lowered_text and keyword not in matched_keywords:
            matched_keywords.add(keyword)
            total_score += score
            reasons.append(f"{source_name}:{keyword}+{score}")

    return total_score, reasons


def get_priority_level(is_alive, priority_score):
    if not is_alive:
        return "dead"
    if priority_score >= 80:
        return "high"
    if priority_score >= 55:
        return "medium"
    return "low"


def analyze_result(result):
    analyzed_result = dict(result)

    status = analyzed_result.get("status", "ERROR")
    title = analyzed_result.get("title", "")
    url = analyzed_result.get("url", "")
    final_url = analyzed_result.get("final_url", "")
    content_type = analyzed_result.get("content_type", "").lower()

    if title == "-":
        title = ""

    is_alive = status in ALIVE_STATUS_CODES
    priority_score = 0
    priority_reasons = []
    fingerprints = []
    fingerprint_evidence = {}
    technology_matches = []
    technology_details = []
    primary_technologies = []
    secondary_technologies = []
    thirdparty_technology_details = []
    noise_flags = []

    if is_alive:
        base_score = STATUS_BASE_SCORES.get(status, 0)
        priority_score += base_score
        priority_reasons.append(f"status:{status}+{base_score}")

        if any(item in content_type for item in HTML_CONTENT_TYPES):
            priority_score += 10
            priority_reasons.append("content_type:html+10")

        title_score, title_reasons = collect_keyword_score(
            title, TITLE_KEYWORD_SCORES, "title"
        )
        priority_score += title_score
        priority_reasons.extend(title_reasons)

        url_score, url_reasons = collect_keyword_score(
            f"{url} {final_url}", URL_KEYWORD_SCORES, "url"
        )
        priority_score += url_score
        priority_reasons.extend(url_reasons)

        fingerprint_result = identify_fingerprints(analyzed_result)
        fingerprints = fingerprint_result["fingerprints"]
        fingerprint_evidence = fingerprint_result["fingerprint_evidence"]
        technology_matches = fingerprint_result["technology_matches"]
        technology_details = fingerprint_result.get("technology_details", [])
        primary_technologies = fingerprint_result.get("primary_technologies", [])
        secondary_technologies = fingerprint_result.get("secondary_technologies", [])
        thirdparty_technology_details = fingerprint_result.get("thirdparty_technology_details", [])
        noise_flags = fingerprint_result["noise_flags"]
        priority_score += fingerprint_result["fingerprint_score"]
        priority_reasons.extend(fingerprint_result["fingerprint_reasons"])

        if is_generic_auth_gateway_profile(analyzed_result, fingerprints) and (
            "webvpn" in f"{url} {final_url}".lower()
        ):
            priority_score -= 20
            priority_reasons.append("tune:webvpn-auth-gateway-20")

    priority_level = get_priority_level(is_alive, priority_score)

    analyzed_result["is_alive"] = is_alive
    analyzed_result["fingerprints"] = fingerprints
    analyzed_result["fingerprint_evidence"] = fingerprint_evidence
    analyzed_result["technology_matches"] = technology_matches
    analyzed_result["technology_details"] = technology_details
    analyzed_result["primary_technologies"] = primary_technologies
    analyzed_result["secondary_technologies"] = secondary_technologies
    analyzed_result["thirdparty_technology_details"] = thirdparty_technology_details
    analyzed_result["noise_flags"] = noise_flags
    analyzed_result["priority_score"] = priority_score
    analyzed_result["priority_level"] = priority_level
    analyzed_result["priority_reason"] = (
        "; ".join(priority_reasons) if priority_reasons else "not_alive"
    )

    return analyzed_result


def analyze_results(results):
    analyzed_results = []
    for item in results:
        analyzed_results.append(analyze_result(item))
    return analyzed_results


def filter_results(results, include_all=False):
    if include_all:
        return results

    kept_results = []
    for item in results:
        if item.get("is_alive", False):
            kept_results.append(item)
    return kept_results


def sort_results(results):
    return sorted(
        results,
        key=lambda item: (
            PRIORITY_ORDER.get(item.get("priority_level", "dead"), 3),
            -item.get("priority_score", 0),
            item.get("status", ""),
            item.get("url", ""),
        ),
    )
