from .html_report import save_results_html
from .output_helpers import (
    DEFAULT_OUTPUT_FORMATS,
    ensure_output_dir,
    get_output_path,
)
from .output_writers import save_results_csv, save_results_json, save_results_txt


def save_results(
    output_dir,
    base_name,
    results,
    output_formats=None,
    only_alive=False,
    scanned_total=None,
):
    if output_formats is None:
        output_formats = DEFAULT_OUTPUT_FORMATS

    output_dir_path = ensure_output_dir(output_dir)
    output_files = []

    for output_format in output_formats:
        output_path = get_output_path(output_dir_path, base_name, output_format)
        if output_format == "html":
            save_results_html(output_path, results, scanned_total, only_alive)
        elif output_format == "csv":
            save_results_csv(output_path, results, only_alive)
        elif output_format == "txt":
            save_results_txt(output_path, results, only_alive)
        elif output_format == "json":
            save_results_json(output_path, results, only_alive)
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

        output_files.append(str(output_path))

    return output_files
