DEFAULT_URL_SCHEME = "http://"
SUPPORTED_URL_SCHEMES = ("http://", "https://")
UTF8_BOM = "\ufeff"

DEFAULT_OUTPUT_FORMATS = ["html", "csv"]
OUTPUT_FIELDNAMES = ["网站", "响应码", "标题", "指纹标签", "优先级"]

MAX_TIMEOUT_RETRIES = 2

ALIVE_STATUS_CODES = {"200", "301", "302", "401", "403"}
HTML_CONTENT_TYPES = ("text/html", "application/xhtml+xml")

STATUS_BASE_SCORES = {
    "200": 50,
    "301": 25,
    "302": 30,
    "401": 35,
    "403": 35,
}

TITLE_KEYWORD_SCORES = [
    ("登录", 30),
    ("login", 30),
    ("signin", 25),
    ("admin", 30),
    ("后台", 30),
    ("管理", 25),
    ("dashboard", 25),
    ("oa", 25),
    ("portal", 20),
    ("统一身份认证", 25),
    ("单点登录", 25),
    ("auth", 15),
]

URL_KEYWORD_SCORES = [
    ("login", 20),
    ("admin", 20),
    ("dashboard", 15),
    ("portal", 15),
    ("oa", 20),
    ("auth", 10),
    ("sso", 15),
    ("vpn", 10),
]

PRIORITY_ORDER = {
    "high": 0,
    "medium": 1,
    "low": 2,
    "dead": 3,
}

SERVER_FINGERPRINT_RULES = [
    ("openresty", "openresty", 12),
    ("nginx", "nginx", 10),
    ("microsoft-iis", "iis", 12),
    ("apache", "apache", 10),
    ("tomcat", "tomcat", 15),
    ("jetty", "jetty", 10),
]

TITLE_FINGERPRINT_RULES = [
    ("统一身份认证", "sso", 20),
    ("单点登录", "sso", 20),
    ("登录", "login-page", 15),
    ("login", "login-page", 15),
    ("后台", "admin-page", 15),
    ("admin", "admin-page", 15),
    ("管理", "admin-page", 10),
    ("管理后台", "admin-console", 22),
    ("后台管理", "admin-console", 22),
    ("管理系统", "admin-console", 18),
    ("系统管理", "admin-console", 18),
    ("控制台", "admin-console", 18),
    ("后台登录", "admin-console", 22),
    ("oa", "oa", 15),
    ("教务", "edu-system", 12),
    ("welcome to nginx", "generic-default-page", 10),
    ("welcome to apache", "generic-default-page", 10),
    ("apache2 debian default page", "generic-default-page", 15),
    ("iis7", "generic-default-page", 10),
    ("index of /", "directory-listing", 18),
    ("404 not found", "soft-404", 24),
    ("page not found", "soft-404", 22),
    ("页面不存在", "soft-404", 24),
    ("您访问的页面不存在", "soft-404", 24),
    ("正在跳转", "redirect-placeholder", 18),
    ("redirecting", "redirect-placeholder", 16),
    ("安全验证", "waf-page", 20),
    ("访问已被拦截", "waf-page", 24),
    ("request blocked", "waf-page", 22),
]

URL_FINGERPRINT_RULES = [
    ("/login", "login-page", 12),
    ("/signin", "login-page", 12),
    ("/console", "admin-console", 12),
    ("/admin/login", "admin-console", 16),
    ("/manage/login", "admin-console", 16),
    ("/system/login", "admin-console", 12),
    ("/admin", "admin-page", 12),
    ("/manage", "admin-page", 12),
    ("/manager", "tomcat-manager", 20),
    ("oa", "oa", 12),
    ("auth", "sso", 10),
    ("sso", "sso", 12),
]

HEADER_FINGERPRINT_RULES = [
    ("basic", "basic-auth", 18),
    ("bearer", "bearer-auth", 12),
    ("asp.net", "asp-net", 10),
    ("php", "php", 8),
    ("jsp", "jsp", 10),
    ("apache-coyote", "tomcat", 12),
    ("cf-mitigated", "waf-page", 24),
    ("safedog", "waf-page", 24),
    ("incap_ses", "waf-page", 22),
    ("perimeterx", "waf-page", 22),
]

