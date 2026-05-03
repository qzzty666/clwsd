import csv
import json


FIELDNAMES = [
    "url",
    "status",
    "title",
    "length",
    "server",
    "final_url",
    "content_type",
]


def filter_results(results, only_alive=False):
    if not only_alive:
        return results

    filtered_results = []
    for item in results:
        if item["status"] == "ERROR":
            continue
        filtered_results.append(item)
    return filtered_results


def save_results_txt(output_file, results, only_alive=False):
    filtered_results = filter_results(results, only_alive)

    with open(output_file, "w", encoding="utf-8") as file_obj:
        for item in filtered_results:
            line = (
                f"{item['url']} | "
                f"{item['status']} | "
                f"{item['title']} | "
                f"{item['length']} | "
                f"{item['server']} | "
                f"{item['final_url']} | "
                f"{item['content_type']}"
            )
            file_obj.write(line + "\n")


def save_results_csv(output_file, results, only_alive=False):
    filtered_results = filter_results(results, only_alive)

    with open(output_file, "w", encoding="utf-8-sig", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=FIELDNAMES)
        writer.writeheader()

        for item in filtered_results:
            writer.writerow(item)


def save_results_json(output_file, results, only_alive=False):
    filtered_results = filter_results(results, only_alive)

    with open(output_file, "w", encoding="utf-8") as file_obj:
        json.dump(filtered_results, file_obj, ensure_ascii=False, indent=4)


def save_results(output_file, results, output_format="txt", only_alive=False):
    if output_format == "txt":
        save_results_txt(output_file, results, only_alive)
    elif output_format == "csv":
        save_results_csv(output_file, results, only_alive)
    elif output_format == "json":
        save_results_json(output_file, results, only_alive)
    else:
        raise ValueError(f"不支持的输出格式: {output_format}")
