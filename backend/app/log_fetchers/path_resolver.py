"""
Date + gzip aware remote path resolution.

Builds the ordered list of remote paths to try for one log file on one day:
 - if the file doesn't rotate by date, search the static path directly
 - if the target day is within `gzip_after_days`, try the plain dated file
 - if it's older, try the gzip-compressed dated file first (read via zcat)
 - either way, fall back to the un-dated base filename as a last resort,
   since "not every log file is generated with a date"

The caller (log_analysis_service) tries candidates in order and stops at
the first one that actually produces a result.
"""
import re
from dataclasses import dataclass
from datetime import date, timedelta

from app.config.log_files import LogFileConfig
from app.config.servers import Tier
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ResolvedLogPath:
    """
    Logical resolved log candidate.

    The resolver determines:
        - service
        - filename
        - gzip state
        - dated state

    The actual directory/full path is resolved by the
    local/remote fetcher because the available filesystem
    locations depend on the execution environment.
    """

    service: str
    filename: str

    is_gzipped: bool
    is_dated: bool

    directory: str | None = None
    full_path: str | None = None





def resolve_log_file_candidates(
    file: LogFileConfig,
    target_date: date,
    now: date | None = None,
) -> list[ResolvedLogPath]:

    now = now or date.today()

    #
    # Static logs
    #
    if file.tier != Tier.TELEPHONY or not file.has_date_pattern:

        return [
            ResolvedLogPath(
                service=file.service,
                filename=file.filename_template,
                is_gzipped=False,
                is_dated=False,
            )
        ]

    #
    # Telephony logs
    #
    date_str = target_date.strftime(file.date_pattern)

    #dated_filename = file.filename.replace("{date}", date_str)
    dated_filename = file.filename_template.format(date=date_str)

    age = (now - target_date).days

    candidates = []

    if age >= file.gzip_after_days:

        candidates.append(
            ResolvedLogPath(
                service=file.service,
                filename=f"{dated_filename}.gz",
                is_gzipped=True,
                is_dated=True,
            )
        )

        candidates.append(
            ResolvedLogPath(
                service=file.service,
                filename=dated_filename,
                is_gzipped=False,
                is_dated=True,
            )
        )

    else:

        candidates.append(
            ResolvedLogPath(
                service=file.service,
                filename=dated_filename,
                is_gzipped=False,
                is_dated=True,
            )
        )

    #
    # fallback
    #
    undated_filename = re.sub(
        r"[._-]?\{date\}",
        "",
        file.filename_template,
    )
    candidates.append(
        ResolvedLogPath(
            service=file.service,
            filename=undated_filename,
            is_gzipped=False,
            is_dated=False,
        )
    )

    logger.info("=" * 80)
    logger.info("Generated Candidates")

    for c in candidates:
        logger.info(
            f"Candidate => filename={c.filename}, "
            f"dated={c.is_dated}, "
            f"gzipped={c.is_gzipped}"
        )

    logger.info("=" * 80)

    return candidates

def each_day(start: date, end: date):
    cursor = start
    while cursor <= end:
        yield cursor
        cursor += timedelta(days=1)