# Clwsd

Clwsd 是一个使用 Python 编写的 Web 存活探测小工具。

当前版本：`4.1.0`

这个项目的目标不是替代成熟工具，而是把一个常见探测工具从单文件脚本逐步做成结构清晰、方便继续扩展的小项目。

同时，`clwsd` 的定位是明确收口的：

- 它负责 `Web 存活探测`
- 它负责 `高价值目标筛选`
- 它负责 `轻量技术研判`
- 它不追求变成一个“大而全”的深度指纹平台

当前版本已经支持：

- 从文件读取 URL 并自动去重
- 批量发送 HTTP/HTTPS 请求
- 支持自定义超时时间
- 支持多线程并发探测
- 自动跟随跳转
- 忽略 HTTPS 证书校验错误
- 提取页面标题
- 处理常见中文编码问题
- 解码 HTML 实体标题
- 提取状态码、响应长度、Server、最终跳转 URL、Content-Type
- 默认只保留高价值存活结果
- 支持 HTML / CSV / TXT / JSON 输出
- 将核心逻辑拆分到 `core/` 模块中
- 对超时时间和线程数进行基础合法性校验
- 对非法输出格式进行明确报错
- 对输入 URL 进行基础预清洗
- 增加终端彩色输出
- 将终端显示逻辑拆分到 `core/display.py`
- 对超时目标默认自动重试 1 次
- 默认只保留高价值存活结果
- 增加优先级评分、等级和原因
- 按优先级排序显示与保存结果
- 默认输出到 `result/` 目录
- 默认生成 `html + csv` 双格式结果
- 输出字段精简为：网站、响应码、标题、指纹标签、优先级
- HTML 报告中的网址可直接点击访问
- HTML 报告增加顶部统计摘要卡片
- HTML 报告支持按优先级一键筛选
- HTML 报告支持关键词搜索与排序
- 核心请求层支持线程内连接复用与页面预读提取标题
- 核心请求层支持连接超时拆分与跳转次数限制
- 核心请求层支持更细的错误分类与更轻的非 HTML 处理
- 核心请求层支持按目标类型自适应选择 HEAD 或 GET
- 调度层支持滑动窗口提交，默认线程提升到 30
- 支持轻量指纹识别和指纹标签输出
- 指纹标签已同步写入 HTML / CSV / TXT / JSON
- 进一步细分默认页、后台控制台和认证网关的优先级
- 增加页面正文轻量采样，识别登录框、上传点和常见控制台特征
- 支持自定义请求头、Cookie 和代理
- 增强 favicon 与静态资源路径指纹识别
- 增加 WAF、软 404、跳转壳降噪识别
- 指纹结果增加结构化 `technology_details`
- 新增第三方指纹适配层骨架
- 支持通过可选开关启用 `python-Wappalyzer` 增强识别

## 项目结构

```text
chen/
├── clwsd.py              # CLI 入口，负责参数解析和调度
├── core/
│   ├── __init__.py       # 模块导出入口
│   ├── constants.py      # 公共常量
│   ├── loader.py         # 读取 URL、预清洗、去重
│   ├── http_client.py    # Session、连接池、超时、HEAD/GET 请求
│   ├── response_parser.py# 标题提取、正文预读、编码处理
│   ├── checker.py        # 探测调度、结果组装、异常分类
│   ├── fingerprinter.py  # 轻量指纹识别和标签提取
│   ├── thirdparty_fingerprints.py # 第三方指纹调度与启用条件
│   ├── thirdparty_providers.py # 第三方指纹 provider 适配实现
│   ├── technology_merge.py # 内部/外部技术结果合并
│   ├── analyzer.py       # 存活判断、优先级分析、结果排序
│   ├── output_helpers.py # 输出公共工具和字段定义
│   ├── output_writers.py # TXT / CSV / JSON 写出
│   ├── html_report.py    # HTML 报告生成
│   ├── output.py         # 输出统一入口
│   └── display.py        # 终端显示、颜色、摘要输出
├── tests/                # 基础单元测试
├── result/               # 默认输出目录
├── urls.txt
├── README.md
└── UPGRADE_NOTES.md
```

## 环境要求

- Python 3.x
- colorama
- requests
- urllib3
- unittest

