from .thirdparty_providers import detect_with_providers


def should_run_thirdparty_fingerprints(result, evidence, noise_flags):
    status = str(result.get("status", ""))
    content_type = str(result.get("content_type", "")).lower()
    preview_text = str(evidence.get("preview_text", "")).strip()
    enable_thirdparty_fingerprints = bool(
        result.get("enable_thirdparty_fingerprints", False)
    )

    if not enable_thirdparty_fingerprints:
        return False

    if status not in {"200", "401", "403"}:
        return False

    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        return False

    if not preview_text:
        return False

    if {"soft-404", "waf-page", "redirect-placeholder"} & set(noise_flags):
        return False

    return True


def run_thirdparty_fingerprints(result, evidence, noise_flags, providers=None):
    if not should_run_thirdparty_fingerprints(result, evidence, noise_flags):
        return []

    return detect_with_providers(result, evidence, providers)
