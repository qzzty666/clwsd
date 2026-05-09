import csv
import json

from .output_helpers import (
    OUTPUT_FIELDNAMES,
    filter_results,
    format_fingerprints,
    format_priority,
)


def build_txt_lines(results):
    lines = []
    for item in results:
        lines.append(
            f"网站: {item.get('url', '-')} | "
            f"响应码: {item.get('status', '-')} | "
            f"标题: {item.get('title', '-')} | "
            f"指纹标签: {format_fingerprints(item)} | "
            f"优先级: {format_priority(item)}"
        )
    return "\n".join(lines)


def save_results_txt(output_file, results, only_alive=False):
    filtered_results = filter_results(results, only_alive)

    with open(output_file, "w", encoding="utf-8") as file_obj:
        file_obj.write(build_txt_lines(filtered_results))
        file_obj.write("\n")


def save_results_csv(output_file, results, only_alive=False):
    filtered_results = filter_results(results, only_alive)

    with open(output_file, "w", encoding="utf-8-sig", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()

        for item in filtered_results:
            writer.writerow(
                {
                    "网站": item.get("url", "-"),
                    "响应码": item.get("status", "-"),
                    "标题": item.get("title", "-"),
                    "指纹标签": format_fingerprints(item),
                    "优先级": format_priority(item),
                }
            )


def save_results_json(output_file, results, only_alive=False):
    filtered_results = filter_results(results, only_alive)

    json_results = []
    for item in filtered_results:
        json_results.append(
            {
                "网站": item.get("url", "-"),
                "响应码": item.get("status", "-"),
                "标题": item.get("title", "-"),
                "指纹标签": format_fingerprints(item),
                "优先级": format_priority(item),
            }
        )

    with open(output_file, "w", encoding="utf-8") as file_obj:
        json.dump(json_results, file_obj, ensure_ascii=False, indent=4)
