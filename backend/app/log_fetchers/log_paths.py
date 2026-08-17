"""
Shared filesystem path configuration for log fetchers.

This module contains only directory configuration.

It does NOT:
    - read files
    - connect through SSH
    - parse logs
    - perform incremental reads

The local and remote fetchers both use this registry so that
path definitions do not get duplicated.
"""

LOCAL_LOG_PATHS: dict[str, list[str]] = {
    "apache": [
        "/var/log/httpd",
        "/var/log/apache2",
        "/usr/local/apache/logs",
    ],
    "mysql": [
        "/var/log/mysql",
        "/var/log",
    ],
    "syslog": [
        "/var/log",
    ],
}


REMOTE_LOG_PATHS: dict[str, list[str]] = {
    "apache": [
        "/var/log/httpd",
        "/var/log/apache2",
        "/usr/local/apache/logs",
    ],
    "mysql": [
        "/var/log/mysql",
        "/var/log",
    ],
    "syslog": [
        "/var/log",
    ],
}