BODY_FINGERPRINT_RULES = [
    ('type="password"', "password-input", 18),
    ("type='password'", "password-input", 18),
    ('name="password"', "password-input", 16),
    ("name='password'", "password-input", 16),
    ('placeholder="密码"', "password-input", 14),
    ('placeholder="password"', "password-input", 14),
    ('type="file"', "upload-form", 16),
    ("type='file'", "upload-form", 16),
    ("multipart/form-data", "upload-form", 18),
    ("webuploader", "upload-form", 14),
    ("plupload", "upload-form", 14),
    ("kindeditor", "kindeditor", 16),
    ("ueditor", "ueditor", 16),
    ("ckeditor", "ckeditor", 14),
    ("tinymce", "tinymce", 14),
    ("swagger-ui", "swagger-ui", 24),
    ("swagger-ui.css", "swagger-ui", 24),
    ('id="swagger-ui"', "swagger-ui", 24),
    ("jenkins", "jenkins", 24),
    ("grafana", "grafana", 24),
    ("phpmyadmin", "phpmyadmin", 26),
    ("druid", "druid-monitor", 22),
    ("prometheus", "prometheus", 20),
    ("http-equiv=\"refresh\"", "redirect-placeholder", 18),
    ("http-equiv='refresh'", "redirect-placeholder", 18),
    ("window.location", "redirect-placeholder", 16),
    ("location.href", "redirect-placeholder", 16),
    ("页面正在跳转", "redirect-placeholder", 16),
    ("redirecting", "redirect-placeholder", 14),
    ("404 not found", "soft-404", 24),
    ("page not found", "soft-404", 22),
    ("页面不存在", "soft-404", 24),
    ("您访问的页面不存在", "soft-404", 24),
    ("the requested url was not found on this server", "soft-404", 22),
    ("cf-browser-verification", "waf-page", 24),
    ("cf-chl-", "waf-page", 24),
    ("attention required!", "waf-page", 22),
    ("sorry, you have been blocked", "waf-page", 22),
    ("safedog", "waf-page", 24),
    ("安全狗", "waf-page", 24),
    ("incapsula incident id", "waf-page", 24),
    ("blocked by waf", "waf-page", 22),
]

ASSET_PATH_FINGERPRINT_RULES = [
    ("swagger", "swagger-ui", 18),
    ("jenkins", "jenkins", 20),
    ("grafana", "grafana", 20),
    ("phpmyadmin", "phpmyadmin", 22),
    ("druid", "druid-monitor", 20),
    ("prometheus", "prometheus", 18),
    ("kindeditor", "kindeditor", 14),
    ("ueditor", "ueditor", 14),
    ("ckeditor", "ckeditor", 12),
    ("tinymce", "tinymce", 12),
    ("layuiadmin", "admin-console", 18),
    ("adminlte", "admin-console", 16),
]

FAVICON_PATH_FINGERPRINT_RULES = [
    ("swagger", "swagger-ui", 18),
    ("jenkins", "jenkins", 20),
    ("grafana", "grafana", 20),
    ("phpmyadmin", "phpmyadmin", 22),
    ("druid", "druid-monitor", 18),
    ("prometheus", "prometheus", 18),
]

META_GENERATOR_TECH_RULES = [
    ("wordpress", "WordPress"),
    ("drupal", "Drupal"),
    ("joomla", "Joomla"),
    ("grafana", "Grafana"),
    ("docusaurus", "Docusaurus"),
]

ASSET_PATH_TECH_RULES = [
    ("wp-content/", "WordPress"),
    ("swagger-ui", "Swagger UI"),
    ("swagger-ui-bundle", "Swagger UI"),
    ("jenkins", "Jenkins"),
    ("grafana", "Grafana"),
    ("phpmyadmin", "phpMyAdmin"),
    ("druid", "Druid Monitor"),
    ("prometheus", "Prometheus"),
    ("kindeditor", "KindEditor"),
    ("ueditor", "UEditor"),
    ("ckeditor", "CKEditor"),
    ("tinymce", "TinyMCE"),
    ("layuiadmin", "LayuiAdmin"),
    ("adminlte", "AdminLTE"),
]

HEADER_TECH_RULES = [
    ("x-drupal-", "Drupal"),
    ("x-generator: drupal", "Drupal"),
    ("x-powered-by: php", "PHP"),
    ("x-powered-by: asp.net", "ASP.NET"),
    ("server: openresty", "OpenResty"),
    ("server: nginx", "Nginx"),
    ("server: apache", "Apache"),
    ("server: microsoft-iis", "Microsoft IIS"),
]

FAVICON_HASH_TECH_RULES = {
    "1494302000": "phpMyAdmin",
}

