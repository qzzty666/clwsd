from colorama import Fore, Style, init

init(autoreset=True)

def print_banner(version):
    print(
        rf"""
   ____   _                        _
  / ___| | | __      __  ___    __| |
 | |     | | \ \ /\ / / / __|  / _` |
 | |___  | |  \ V  V /  \__ \ | (_| |
  \____| |_|   \_/\_/   |___/  \__,_|

            Clwsd {version} by 骑猪走天涯
"""
    )

def get_result_color(result):
    if not result.get("is_alive", False):
        return Fore.RED

    priority_level = result.get("priority_level", "low")

    if priority_level == "high":
        return Fore.LIGHTRED_EX

    if priority_level == "medium":
        return Fore.YELLOW

    return Fore.GREEN

def build_priority_label(priority_level):
    return priority_level.upper()


def print_result(result, completed_count=None, total_count=None):
    color = get_result_color(result)
    priority_level = result.get("priority_level", "dead").upper()
    priority_label = build_priority_label(priority_level)
    progress_prefix = ""
    if completed_count is not None and total_count is not None:
        progress_prefix = f"正在扫描: {completed_count}/{total_count} | "
    line = (
        f"[{priority_label}] "
        f"{result['url']} -> "
        f"{result['status']} | "
        f"{result['title']}"
    )
    print("\r\033[K" + progress_prefix + color + line + Style.RESET_ALL)


def print_progress(completed_count, total_count, kept_count):
    progress_text = (
        f"\r正在扫描: {completed_count}/{total_count} | "
        f"当前保留: {kept_count}"
    )
    print(progress_text, end="", flush=True)


def finish_progress():
    print()

def print_summary(scanned_results, kept_results, output_files, include_all=False):
    scanned_total = len(scanned_results)
    kept_total = len(kept_results)
    output_text = "，".join(output_files)

    print(
        f"\n探测结束,共扫描{scanned_total}个目标，保留{kept_total}个结果，结果已保存到{output_text}"
    )

    high_count = 0
    medium_count = 0
    low_count = 0
    dead_count = 0
    error_type_counts = {}

    for item in kept_results:
        priority_level = item.get("priority_level", "dead")
        if priority_level == "high":
            high_count += 1
        elif priority_level == "medium":
            medium_count += 1
        elif priority_level == "low":
            low_count += 1
        else:
            dead_count += 1

        if item.get("status") == "ERROR":
            error_type = item.get("error_type", "unknown_error")
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1

    if include_all:
        print(
            f"高优先级:{high_count}个 | 中优先级:{medium_count}个 | "
            f"低优先级:{low_count}个 | 非存活:{dead_count}个"
        )
        if error_type_counts:
            error_parts = []
            for error_type, count in sorted(
                error_type_counts.items(),
                key=lambda item: (-item[1], item[0]),
            ):
                error_parts.append(f"{error_type}:{count}个")
            print("错误分布:" + " | ".join(error_parts))
    else:
        print(
            f"高优先级:{high_count}个 | 中优先级:{medium_count}个 | "
            f"低优先级:{low_count}个"
        )
