def resolve_log_file_candidates_old(
    file: LogFileConfig,
    target_date: date,
    now: date | None = None,
) -> list[ResolvedLogPath]:
    now = now or date.today()

    # Date-suffixed filenames are a telephony-only concept (point 3) - web
    # and DB tier logs always search their static path, even if
    # `has_date_pattern` was left True on a config entry by mistake. The
    # tier check is the source of truth, not the flag alone.
    if file.tier != Tier.TELEPHONY or not file.has_date_pattern:
        print(f"[resolve_log_file_candidates] Reading {file.tier}")
        return [ResolvedLogPath(path=file.remote_path_template, is_gzipped=False, is_dated=False)]

    date_str = target_date.strftime(file.date_pattern)
    dated_path = file.remote_path_template.replace("{date}", date_str)
    age_in_days = (now - target_date).days
    should_be_gzipped = age_in_days >= file.gzip_after_days

    candidates: list[ResolvedLogPath] = []

    if should_be_gzipped:
        candidates.append(ResolvedLogPath(path=f"{dated_path}.gz", is_gzipped=True, is_dated=True))
        # Still worth trying uncompressed too, in case rotation hasn't run yet.
        candidates.append(ResolvedLogPath(path=dated_path, is_gzipped=False, is_dated=True))
    else:
        candidates.append(ResolvedLogPath(path=dated_path, is_gzipped=False, is_dated=True))

    undated_path = re.sub(r"_?\{date\}", "", file.remote_path_template)
    candidates.append(ResolvedLogPath(path=undated_path, is_gzipped=False, is_dated=False))

    return candidates


    LOCAL_LOG_PATHS = {
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
    "asterisk-core": [
        "/var/log/asterisk",
    ],
    "asterisk-full": [
        "/var/log/asterisk",
    ],
    "vicidial": [
        "/var/log/astguiclient",
    ],
}


 REMOTE_LOG_PATHS = {
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
        "asterisk-core": [
            "/var/log/asterisk",
        ],
        "asterisk-full": [
            "/var/log/asterisk",
        ],
        "astguiclient": [
            "/var/log/astguiclient",
        ],
    }
    

