import re

from .constants import (
    ASSET_PATH_FINGERPRINT_RULES,
    BODY_FINGERPRINT_RULES,
    FAVICON_PATH_FINGERPRINT_RULES,
    HEADER_FINGERPRINT_RULES,
    SERVER_FINGERPRINT_RULES,
    TECHNOLOGY_EVIDENCE_RULES,
    TECHNOLOGY_FAVICON_HASH_RULES,
    TECHNOLOGY_TAG_RULES,
    TITLE_FINGERPRINT_RULES,
    URL_FINGERPRINT_RULES,
)
from .technology_merge import merge_technology_details, split_primary_and_secondary_technologies
from .thirdparty_fingerprints import run_thirdparty_fingerprints

ASSET_PATH_PATTERN = re.compile(r"""(?:src|href)=["']([^"']+)["']""", re.IGNORECASE)
FAVICON_PATH_PATTERN = re.compile(
    r"""<link[^>]+rel=["'][^"']*icon[^"']*["'][^>]+href=["']([^"']+)["']""",
    re.IGNORECASE,
)
META_GENERATOR_PATTERN = re.compile(
    r"""<meta[^>]+name=["']generator["'][^>]+content=["']([^"']+)["']""",
    re.IGNORECASE,
)

TECH_TAG_LABELS = {
    "openresty": "OpenResty",
    "nginx": "Nginx",
    "iis": "Microsoft IIS",
    "apache": "Apache",
    "tomcat": "Tomcat",
    "jetty": "Jetty",
    "asp-net": "ASP.NET",
    "php": "PHP",
    "jsp": "JSP",
    "swagger-ui": "Swagger UI",
    "jenkins": "Jenkins",
    "grafana": "Grafana",
    "phpmyadmin": "phpMyAdmin",
    "druid-monitor": "Druid Monitor",
    "prometheus": "Prometheus",
    "kindeditor": "KindEditor",
    "ueditor": "UEditor",
    "ckeditor": "CKEditor",
    "tinymce": "TinyMCE",
    "tomcat-manager": "Tomcat Manager",
    "edu-system": "Edu System",
}

TECH_TAG_RULE_INDEX = {item["tag"]: item for item in TECHNOLOGY_TAG_RULES}

NOISE_FLAG_SET = {
    "generic-default-page",
    "soft-404",
    "waf-page",
    "redirect-placeholder",
}


def collect_fingerprints(text, rules, source_name):
    lowered_text = text.lower()
    tags = []
    reasons = []
    score = 0
    seen_tags = set()

    for keyword, tag, tag_score in rules:
        if keyword in lowered_text and tag not in seen_tags:
            seen_tags.add(tag)
            tags.append(tag)
            score += tag_score
            reasons.append(f"{source_name}:{tag}+{tag_score}")

    return tags, score, reasons


def merge_fingerprint_data(*fingerprint_parts):
    merged_tags = []
    merged_reasons = []
    merged_score = 0
    seen_tags = set()

    for tags, score, reasons in fingerprint_parts:
        merged_score += score
        merged_reasons.extend(reasons)
        for tag in tags:
            if tag not in seen_tags:
                seen_tags.add(tag)
                merged_tags.append(tag)

    return merged_tags, merged_score, merged_reasons


def collect_path_fingerprints(paths, rules, source_name):
    if not paths:
        return [], 0, []
    return collect_fingerprints(" ".join(paths), rules, source_name)


def extract_asset_paths(preview_text):
    return ASSET_PATH_PATTERN.findall(preview_text)


def extract_favicon_paths(preview_text):
    return FAVICON_PATH_PATTERN.findall(preview_text)


def extract_meta_generator(preview_text):
    matched = META_GENERATOR_PATTERN.search(preview_text)
    if not matched:
        return ""
    return matched.group(1).strip()


def append_unique(values, seen_values, value):
    if value and value not in seen_values:
        seen_values.add(value)
        values.append(value)


def append_technology_detail(details, seen_names, rule_name, category, confidence, source, matched_value):
    if not rule_name or rule_name in seen_names:
        return

    seen_names.add(rule_name)
    details.append(
        {
            "name": rule_name,
            "category": category,
            "confidence": confidence,
            "source": source,
            "matched": matched_value,
        }
    )


def collect_technology_matches_from_text(text, rules, matched, details, detail_seen, source_name):
    lowered_text = text.lower()
    matched_set = set(matched)
    for rule in rules:
        keyword = rule["keyword"]
        technology_name = rule["name"]
        if keyword in lowered_text:
            append_unique(matched, matched_set, technology_name)
            append_technology_detail(
                details,
                detail_seen,
                technology_name,
                rule["category"],
                rule["confidence"],
                source_name,
                keyword,
            )


def collect_technology_matches_from_paths(paths, rules, matched, details, detail_seen, source_name):
    if not paths:
        return

    matched_set = set(matched)
    for path in paths:
        lowered_path = path.lower()
        for rule in rules:
            keyword = rule["keyword"]
            technology_name = rule["name"]
            if keyword in lowered_path:
                append_unique(matched, matched_set, technology_name)
                append_technology_detail(
                    details,
                    detail_seen,
                    technology_name,
                    rule["category"],
                    rule["confidence"],
                    source_name,
                    path,
                )


