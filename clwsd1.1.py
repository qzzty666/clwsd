import requests
import re
import argparse
import urllib3
import html

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def extract_title(html_text):
    match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if match:
        title = match.group(1).strip()
        title = html.unescape(title)
        title = re.sub(r"\s+", " ", title)
        return title
    return "-"

def check_url(url,timeout):
    try:
        response = requests.get(
            url,
            timeout=timeout,
            verify=False,
            allow_redirects=True,
            headers={"User-Agent":"Mozilla/5.0"}
        )

        if not response.encoding or response.encoding.lower() == "iso-8859-1":
            response.encoding = response.apparent_encoding

        status_code = response.status_code
        title = extract_title(response.text)
        length = len(response.content)
        server = response.headers.get("Server","-")
        final_url = response.url
        content_type = response.headers.get("Content-Type","-")

        return {
            "url":url,
            "status":str(status_code),
            "title":title,
            "length":str(length),
            "server":server,
            "final_url":final_url,
            "content_type":content_type,
        }

    except requests.exceptions.Timeout:
        return {
            "url":url,
            "status":"ERROR",
            "title":"timeout",
            "length":"0",
            "server":"-",
            "final_url":"-",
            "content_type":"-",
        }

    except requests.exceptions.ConnectionError:
        return {
            "url":url,
            "status":"ERROR",
            "title":"connection_error",
            "length":"0",
            "server":"-",
            "final_url":"-",
            "content_type":"-",
        }

    except  requests.exceptions.RequestException as e:
        return {
            "url":url,
            "status":"ERROR",
            "title":str(e),
            "length":"0",
            "server":"-",
            "final_url":"-",
            "content_type":"-",
        }

def load_urls(input_file):
    urls = []
    seen = set()

    with open(input_file,"r",encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue
            if url in seen:
                continue
            seen.add(url)
            urls.append(url)

    return urls

def save_results(output_file,results,only_alive=False):
    with open(output_file,"w",encoding="utf-8") as f:
        for item in results:
            if only_alive and item["status"] == "ERROR":
                continue

            line = (
                f"{item['url']} | "
                f"{item['status']} | "
                f"{item['title']} | "
                f"{item['length']} | "
                f"{item['server']} | "
                f"{item['final_url']} | "
                f"{item['content_type']}"
            )

            f.write(line+"\n")

def main():
    print(r"""
   ____   _                        _ 
  / ___| | | __      __  ___    __| |
 | |     | | \ \ /\ / / / __|  / _` |
 | |___  | |  \ V  V /  \__ \ | (_| |
  \____| |_|   \_/\_/   |___/  \__,_|

                            Clwsd 1.1
""")
        
    parser = argparse.ArgumentParser(
        description="Web 存活探测工具",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog, max_help_position=30 
        )
    )
    parser.add_argument("-i","--input",required=True,help="输入URL文件")
    parser.add_argument("-o","--output",default="alive.txt",help="输出结果文件")
    parser.add_argument("-t","--timeout",type=int,default=5,help="超时时间,默认5秒")
    parser.add_argument("-a","--only-alive",action="store_true",help="仅输出存活目标")

    args = parser.parse_args()

    urls = load_urls(args.input)
    results = []

    for url in urls:
        result = check_url(url,args.timeout)
        results.append(result)
        print(
            f"{result['url']} -> "
            f"{result['status']} | "
            f"{result['title']}"
        )

    save_results(args.output,results,args.only_alive)

    print(f"\n探测结束，共{len(results)}个目标，结果已保存到{args.output}")

    if args.only_alive:
        alive_count = len([item for item in results if item["status"] != "ERROR"])
        print(f"仅输出存活目标：{alive_count}个")

if __name__ == "__main__":
    main()








                            
          