安装依赖：

```bash
pip install colorama requests urllib3
```

如果需要启用第三方技术指纹增强，可额外安装：

```bash
pip install python-Wappalyzer
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
python clwsd.py -i urls.txt -o alive
```

指定超时时间和线程数：

```bash
python clwsd.py -i urls.txt -o alive -t 3 -w 20
```

显示并保存全部结果：

```bash
python clwsd.py -i urls.txt -o alive --all
```

仅输出 CSV：

```bash
python clwsd.py -i urls.txt -o alive -f csv
```

仅输出 JSON：

```bash
python clwsd.py -i urls.txt -o alive -f json
```

启用第三方技术指纹增强：

```bash
python clwsd.py -i urls.txt -o alive --thirdparty-fingerprints
```

查看帮助：

```bash
python clwsd.py -h
```

## 参数说明

```text
-i, --input      输入 URL 文件，必填
-o, --output     输出文件基础名，默认 alive
-t, --timeout    请求超时时间，默认 5 秒
--all            显示并保存全部结果
-w, --workers    线程数，默认 30
-f, --format     输出格式：html / csv / txt / json，默认 html csv
--thirdparty-fingerprints  启用可选第三方技术指纹增强
```

## 测试

当前项目已经补上了基础单元测试，重点覆盖：

- `loader` 的 URL 规范化和去重逻辑
- `analyzer` 的优先级判断和排序逻辑
- `response_parser` 的标题提取、预读、编码处理逻辑
- `fingerprinter` 的轻量标签识别逻辑
- `thirdparty_fingerprints` 的启用条件与 provider 调度逻辑
- `technology_merge` 的内外部技术结果合并逻辑
- `output_writers` 的 TXT / CSV / JSON 写出逻辑
- `html_report` 的摘要、表格行和空结果页逻辑

运行测试：

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## 参数校验说明

为了避免无效输入导致程序行为异常，当前版本增加了基础参数校验：

- `--timeout` 必须大于等于 1
- `--workers` 必须大于等于 1
- 非法输出格式会明确报错，而不是静默失败

## 输入预清洗说明

为了让输入目标更统一，当前版本会在读取 URL 时进行基础预清洗：

- 去掉每行首尾空白
- 去掉 UTF-8 BOM
- 对缺少协议头的目标自动补全 `http://`
- 在清洗后的结果基础上进行去重

当前版本不会自动添加或删除 `www`

## 请求策略说明

为了减少临时网络抖动导致的误判，当前版本增加了基础请求重试策略：

- 当目标第一次请求超时后，会默认自动再请求 1 次
- 如果第二次仍然超时，结果才会标记为 `timeout`
- 当前版本只对 `Timeout` 做默认重试
- `ConnectionError` 和其他请求异常仍按原逻辑直接返回错误结果

## 优先级说明

当前版本会默认保留更有价值的存活结果，并给每个目标打上优先级：

- `200`、`301`、`302`、`401`、`403` 会被视为存活结果
- 标题中出现 `登录`、`后台`、`管理`、`OA` 等关键词会提高优先级
- `200` 且是 HTML 页面的目标通常优先级更高
- 输出结果会按优先级从高到低排序
- 终端会用不同颜色标记不同优先级

## 指纹识别说明

当前版本的指纹识别分为两层：

- 内部轻量规则识别
- 可选第三方技术识别增强

内部轻量规则当前会综合这些证据：

- `Server`
- `Title`
- `URL`
- 关键响应头
- 正文关键特征
- 静态资源路径
- favicon 路径与 hash
- `meta generator`

识别结果除了原有 `technology_matches` 外，还会保留结构化 `technology_details`，用于描述：

- 技术名称
- 分类
- 置信度
- 命中来源
- 命中证据

当前版本还会进一步归纳：

- `primary_technologies`
- `secondary_technologies`

这样可以把更值得优先关注的 `CMS / 面板 / 暴露面 / 中间件` 放在前面，把 `Server / Language` 这类辅助环境信息放在后面。

如果通过 `--thirdparty-fingerprints` 启用第三方识别，当前会尝试调用 `python-Wappalyzer`：

- 未安装依赖时自动跳过，不影响主流程
- 默认不会启用，避免为普通扫描增加额外负担
- 当前第三方结果会先并入 `technology_details`，为后续主技术排序和融合做准备