def build_fingerprint_evidence(result):
    preview_text = str(result.get("preview_text", ""))
    asset_paths = extract_asset_paths(preview_text)
    favicon_paths = extract_favicon_paths(preview_text)
    meta_generator = extract_meta_generator(preview_text)

    header_text = str(result.get("header_text", ""))
    if not header_text:
        header_parts = []
        server = str(result.get("server", "")).strip()
        www_authenticate = str(result.get("www_authenticate", "")).strip()
        x_powered_by = str(result.get("x_powered_by", "")).strip()

        if server and server != "-":
            header_parts.append(f"Server: {server}")
        if www_authenticate and www_authenticate != "-":
            header_parts.append(f"WWW-Authenticate: {www_authenticate}")
        if x_powered_by and x_powered_by != "-":
            header_parts.append(f"X-Powered-By: {x_powered_by}")

        header_text = " | ".join(header_parts)

    return {
        "server": str(result.get("server", "")),
        "title": str(result.get("title", "")),
        "url_text": f"{result.get('url', '')} {result.get('final_url', '')}",
        "header_text": header_text,
        "preview_text": preview_text,
        "meta_generator": meta_generator,
        "asset_paths": asset_paths,
        "favicon_paths": favicon_paths,
        "favicon_hash": str(result.get("favicon_hash", "")),
        "favicon_md5": str(result.get("favicon_md5", "")),
        "favicon_path": str(result.get("favicon_path", "")),
        "favicon_url": str(result.get("favicon_url", "")),
    }


def build_technology_matches(tags, evidence):
    technology_matches = []
    technology_seen = set()
    technology_details = []
    detail_seen = set()
    noise_flags = []

    for tag in tags:
        technology_name = TECH_TAG_LABELS.get(tag)
        if technology_name:
            append_unique(technology_matches, technology_seen, technology_name)
            tag_rule = TECH_TAG_RULE_INDEX.get(tag, {})
            append_technology_detail(
                technology_details,
                detail_seen,
                technology_name,
                tag_rule.get("category", "unknown"),
                tag_rule.get("confidence", "low"),
                "tag",
                tag,
            )
        if tag in NOISE_FLAG_SET:
            noise_flags.append(tag)

    collect_technology_matches_from_text(
        evidence.get("meta_generator", ""),
        TECHNOLOGY_EVIDENCE_RULES["meta_generator"],
        technology_matches,
        technology_details,
        detail_seen,
        "meta_generator",
    )

    collect_technology_matches_from_text(
        evidence.get("header_text", ""),
        TECHNOLOGY_EVIDENCE_RULES["header_text"],
        technology_matches,
        technology_details,
        detail_seen,
        "header",
    )

    collect_technology_matches_from_paths(
        evidence.get("asset_paths", []),
        TECHNOLOGY_EVIDENCE_RULES["asset_paths"],
        technology_matches,
        technology_details,
        detail_seen,
        "asset_path",
    )

    collect_technology_matches_from_paths(
        evidence.get("favicon_paths", []),
        TECHNOLOGY_EVIDENCE_RULES["favicon_paths"],
        technology_matches,
        technology_details,
        detail_seen,
        "favicon_path",
    )
    technology_seen = set(technology_matches)

    favicon_hash = evidence.get("favicon_hash", "")
    favicon_rule = TECHNOLOGY_FAVICON_HASH_RULES.get(favicon_hash)
    if favicon_rule:
        technology_name = favicon_rule["name"]
        append_unique(technology_matches, technology_seen, technology_name)
        append_technology_detail(
            technology_details,
            detail_seen,
            technology_name,
            favicon_rule["category"],
            favicon_rule["confidence"],
            "favicon_hash",
            favicon_hash,
        )

    return technology_matches, technology_details, noise_flags


