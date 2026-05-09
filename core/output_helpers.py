from pathlib import Path
from .constants import DEFAULT_OUTPUT_FORMATS, OUTPUT_FIELDNAMES


def ensure_output_dir(output_dir="result"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return Path(output_dir)


def get_output_path(output_dir, base_name, extension):
    safe_name = Path(base_name).stem
    return Path(output_dir) / f"{safe_name}.{extension}"


def filter_results(results, only_alive=False):
    if not only_alive:
        return results

    filtered_results = []
    for item in results:
        if item.get("is_alive", False):
            filtered_results.append(item)
    return filtered_results


def format_priority(item):
    return item.get("priority_level", "-").upper()


def format_fingerprints(item):
    fingerprints = item.get("fingerprints", [])
    if not fingerprints:
        return "-"
    return ", ".join(fingerprints)
