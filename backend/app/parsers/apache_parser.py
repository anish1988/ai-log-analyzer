"""
Apache Log Parser

Version 1

Every non-empty line is treated as one error block.

Future Versions
---------------
- Multi-line PHP stack traces
- Apache module grouping
- Severity detection
- Timestamp parsing
- Client IP parsing
"""

import re

from app.parsers.base_parser import BaseLogParser

from app.schemas.log_analysis import (
    WebErrorBlockSchema,
    WebLogFileSchema,
    WebLogLineSchema,
)


#
# Example
#
# [Tue Jul 22 13:55:20.123456 2025]
#
APACHE_TIMESTAMP_PATTERN = re.compile(
    r"^\[[A-Za-z]{3}\s+[A-Za-z]{3}"
)


class ApacheParser(BaseLogParser):

    def parse(
        self,
        *,
        server: str,
        log_type: str,
        file_name: str,
        file_path: str,
        raw_lines: list[str],
    ) -> WebLogFileSchema:

        print("=" * 100)
        print("APACHE PARSER")
        print("=" * 100)

        print(f"Total Raw Lines : {len(raw_lines)}")

        errors: list[WebErrorBlockSchema] = []

        error_counter = 1

        for line_number, raw in enumerate(raw_lines, start=1):

            #
            # Ignore empty lines
            #
            if not raw.strip():
                continue

            log_line = WebLogLineSchema(

                line_number=line_number,

                file=file_name,

                raw=raw,

            )

            errors.append(

                WebErrorBlockSchema(

                    error_id=f"ERR-{error_counter:05}",

                    title=raw,

                    severity="UNKNOWN",

                    timestamp="",

                    start_line=line_number,

                    end_line=line_number,

                    total_lines=1,

                    lines=[log_line],

                )

            )

            print(
                f"Apache Error {error_counter} "
                f"(Line {line_number})"
            )

            error_counter += 1

        print("=" * 100)
        print(f"Total Errors : {len(errors)}")
        print("=" * 100)

        return WebLogFileSchema(

            server=server,

            log_type=log_type,

            file_name=file_name,

            file_path=file_path,

            total_lines=len(raw_lines),

            total_errors=len(errors),

            errors=errors,

        )