TECHNOLOGY_CATEGORY_WEIGHTS = {
    "cms": 90,
    "panel": 88,
    "surface": 86,
    "editor": 78,
    "framework": 72,
    "middleware": 70,
    "language": 62,
    "server": 55,
    "site": 50,
    "business": 48,
    "unknown": 40,
}

CONFIDENCE_WEIGHTS = {
    "high": 18,
    "medium": 10,
    "low": 4,
}


def merge_technology_details(*detail_groups):
    merged_details = []
    merged_names = []
    detail_index = {}

    for details in detail_groups:
        for detail in details or []:
            name = str(detail.get("name", "")).strip()
            if not name:
                continue

            normalized_detail = {
                "name": name,
                "category": str(detail.get("category", "unknown")).strip() or "unknown",
                "confidence": str(detail.get("confidence", "low")).strip() or "low",
                "source": str(detail.get("source", "")).strip(),
                "matched": str(detail.get("matched", "")).strip(),
                "score": 0,
            }

            if name not in detail_index:
                detail_index[name] = normalized_detail
                merged_details.append(normalized_detail)
                merged_names.append(name)
                continue

            existing_detail = detail_index[name]
            existing_detail["confidence"] = choose_higher_confidence(
                existing_detail.get("confidence", "low"),
                normalized_detail["confidence"],
            )

            if not existing_detail.get("category") or existing_detail["category"] == "unknown":
                existing_detail["category"] = normalized_detail["category"]

            if normalized_detail["source"]:
                existing_source = existing_detail.get("source", "")
                if existing_source:
                    source_parts = set(part.strip() for part in existing_source.split(",") if part.strip())
                    if normalized_detail["source"] not in source_parts:
                        existing_detail["source"] = f"{existing_source},{normalized_detail['source']}"
                else:
                    existing_detail["source"] = normalized_detail["source"]

            if normalized_detail["matched"]:
                existing_matched = existing_detail.get("matched", "")
                if existing_matched:
                    matched_parts = set(part.strip() for part in existing_matched.split(" | ") if part.strip())
                    if normalized_detail["matched"] not in matched_parts:
                        existing_detail["matched"] = f"{existing_matched} | {normalized_detail['matched']}"
                else:
                    existing_detail["matched"] = normalized_detail["matched"]

    for detail in merged_details:
        detail["score"] = calculate_technology_score(detail)

    merged_details.sort(
        key=lambda item: (
            -item.get("score", 0),
            item.get("category", ""),
            item.get("name", ""),
        )
    )
    merged_names = [item["name"] for item in merged_details]

    return merged_names, merged_details


def choose_higher_confidence(left, right):
    confidence_order = {"low": 0, "medium": 1, "high": 2}
    left_score = confidence_order.get(left, 0)
    right_score = confidence_order.get(right, 0)
    if right_score > left_score:
        return right
    return left


def calculate_technology_score(detail):
    category = str(detail.get("category", "unknown")).strip() or "unknown"
    confidence = str(detail.get("confidence", "low")).strip() or "low"
    source_text = str(detail.get("source", "")).strip()

    score = TECHNOLOGY_CATEGORY_WEIGHTS.get(category, TECHNOLOGY_CATEGORY_WEIGHTS["unknown"])
    score += CONFIDENCE_WEIGHTS.get(confidence, CONFIDENCE_WEIGHTS["low"])

    source_parts = [part.strip() for part in source_text.split(",") if part.strip()]
    if len(source_parts) > 1:
        score += 12

    if any(part.startswith("external:") for part in source_parts) and any(
        not part.startswith("external:") for part in source_parts
    ):
        score += 8

    return score


def split_primary_and_secondary_technologies(details, max_primary=3):
    primary_items = []
    secondary_items = []

    for detail in details:
        category = detail.get("category", "unknown")
        score = detail.get("score", 0)

        if len(primary_items) < max_primary and (
            category in {"cms", "panel", "surface", "editor", "framework", "middleware"}
            or score >= 85
        ):
            primary_items.append(detail)
        else:
            secondary_items.append(detail)

    if not primary_items and details:
        primary_items.append(details[0])
        secondary_items = details[1:]

    return primary_items, secondary_items