## 核心边界

为了避免项目越来越臃肿，当前版本明确把 `clwsd` 的职责边界控制在三层：

1. 存活判断
   状态码、标题、响应头、最终跳转、基础错误分类。
2. 轻量研判
   登录页、后台、控制台、上传点、编辑器、CMS、WAF、软 404、跳转壳等高价值特征。
3. 主技术归纳
   输出 `technology_matches`、`technology_details`、`primary_technologies`、`secondary_technologies`，帮助人工决定后续测试方向。

当前版本明确不把这些能力继续堆进主程序：

- 大规模 CMS 规则库
- 精细版本识别
- WordPress / Joomla / Drupal 深层插件组件枚举
- 完整 CPE 映射
- 全量 headless 渲染识别
- 大而全的 WAF / 指纹 / 漏洞平台化功能

## 输出格式

当前版本默认会在 `result/` 目录下生成：

- `html` 报告
- `csv` 结果表

如果需要，也可以通过 `-f` 指定输出为 `txt` 或 `json`。

所有格式默认只保留 5 个核心字段：

```text
网站 | 响应码 | 标题 | 指纹标签 | 优先级
```

示例：

```text
http://example.com | 200 | Example Domain | nginx, login-page | HIGH
http://127.0.0.1:8080 | ERROR | connection_error | - | LOW
```

字段说明：

- `网站`：被探测的目标地址
- `响应码`：HTTP 状态码，或 `ERROR`
- `标题`：HTML `<title>` 内容，未获取到时为 `-`
- `指纹标签`：轻量识别出的站点标签，多个标签用逗号分隔
- `优先级`：`HIGH` / `MEDIUM` / `LOW`

HTML 报告中的网站链接可直接点击访问，指纹标签也会以独立列展示，便于人工筛选。

## 终端显示说明

当前版本增加了终端彩色输出，并将显示逻辑独立到 `core/display.py`：

- 高优先级结果整行高亮显示
- 中优先级结果整行显示为黄色
- 低优先级结果整行显示为绿色
- 非存活结果在 `--all` 模式下显示为红色
- 文件输出仍然保持纯文本，不包含颜色控制字符

## 当前版本定位

`4.1.0` 的重点是在 `4.0.0` 的实战研判基础上，继续把指纹系统往“结构化”和“可扩展”方向推进。

这意味着当前版本除了具备清晰的模块结构，还进一步做到：

- 对非法参数进行拦截
- 对错误输出格式进行显式报错
- 避免“输入错了但程序悄悄失败”的情况
- 对输入 URL 进行基础预清洗
- 将终端显示逻辑从主入口中独立出来
- 让扫描结果在终端中更直观可读
- 对超时目标增加一次默认自动重试
- 默认保留更有价值的存活结果
- 为目标增加优先级分数和原因
- 按优先级输出更值得优先测试的站点
- 默认输出到 `result/` 目录
- 默认生成更适合人工研判的 `html + csv` 结果
- 将结果字段精简到最关键的 5 项
- 让终端颜色和 HTML 行着色都围绕优先级展开
- 让 HTML 报告在打开后第一眼就能看到整体资产分布
- 让 HTML 报告可以直接切换查看高/中/低优先级目标
- 让 HTML 报告具备基础检索与排序能力
- 让请求层减少重复建连和不必要的整页下载
- 让异常连接和异常跳转更快结束，避免拖慢整体扫描
- 让错误结果更容易被统计和诊断
- 让静态资源和下载类目标尽量更早结束探测
- 让大规模 URL 任务在更高并发下保持更稳的资源占用
- 让技术识别结果从平铺标签升级为结构化明细
- 为后续接入更多第三方指纹库预留统一适配层
- 让内部规则和外部技术识别可以走同一套合并链路
- 明确主程序边界，避免项目继续失控膨胀

## 适用场景

- 学习 Python HTTP 请求
- 学习如何把单文件脚本拆成模块
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
- 一个脚本如何演化为可维护的小项目

先自己实现一个简单版本，可以帮助我更好地理解成熟工具的设计，也能在以后更准确地使用、调试和组合前辈的工具。

最后，谢谢大家。
