from datetime import datetime
import html

from .output_helpers import (
    OUTPUT_FIELDNAMES,
    filter_results,
    format_fingerprints,
    format_priority,
)


def count_priority_levels(results):
    counts = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "dead": 0,
    }

    for item in results:
        priority_level = item.get("priority_level", "dead").lower()
        if priority_level not in counts:
            priority_level = "dead"
        counts[priority_level] += 1

    return counts


def build_html_rows(results):
    rows = []

    if not results:
        return (
            "<tr>"
            "<td colspan=\"5\" class=\"empty-row\">当前没有可展示的结果</td>"
            "</tr>"
        )

    for item in results:
        website = html.escape(item.get("url", "-"))
        status = html.escape(item.get("status", "-"))
        title = html.escape(item.get("title", "-"))
        priority_level = html.escape(format_priority(item))
        priority_class = item.get("priority_level", "low").lower()
        fingerprint_text = format_fingerprints(item)
        url_text = item.get("url", "-")
        title_text = item.get("title", "-")
        status_text = item.get("status", "-")
        priority_rank = {"high": 0, "medium": 1, "low": 2, "dead": 3}.get(
            priority_class, 3
        )
        if str(status_text).isdigit():
            status_rank = int(status_text)
        else:
            status_rank = 9999

        if fingerprint_text == "-":
            fingerprint_html = "-"
        else:
            fingerprint_html = (
                "<div class=\"fingerprint-tags\">"
                + "".join(
                    f"<span class=\"fingerprint-tag\">{html.escape(tag.strip())}</span>"
                    for tag in fingerprint_text.split(",")
                )
                + "</div>"
            )

        rows.append(
            f"<tr class=\"priority-{priority_class}\" "
            f"data-priority=\"{priority_class}\" "
            f"data-url=\"{html.escape(url_text.lower())}\" "
            f"data-title=\"{html.escape(title_text.lower())}\" "
            f"data-status=\"{html.escape(str(status_text).lower())}\" "
            f"data-fingerprints=\"{html.escape(fingerprint_text.lower())}\" "
            f"data-order=\"{len(rows)}\" "
            f"data-priority-rank=\"{priority_rank}\" "
            f"data-status-rank=\"{status_rank}\">"
            f"<td><a href=\"{website}\" target=\"_blank\" rel=\"noopener noreferrer\">{website}</a></td>"
            f"<td>{status}</td>"
            f"<td>{title}</td>"
            f"<td>{fingerprint_html}</td>"
            f"<td>{priority_level}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def build_summary_cards(results, scanned_total):
    counts = count_priority_levels(results)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cards = [
        ("已扫描目标", str(scanned_total), "card-neutral", "all"),
        ("当前展示", str(len(results)), "card-neutral", "all"),
        ("高优先级", str(counts["high"]), "card-high", "high"),
        ("中优先级", str(counts["medium"]), "card-medium", "medium"),
        ("低优先级", str(counts["low"]), "card-low", "low"),
    ]

    if counts["dead"] > 0:
        cards.append(("非存活", str(counts["dead"]), "card-dead", "dead"))

    card_html = []
    for title, value, card_class, filter_name in cards:
        card_html.append(
            f"<section class=\"summary-card {card_class}\" data-filter=\"{html.escape(filter_name)}\">"
            f"<div class=\"summary-label\">{html.escape(title)}</div>"
            f"<div class=\"summary-value\">{html.escape(value)}</div>"
            "</section>"
        )

    return (
        "<section class=\"report-header\">"
        "<div>"
        "<h1>Clwsd 探测结果</h1>"
        "<p class=\"report-subtitle\">面向人工研判的 Web 存活结果报告</p>"
        "</div>"
        f"<div class=\"report-meta\">生成时间：{html.escape(generated_at)}</div>"
        "</section>"
        "<section class=\"summary-grid\">"
        + "".join(card_html)
        + "</section>"
    )


def build_filter_toolbar(results):
    counts = count_priority_levels(results)

    buttons = [
        ("全部", "all", len(results)),
        ("高优先级", "high", counts["high"]),
        ("中优先级", "medium", counts["medium"]),
        ("低优先级", "low", counts["low"]),
    ]

    if counts["dead"] > 0:
        buttons.append(("非存活", "dead", counts["dead"]))

    button_html = []
    for label, filter_name, count in buttons:
        active_class = " active" if filter_name == "all" else ""
        button_html.append(
            f"<button class=\"filter-button{active_class}\" type=\"button\" "
            f"data-filter=\"{html.escape(filter_name)}\">"
            f"{html.escape(label)} ({count})"
            "</button>"
        )

    return (
        "<section class=\"toolbar\">"
        "<div class=\"toolbar-left\">"
        "<div class=\"toolbar-title\">结果筛选</div>"
        "<div class=\"toolbar-buttons\">"
        + "".join(button_html)
        + "</div>"
        "</div>"
        "<div class=\"toolbar-status\">当前筛选：<span id=\"filter-status\">全部</span> | "
        "显示数量：<span id=\"visible-count\">0</span></div>"
        "</section>"
    )


def build_search_toolbar():
    return (
        "<section class=\"search-toolbar\">"
        "<div class=\"search-group\">"
        "<label class=\"control-label\" for=\"keyword-search\">关键词搜索</label>"
        "<input id=\"keyword-search\" class=\"search-input\" type=\"text\" "
        "placeholder=\"搜索网址、标题、状态码、指纹标签\">"
        "</div>"
        "<div class=\"sort-group\">"
        "<label class=\"control-label\" for=\"sort-select\">排序方式</label>"
        "<select id=\"sort-select\" class=\"sort-select\">"
        "<option value=\"default\">默认排序</option>"
        "<option value=\"priority\">优先级优先</option>"
        "<option value=\"status-asc\">状态码升序</option>"
        "<option value=\"status-desc\">状态码降序</option>"
        "<option value=\"url-asc\">网址 A-Z</option>"
        "<option value=\"title-asc\">标题 A-Z</option>"
        "</select>"
        "</div>"
        "</section>"
    )


def build_html_report(results, scanned_total):
    return (
        "<!doctype html>\n"
        "<html lang=\"zh-CN\">\n"
        "<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>Clwsd 结果</title>\n"
        "<style>"
        "body{font-family:Arial,sans-serif;margin:0;background:#ffffff;color:#222222;}"
        ".container{max-width:1440px;margin:0 auto;padding:32px 20px 40px;}"
        ".report-header{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;margin-bottom:20px;flex-wrap:wrap;}"
        "h1{margin:0;font-size:32px;color:#182230;}"
        ".report-subtitle{margin:8px 0 0;color:#5b6573;font-size:14px;}"
        ".report-meta{color:#5b6573;font-size:14px;padding-top:8px;}"
        ".summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:24px;}"
        ".summary-card{border:1px solid #d0d7de;border-radius:14px;padding:16px 18px;background:#ffffff;box-shadow:0 4px 14px rgba(15,23,42,0.05);}"
        ".summary-card[data-filter]{cursor:pointer;transition:transform 0.18s ease,box-shadow 0.18s ease,border-color 0.18s ease;}"
        ".summary-card[data-filter]:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(15,23,42,0.08);}"
        ".summary-card.is-active{border-color:#0b57d0;box-shadow:0 0 0 2px rgba(11,87,208,0.12),0 8px 20px rgba(15,23,42,0.08);}"
        ".summary-label{font-size:13px;color:#5b6573;margin-bottom:8px;}"
        ".summary-value{font-size:30px;font-weight:700;color:#182230;line-height:1;}"
        ".card-high{background:#fff0f1;border-color:#f3b8c0;}"
        ".card-medium{background:#fff8df;border-color:#f0d58a;}"
        ".card-low{background:#edf8f0;border-color:#b8ddc0;}"
        ".card-dead{background:#f5f6f8;border-color:#d7dce2;}"
        ".fingerprint-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;}"
        ".fingerprint-tag{display:inline-block;background:#e8f1ff;color:#0b57d0;border:1px solid #c9defd;border-radius:999px;padding:2px 8px;font-size:12px;line-height:1.6;}"
        ".toolbar{display:flex;justify-content:space-between;gap:16px;align-items:flex-end;flex-wrap:wrap;margin-bottom:18px;}"
        ".toolbar-title{font-size:15px;font-weight:700;color:#182230;margin-bottom:10px;}"
        ".toolbar-buttons{display:flex;gap:10px;flex-wrap:wrap;}"
        ".filter-button{border:1px solid #c7d2e0;background:#ffffff;color:#182230;border-radius:999px;padding:8px 14px;font-size:13px;cursor:pointer;transition:all 0.18s ease;}"
        ".filter-button:hover{border-color:#0b57d0;color:#0b57d0;background:#f5f9ff;}"
        ".filter-button.active{background:#0b57d0;border-color:#0b57d0;color:#ffffff;box-shadow:0 6px 16px rgba(11,87,208,0.2);}"
        ".toolbar-status{color:#5b6573;font-size:14px;padding-bottom:6px;}"
        ".search-toolbar{display:flex;justify-content:space-between;gap:16px;align-items:flex-end;flex-wrap:wrap;margin-bottom:18px;}"
        ".search-group,.sort-group{display:flex;flex-direction:column;gap:8px;}"
        ".control-label{font-size:13px;color:#5b6573;}"
        ".search-input,.sort-select{min-height:42px;border:1px solid #c7d2e0;border-radius:12px;padding:0 14px;background:#ffffff;color:#182230;font-size:14px;outline:none;transition:border-color 0.18s ease,box-shadow 0.18s ease;}"
        ".search-input{min-width:300px;}"
        ".sort-select{min-width:220px;cursor:pointer;}"
        ".search-input:focus,.sort-select:focus{border-color:#0b57d0;box-shadow:0 0 0 3px rgba(11,87,208,0.12);}"
        ".table-wrap{border:1px solid #d0d7de;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(15,23,42,0.06);}"
        "table{border-collapse:collapse;width:100%;font-size:14px;background:#ffffff;}"
        "th,td{border-bottom:1px solid #d0d7de;padding:10px 12px;vertical-align:top;text-align:left;}"
        "th{background:#1b2030;color:#fff;position:sticky;top:0;}"
        "td:last-child,th:last-child{white-space:nowrap;}"
        "a{color:#0b57d0;text-decoration:none;word-break:break-all;}"
        "a:hover{text-decoration:underline;}"
        "tr:last-child td{border-bottom:none;}"
        "tr:nth-child(even){background:#f8fafc;}"
        "tr.priority-high{background:#fde2e4;}"
        "tr.priority-high:nth-child(even){background:#fcd5ce;}"
        "tr.priority-medium{background:#fff1c9;}"
        "tr.priority-medium:nth-child(even){background:#ffe8a3;}"
        "tr.priority-low{background:#e6f4ea;}"
        "tr.priority-low:nth-child(even){background:#d7f0dd;}"
        "tr.priority-dead{background:#f1f3f5;}"
        "tr.priority-dead:nth-child(even){background:#e9ecef;}"
        ".empty-row{text-align:center;color:#6b7280;padding:28px 12px;background:#ffffff;}"
        "@media (max-width:768px){.container{padding:20px 12px 28px;}h1{font-size:26px;}.summary-value{font-size:24px;}.toolbar,.search-toolbar{align-items:flex-start;}.toolbar-status{padding-bottom:0;}.search-input,.sort-select{min-width:100%;width:100%;}th,td{padding:9px 10px;font-size:13px;}}"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "<main class=\"container\">\n"
        + build_summary_cards(results, scanned_total)
        + "\n"
        + build_filter_toolbar(results)
        + "\n"
        + build_search_toolbar()
        + "\n<div class=\"table-wrap\">\n<table>\n"
        "<thead><tr>"
        + "".join(f"<th>{name}</th>" for name in OUTPUT_FIELDNAMES)
        + "</tr></thead>\n<tbody>\n"
        + build_html_rows(results)
        + "\n</tbody>\n</table>\n</div>\n"
        "<script>"
        "(function(){"
        "const rows=Array.from(document.querySelectorAll('tbody tr[data-priority]'));"
        "const buttons=Array.from(document.querySelectorAll('.filter-button'));"
        "const cards=Array.from(document.querySelectorAll('.summary-card[data-filter]'));"
        "const filterStatus=document.getElementById('filter-status');"
        "const visibleCount=document.getElementById('visible-count');"
        "const searchInput=document.getElementById('keyword-search');"
        "const sortSelect=document.getElementById('sort-select');"
        "const tbody=document.querySelector('tbody');"
        "const filterLabels={all:'全部',high:'高优先级',medium:'中优先级',low:'低优先级',dead:'非存活'};"
        "let activeFilter='all';"
        "function sortRows(mode){"
        "const sortedRows=[...rows].sort((a,b)=>{"
        "if(mode==='priority'){"
        "const priorityDiff=Number(a.dataset.priorityRank)-Number(b.dataset.priorityRank);"
        "if(priorityDiff!==0){return priorityDiff;}"
        "const statusDiff=Number(a.dataset.statusRank)-Number(b.dataset.statusRank);"
        "if(statusDiff!==0){return statusDiff;}"
        "return a.dataset.url.localeCompare(b.dataset.url);"
        "}"
        "if(mode==='status-asc'){"
        "const diff=Number(a.dataset.statusRank)-Number(b.dataset.statusRank);"
        "if(diff!==0){return diff;}"
        "return a.dataset.url.localeCompare(b.dataset.url);"
        "}"
        "if(mode==='status-desc'){"
        "const diff=Number(b.dataset.statusRank)-Number(a.dataset.statusRank);"
        "if(diff!==0){return diff;}"
        "return a.dataset.url.localeCompare(b.dataset.url);"
        "}"
        "if(mode==='url-asc'){return a.dataset.url.localeCompare(b.dataset.url);}"
        "if(mode==='title-asc'){"
        "const titleDiff=a.dataset.title.localeCompare(b.dataset.title);"
        "if(titleDiff!==0){return titleDiff;}"
        "return a.dataset.url.localeCompare(b.dataset.url);"
        "}"
        "return Number(a.dataset.order)-Number(b.dataset.order);"
        "});"
        "sortedRows.forEach(row=>tbody.appendChild(row));"
        "}"
        "function applyView(){"
        "const keyword=searchInput.value.trim().toLowerCase();"
        "buttons.forEach(btn=>btn.classList.toggle('active',btn.dataset.filter===activeFilter));"
        "cards.forEach(card=>card.classList.toggle('is-active',card.dataset.filter===activeFilter));"
        "let count=0;"
        "rows.forEach(row=>{"
        "const filterMatched=activeFilter==='all'||row.dataset.priority===activeFilter;"
        "const text=row.dataset.url+' '+row.dataset.title+' '+row.dataset.status+' '+row.dataset.fingerprints;"
        "const keywordMatched=!keyword||text.includes(keyword);"
        "const matched=filterMatched&&keywordMatched;"
        "row.style.display=matched?'':'none';"
        "if(matched){count+=1;}"
        "});"
        "filterStatus.textContent=filterLabels[activeFilter]||activeFilter;"
        "visibleCount.textContent=String(count);"
        "}"
        "function setActive(filter){"
        "activeFilter=filter;"
        "buttons.forEach(btn=>btn.classList.toggle('active',btn.dataset.filter===filter));"
        "cards.forEach(card=>card.classList.toggle('is-active',card.dataset.filter===filter));"
        "applyView();"
        "}"
        "buttons.forEach(btn=>btn.addEventListener('click',()=>setActive(btn.dataset.filter)));"
        "cards.forEach(card=>card.addEventListener('click',()=>setActive(card.dataset.filter)));"
        "searchInput.addEventListener('input',applyView);"
        "sortSelect.addEventListener('change',()=>{sortRows(sortSelect.value);applyView();});"
        "sortRows('default');"
        "setActive('all');"
        "})();"
        "</script>\n"
        "</main>\n</body>\n</html>\n"
    )


def save_results_html(output_file, results, scanned_total=None, only_alive=False):
    filtered_results = filter_results(results, only_alive)
    if scanned_total is None:
        scanned_total = len(filtered_results)

    html_content = build_html_report(filtered_results, scanned_total)

    with open(output_file, "w", encoding="utf-8") as file_obj:
        file_obj.write(html_content)
