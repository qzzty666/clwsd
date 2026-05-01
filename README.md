# Clwsd

Clwsd 是一个使用 Python 编写的 Web 存活探测小工具。

当前版本：`1.0.0`

这是一个最小可用版本，主要用于学习 HTTP 探测的基础流程：读取 URL、发送请求、提取状态码、标题、响应长度和 Server 信息，并将结果保存到文件。

## 功能

- 从文件读取 URL 列表
- 批量发送 HTTP/HTTPS 请求
- 支持自定义请求超时时间
- 自动跟随跳转
- 忽略 HTTPS 证书校验错误
- 提取页面标题
- 处理常见中文编码问题
- 解码 HTML 实体标题
- 输出状态码、标题、响应长度和 Server 头
- 对超时、连接失败等异常进行标记

## 环境要求

- Python 3.x
- requests
- urllib3

安装依赖：

```bash
pip install requests urllib3
```

## 使用方法

准备一个 URL 文件，例如 `urls.txt`：

```text
http://example.com
https://example.org
http://127.0.0.1:8080
```

运行：

```bash
python clwsd.py -i urls.txt -o alive.txt
```

指定超时时间：

```bash
python clwsd.py -i urls.txt -o alive.txt -t 3
```

查看帮助：

```bash
python clwsd.py -h
```

## 参数说明

```text
-i, --input      输入 URL 文件，必填
-o, --output     输出结果文件，默认 alive.txt
-t, --timeout    请求超时时间，默认 5 秒
```

## 输出格式

结果文件每行格式如下：

```text
URL | 状态 | 标题 | 响应长度 | Server
```

示例：

```text
http://example.com | 200 | Example Domain | 1256 | nginx
http://127.0.0.1:8080 | ERROR | connection_error | 0 | -
```

字段说明：

- `URL`：被探测的目标地址
- `状态`：HTTP 状态码，或 `ERROR`
- `标题`：HTML `<title>` 内容，未获取到时为 `-`
- `响应长度`：响应体字节长度
- `Server`：响应头中的 Server 字段，未获取到时为 `-`

## 当前版本定位

`1.0.0` 是一个基础版本，目标是把 Web 存活探测的核心流程跑通。

它还没有加入并发、去重、只保存存活目标、CSV/JSON 输出、代理、重试、最终跳转 URL、Content-Type 提取等功能。这些会作为后续版本继续完善。

## 适用场景

- 学习 Python HTTP 请求
- 理解 Web 存活探测的基本过程
- 整理小规模 URL 资产
- 作为后续指纹识别、目录扫描、PoC 验证工具的前置练习

## 为什么已有更好的工具，还要自己造轮子

市面上已经有很多成熟工具，我写这个工具不是为了替代它们，而是为了理解它们背后的基本原理：

- HTTP 请求是如何发出的
- 状态码、标题、Header、响应长度是如何提取的
- 超时和连接失败在代码里如何处理
- 编码问题为什么会导致标题乱码
- 一个 Web 探测器最小闭环需要哪些模块

先自己实现一个简单版本，可以帮助我更好地理解成熟工具的设计，也能在以后更准确地使用、调试和组合前辈的工具。