TECHNOLOGY_TAG_RULES = [
    {"tag": "openresty", "name": "OpenResty", "category": "server", "confidence": "medium"},
    {"tag": "nginx", "name": "Nginx", "category": "server", "confidence": "medium"},
    {"tag": "iis", "name": "Microsoft IIS", "category": "server", "confidence": "medium"},
    {"tag": "apache", "name": "Apache", "category": "server", "confidence": "medium"},
    {"tag": "tomcat", "name": "Tomcat", "category": "middleware", "confidence": "medium"},
    {"tag": "jetty", "name": "Jetty", "category": "middleware", "confidence": "medium"},
    {"tag": "asp-net", "name": "ASP.NET", "category": "framework", "confidence": "medium"},
    {"tag": "php", "name": "PHP", "category": "language", "confidence": "medium"},
    {"tag": "jsp", "name": "JSP", "category": "language", "confidence": "medium"},
    {"tag": "swagger-ui", "name": "Swagger UI", "category": "surface", "confidence": "high"},
    {"tag": "jenkins", "name": "Jenkins", "category": "panel", "confidence": "high"},
    {"tag": "grafana", "name": "Grafana", "category": "panel", "confidence": "high"},
    {"tag": "phpmyadmin", "name": "phpMyAdmin", "category": "panel", "confidence": "high"},
    {"tag": "druid-monitor", "name": "Druid Monitor", "category": "panel", "confidence": "high"},
    {"tag": "prometheus", "name": "Prometheus", "category": "panel", "confidence": "high"},
    {"tag": "kindeditor", "name": "KindEditor", "category": "editor", "confidence": "high"},
    {"tag": "ueditor", "name": "UEditor", "category": "editor", "confidence": "high"},
    {"tag": "ckeditor", "name": "CKEditor", "category": "editor", "confidence": "high"},
    {"tag": "tinymce", "name": "TinyMCE", "category": "editor", "confidence": "high"},
    {"tag": "tomcat-manager", "name": "Tomcat Manager", "category": "panel", "confidence": "high"},
    {"tag": "edu-system", "name": "Edu System", "category": "business", "confidence": "low"},
]

TECHNOLOGY_EVIDENCE_RULES = {
    "meta_generator": [
        {"keyword": "wordpress", "name": "WordPress", "category": "cms", "confidence": "high"},
        {"keyword": "drupal", "name": "Drupal", "category": "cms", "confidence": "high"},
        {"keyword": "joomla", "name": "Joomla", "category": "cms", "confidence": "high"},
        {"keyword": "grafana", "name": "Grafana", "category": "panel", "confidence": "high"},
        {"keyword": "docusaurus", "name": "Docusaurus", "category": "site", "confidence": "high"},
    ],
    "header_text": [
        {"keyword": "x-drupal-", "name": "Drupal", "category": "cms", "confidence": "medium"},
        {"keyword": "x-generator: drupal", "name": "Drupal", "category": "cms", "confidence": "high"},
        {"keyword": "x-powered-by: php", "name": "PHP", "category": "language", "confidence": "medium"},
        {"keyword": "x-powered-by: asp.net", "name": "ASP.NET", "category": "framework", "confidence": "medium"},
        {"keyword": "server: openresty", "name": "OpenResty", "category": "server", "confidence": "medium"},
        {"keyword": "server: nginx", "name": "Nginx", "category": "server", "confidence": "medium"},
        {"keyword": "server: apache", "name": "Apache", "category": "server", "confidence": "medium"},
        {"keyword": "server: microsoft-iis", "name": "Microsoft IIS", "category": "server", "confidence": "medium"},
    ],
    "asset_paths": [
        {"keyword": "wp-content/", "name": "WordPress", "category": "cms", "confidence": "high"},
        {"keyword": "swagger-ui", "name": "Swagger UI", "category": "surface", "confidence": "high"},
        {"keyword": "swagger-ui-bundle", "name": "Swagger UI", "category": "surface", "confidence": "high"},
        {"keyword": "jenkins", "name": "Jenkins", "category": "panel", "confidence": "high"},
        {"keyword": "grafana", "name": "Grafana", "category": "panel", "confidence": "high"},
        {"keyword": "phpmyadmin", "name": "phpMyAdmin", "category": "panel", "confidence": "high"},
        {"keyword": "druid", "name": "Druid Monitor", "category": "panel", "confidence": "high"},
        {"keyword": "prometheus", "name": "Prometheus", "category": "panel", "confidence": "high"},
        {"keyword": "kindeditor", "name": "KindEditor", "category": "editor", "confidence": "high"},
        {"keyword": "ueditor", "name": "UEditor", "category": "editor", "confidence": "high"},
        {"keyword": "ckeditor", "name": "CKEditor", "category": "editor", "confidence": "high"},
        {"keyword": "tinymce", "name": "TinyMCE", "category": "editor", "confidence": "high"},
        {"keyword": "layuiadmin", "name": "LayuiAdmin", "category": "panel", "confidence": "medium"},
        {"keyword": "adminlte", "name": "AdminLTE", "category": "panel", "confidence": "medium"},
    ],
    "favicon_paths": [
        {"keyword": "swagger", "name": "Swagger UI", "category": "surface", "confidence": "medium"},
        {"keyword": "jenkins", "name": "Jenkins", "category": "panel", "confidence": "medium"},
        {"keyword": "grafana", "name": "Grafana", "category": "panel", "confidence": "medium"},
        {"keyword": "phpmyadmin", "name": "phpMyAdmin", "category": "panel", "confidence": "medium"},
        {"keyword": "druid", "name": "Druid Monitor", "category": "panel", "confidence": "medium"},
        {"keyword": "prometheus", "name": "Prometheus", "category": "panel", "confidence": "medium"},
    ],
}

TECHNOLOGY_FAVICON_HASH_RULES = {
    "1494302000": {
        "name": "phpMyAdmin",
        "category": "panel",
        "confidence": "high",
    },
}
