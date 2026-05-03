import argparse
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.checker import check_url
from core.loader import load_urls
from core.output import save_results

from colorama import Fore,Style,init 

init(autoreset=True)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "2.3.0"


def print_banner():
    print(
        rf"""
   ____   _                        _
  / ___| | | __      __  ___    __| |
 | |     | | \ \ /\ / / / __|  / _` |
 | |___  | |  \ V  V /  \__ \ | (_| |
  \____| |_|   \_/\_/   |___/  \__,_|

            Clwsd {VERSION} by 骑猪走天涯
"""
    )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Web 存活探测工具",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=99
        ),
    )
    parser.add_argument("-i", "--input", required=True, help="输入URL文件")
    parser.add_argument("-o", "--output", default="alive.txt", help="输出结果文件")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="超时时间,默认5秒")
    parser.add_argument("-a", "--only-alive", action="store_true", help="仅输出存活目标")
    parser.add_argument("-w", "--workers", type=int, default=10, help="线程数,默认10")
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        choices=["txt", "csv", "json"],
        default="txt",
        help="输出格式:txt/csv/json,默认txt",
    )
    return parser

def colorize_status(status):
    if status == "ERROR":
        return Fore.RED + status +Style.RESET_ALL

    if status.startswith("2"):
        return Fore.GREEN + status + Style.RESET_ALL

    if status.startswith("3"):
        return Fore.YELLOW + status + Style.RESET_ALL
    
    if status.startswith("4") or status.startswith("5"):
        return Fore.RED + status + Style.RESET_ALL

    return status


def print_result(result):
    colored_status = colorize_status(result["status"])

    print(
        f"{result['url']} -> "
        f"{colored_status} | "
        f"{result['title']}"
    )


def run_scan(urls, timeout, workers):
    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []

        for url in urls:
            future = executor.submit(check_url, url, timeout)
            futures.append(future)

        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception as exc:
                print(f"任务异常：{exc}")
                continue

            results.append(result)
            print_result(result)

    return results


def count_alive(results):
    alive_count = 0

    for item in results:
        if item["status"] != "ERROR":
            alive_count += 1

    return alive_count

def validate_args(args):
    if args.timeout < 1:
        raise ValueError("超时时间必须大于等于1秒")

    if args.workers < 1:
        raise ValueError("线程数必须大于等于1")

def main():
    print_banner()

    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_args(args)

        urls = load_urls(args.input)
        results = run_scan(urls, args.timeout, args.workers)

        save_results(args.output, results, args.output_format, args.only_alive)

        print(f"\n探测结束,共{len(results)}个目标，结果已保存到{args.output}")

        if args.only_alive:
            alive_count = count_alive(results)
            print(f"仅输出存活目标：{alive_count}个")

    except ValueError as exc:
        print(f"参数错误:{exc}")


if __name__ == "__main__":
    main()
