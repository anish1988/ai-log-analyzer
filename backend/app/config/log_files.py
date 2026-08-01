"""
Registry of searchable log files.

This file is intentionally environment-independent.

It DOES NOT contain filesystem paths.

The actual filesystem paths are resolved by:

    search_local_file()
    search_remote_file()

This allows:

LOCAL
------
/host_logs/apache2/error.log

REMOTE
-------
/var/log/httpd/error_log
/var/log/apache2/error.log

without changing this registry.
"""

from dataclasses import dataclass

from app.config.servers import Tier


@dataclass(frozen=True)
class LogFileConfig:
    id: str

    tier: Tier

    label: str

    #
    # apache
    # mysql
    # syslog
    # messages
    # asterisk-core
    # asterisk-full
    # vicidial
    #
    service: str

    #
    # Relative filename only.
    #
    # Examples
    #
    # access.log
    # error.log
    # messages_{date}
    #
    filename: str

    #
    # Whether filename contains {date}
    #
    has_date_pattern: bool

    filename_template: str | None = None

    #
    # After N days resolver will first try .gz
    #
    gzip_after_days: int = 3

    date_pattern: str = "%Y-%m-%d"


LOG_FILE_REGISTRY = [

    #
    # WEB
    #

    LogFileConfig(
        id="web-apache-access",
        tier=Tier.WEB,
        label="Apache Access",
        service="apache",
        filename="access.log",
        filename_template="access.log",
        has_date_pattern=False,
    ),

    LogFileConfig(
        id="web-apache-error",
        tier=Tier.WEB,
        label="Apache Error",
        service="apache",
        filename="error.log",
        filename_template="error.log",
        has_date_pattern=False,
    ),

    LogFileConfig(
        id="web-syslog",
        tier=Tier.WEB,
        label="System Log",
        service="syslog",
        filename="syslog",
        filename_template="syslog",
        has_date_pattern=False,
    ),

    LogFileConfig(
        id="web-mysql",
        tier=Tier.WEB,
        label="MySQL",
        service="mysql",
        filename="error.log",
        filename_template="error.log",
        has_date_pattern=False,
    ),

    #
    # TELEPHONY
    #

      LogFileConfig(
        id="FASTagiout",
        label="FASTagiout",
        tier="telephony",
        service="astguiclient",
        filename="FASTagiout",
        filename_template="FASTagiout.{date}",
        has_date_pattern=True,
        # date_separator=".",
    ),
    
    LogFileConfig(
        id="reset_mysql_vars",
        label="reset_mysql_VARS",
        tier="telephony",
        service="astguiclient",
        filename="reset_mysql_vars",
        filename_template="reset_mysql_vars.{date}",
        has_date_pattern=True,
        #date_separator=".",
    ),
    LogFileConfig(
        id="vicidial_debug",
        label="vicidial_debug",
        tier="telephony",
        service="astguiclient",
        filename="vicidial_debug",
        filename_template="vicidial_debug.{date}.txt",
        has_date_pattern=True,
       # date_separator=".",
    ),
    
    #
    # DATABASE
    #

    LogFileConfig(
        id="db-slow-query",
        tier=Tier.DB,
        label="Slow Query",
        service="mysql",
        filename="slow-query.log",
        has_date_pattern=False,
    ),
]


def get_log_files_for_tier(tier: Tier) -> list[LogFileConfig]:

    return [
        file
        for file in LOG_FILE_REGISTRY
        if file.tier == tier
    ]