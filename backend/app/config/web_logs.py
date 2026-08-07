WEB_LOG_PATHS = {

    "apache_access": {

        "label": "Apache Access",

        "path": "/var/log/httpd/access.log",

    },

    "apache_error": {

        "label": "Apache Error",

        "path": "/var/log/httpd/error.log",

    },

    "mysql_slow": {

        "label": "MySQL Slow Query",

        "path": "/var/log/mysql/slow-query.log",

    },
     "laravel": {

        "label": "Laravel Log",

        "path": "/var/log/laravel/laravel.log",

    },

}

def debug_web_logs():

    print("\n")
    print("=" * 100)
    print("WEB LOG CONFIG")
    print("=" * 100)

    for key, value in WEB_LOG_PATHS.items():

        print(f"{key} -> {value}")