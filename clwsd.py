import argparse
import urllib3
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

from core.analyzer import analyze_result, filter_results, sort_results
from core.checker import check_url
from core.display import (
    finish_progress,
    print_banner,
    print_progress,
    print_result,
    print_summary,
)
from core.loader import load_urls
from core.output import save_results

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "4.1.0"


def parse_header_values(header_values):
    parsed_headers = {}
    for header_item in header_values:
        if ":" not in header_item:
            raise ValueError(f"请求头格式错误: {header_item}")

        key, value = header_item.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key or not value:
            raise ValueError(f"请求头格式错误: {header_item}")

        parsed_headers[key] = value

    return parsed_headers


def build_request_options(args):
    request_options = {}

    if args.header:
        request_options["headers"] = parse_header_values(args.header)

    if args.cookie:
        request_options["cookie"] = args.cookie.strip()

    if args.proxy:
        request_options["proxy"] = args.proxy.strip()

    request_options["enable_thirdparty_fingerprints"] = bool(
        getattr(args, "thirdparty_fingerprints", False)
    )

    return request_options


def build_parser():
    parser = argparse.ArgumentParser(
        description="Web 存活探测工具",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=99
        ),
    )
    parser.add_argument("-i", "--input", required=True, help="输入URL文件")
    parser.add_argument("-o", "--output", default="alive", help="输出文件基础名")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="超时时间,默认5秒")
    parser.add_argument("--all", action="store_true", help="显示并保存全部结果")
    parser.add_argument("-w", "--workers", type=int, default=30, help="线程数,默认30")
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        default=[],
        help="自定义请求头,可重复使用,格式为 Key: Value",
    )
    parser.add_argument("-C", "--cookie", default="", help="自定义Cookie字符串")
    parser.add_argument(
        "--proxy",
        default="",
        help="代理地址,例如 http://127.0.0.1:8080",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="output_formats",
        choices=["html", "csv", "txt", "json"],
        nargs="+",
        default=["html", "csv"],
        help="输出格式:html/csv/txt/json,默认html csv",
    )
    parser.add_argument(
        "--thirdparty-fingerprints",
        action="store_true",
        help="启用可选第三方技术指纹增强,未安装依赖时会自动跳过",
    )
    return parser

def run_scan(urls, timeout, workers, request_options=None, on_result=None):
    results = []
    inflight_limit = max(workers * 3, workers)
    completed_count = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        url_iter = iter(urls)
        pending_futures = set()

        for _ in range(min(inflight_limit, len(urls))):
            try:
                url = next(url_iter)
            except StopIteration:
                break
            pending_futures.add(
                executor.submit(check_url, url, timeout, request_options)
            )

        while pending_futures:
            completed_futures, pending_futures = wait(
                pending_futures,
                return_when=FIRST_COMPLETED,
            )

            for future in completed_futures:
                try:
                    result = future.result()
                except Exception as exc:
                    print(f"任务异常：{exc}")
                    continue

                results.append(result)
                completed_count += 1

                if on_result is not None:
                    on_result(result, completed_count, len(urls))

                try:
                    next_url = next(url_iter)
                except StopIteration:
                    continue

                pending_futures.add(
                    executor.submit(check_url, next_url, timeout, request_options)
                )

    return results

def validate_args(args):
    if args.timeout < 1:
        raise ValueError("超时时间必须大于等于1秒")

    if args.workers < 1:
        raise ValueError("线程数必须大于等于1")

def main():
    print_banner(VERSION)

    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_args(args)

        urls = load_urls(args.input)
        request_options = build_request_options(args)
        raw_results = []
        analyzed_results = []
        kept_results = []

        def handle_result(raw_result, completed_count, total_count):
            analyzed_result = analyze_result(raw_result)
            raw_results.append(raw_result)
            analyzed_results.append(analyzed_result)

            should_keep = args.all or analyzed_result.get("is_alive", False)
            if should_keep:
                kept_results.append(analyzed_result)
                print_result(analyzed_result, completed_count, total_count)
            else:
                print_progress(completed_count, total_count, len(kept_results))

        run_scan(
            urls,
            args.timeout,
            args.workers,
            request_options,
            on_result=handle_result,
        )
        finish_progress()

        sorted_results = sort_results(filter_results(analyzed_results, args.all))

        output_files = save_results(
            "result",
            args.output,
            sorted_results,
            args.output_formats,
            scanned_total=len(raw_results),
        )

        print_summary(raw_results, sorted_results, output_files, args.all)

    except ValueError as exc:
        print(f"参数错误:{exc}")


if __name__ == "__main__":
    main()