def tune_fingerprint_score(result, tags, base_score, reasons):
    adjusted_score = base_score
    adjusted_reasons = list(reasons)
    is_generic_auth_gateway = is_generic_auth_gateway_profile(result, tags)
    is_generic_default_page = is_generic_default_page_profile(result, tags)
    tags_set = set(tags)

    if is_generic_auth_gateway:
        gateway_cap = 18
        if adjusted_score > gateway_cap:
            delta = gateway_cap - adjusted_score
            adjusted_score = gateway_cap
            adjusted_reasons.append(f"tune:generic-auth-cap{delta}")

        adjusted_score -= 45
        adjusted_reasons.append("tune:generic-auth-gateway-45")

    if is_generic_default_page:
        adjusted_score -= 40
        adjusted_reasons.append("tune:generic-default-page-40")

    if "soft-404" in tags_set:
        adjusted_score -= 90
        adjusted_reasons.append("tune:soft-404-90")

    if "waf-page" in tags_set:
        adjusted_score -= 60
        adjusted_reasons.append("tune:waf-page-60")

    if "redirect-placeholder" in tags_set and "login-page" not in tags_set:
        adjusted_score -= 55
        adjusted_reasons.append("tune:redirect-placeholder-55")

    if "tomcat-manager" in tags_set:
        adjusted_score += 20
        adjusted_reasons.append("tune:tomcat-manager+20")

    if "basic-auth" in tags_set:
        adjusted_score += 12
        adjusted_reasons.append("tune:basic-auth+12")

    if {"iis", "asp-net"}.issubset(tags_set):
        adjusted_score += 8
        adjusted_reasons.append("tune:iis-asp-net+8")

    if "admin-console" in tags_set:
        adjusted_score += 18
        adjusted_reasons.append("tune:admin-console+18")

    if "admin-page" in tags_set and "sso" not in tags_set:
        adjusted_score += 10
        adjusted_reasons.append("tune:admin-page+10")

    if "oa" in tags_set and "sso" not in tags_set:
        adjusted_score += 8
        adjusted_reasons.append("tune:oa+8")

    if "directory-listing" in tags_set:
        adjusted_score += 12
        adjusted_reasons.append("tune:directory-listing+12")

    if is_generic_auth_gateway and "password-input" in tags_set:
        adjusted_score -= 18
        adjusted_reasons.append("tune:generic-auth-password-input-18")
    elif "password-input" in tags_set:
        adjusted_score += 12
        adjusted_reasons.append("tune:password-input+12")

    if "upload-form" in tags_set:
        adjusted_score += 8
        adjusted_reasons.append("tune:upload-form+8")

    if {"swagger-ui", "jenkins", "grafana", "phpmyadmin", "druid-monitor", "prometheus"} & tags_set:
        adjusted_score += 16
        adjusted_reasons.append("tune:page-console-surface+16")

    if {"kindeditor", "ueditor", "ckeditor", "tinymce"} & tags_set:
        adjusted_score += 6
        adjusted_reasons.append("tune:rich-editor+6")

    return adjusted_score, adjusted_reasons


def is_generic_auth_gateway_profile(result, tags):
    tags_set = set(tags)
    title_text = str(result.get("title", "")).lower()
    url_text = f"{result.get('url', '')} {result.get('final_url', '')}".lower()
    has_strong_surface = (
        "basic-auth" in tags_set
        or "tomcat-manager" in tags_set
        or "admin-console" in tags_set
        or ("admin-page" in tags_set and "login-page" not in tags_set)
    )

    return (
        "sso" in tags_set
        and not has_strong_surface
        and (
            "统一身份认证" in title_text
            or "webvpn" in url_text
            or "authserver" in url_text
        )
    )


def is_generic_default_page_profile(result, tags):
    tags_set = set(tags)
    title_text = str(result.get("title", "")).lower()
    has_strong_surface = (
        "admin-console" in tags_set
        or "tomcat-manager" in tags_set
        or "directory-listing" in tags_set
    )

    return (
        "generic-default-page" in tags_set
        and not has_strong_surface
        and (
            "welcome to nginx" in title_text
            or "apache2 debian default page" in title_text
            or title_text.strip() == "iis7"
        )
    )


def identify_fingerprints(result):
    evidence = build_fingerprint_evidence(result)

    tags, score, reasons = merge_fingerprint_data(
        collect_fingerprints(evidence["server"], SERVER_FINGERPRINT_RULES, "server"),
        collect_fingerprints(evidence["title"], TITLE_FINGERPRINT_RULES, "title"),
        collect_fingerprints(evidence["url_text"], URL_FINGERPRINT_RULES, "url"),
        collect_fingerprints(
            evidence["header_text"],
            HEADER_FINGERPRINT_RULES,
            "header",
        ),
        collect_fingerprints(evidence["preview_text"], BODY_FINGERPRINT_RULES, "body"),
        collect_path_fingerprints(
            evidence["asset_paths"],
            ASSET_PATH_FINGERPRINT_RULES,
            "asset",
        ),
        collect_path_fingerprints(
            evidence["favicon_paths"],
            FAVICON_PATH_FINGERPRINT_RULES,
            "favicon",
        ),
    )
    adjusted_score, adjusted_reasons = tune_fingerprint_score(result, tags, score, reasons)
    technology_matches, technology_details, noise_flags = build_technology_matches(tags, evidence)
    thirdparty_details = run_thirdparty_fingerprints(result, evidence, noise_flags)
    technology_matches, technology_details = merge_technology_details(
        technology_details,
        thirdparty_details,
    )
    primary_technologies, secondary_technologies = split_primary_and_secondary_technologies(
        technology_details
    )
    return {
        "fingerprints": tags,
        "fingerprint_score": adjusted_score,
        "fingerprint_reasons": adjusted_reasons,
        "fingerprint_evidence": evidence,
        "technology_matches": technology_matches,
        "technology_details": technology_details,
        "primary_technologies": primary_technologies,
        "secondary_technologies": secondary_technologies,
        "thirdparty_technology_details": thirdparty_details,
        "noise_flags": noise_flags,
    }
