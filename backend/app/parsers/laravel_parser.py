"""
Laravel Log Parser

A Laravel error starts with:

[YYYY-MM-DD HH:MM:SS]

Everything until the next timestamp belongs
to the same error block.
"""

import re
from pathlib import Path

from app.parsers.base_parser import BaseLogParser
from app.schemas.log_analysis import (
    WebErrorBlockSchema,
    WebLogFileSchema,
    WebLogLineSchema,
)


#
# Example
#
# [2019-02-04 11:42:00]
#
LARAVEL_TIMESTAMP_PATTERN = re.compile(
    r"^\[\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"
)


class LaravelParser(BaseLogParser):

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
        print("LARAVEL PARSER")
        print("=" * 100)

        print(f"Total Raw Lines : {len(raw_lines)}")

        errors: list[WebErrorBlockSchema] = []

        current_lines: list[WebLogLineSchema] = []

        current_start_line = 1

        error_counter = 1

        #
        # Read file line by line
        #
        for line_number, raw in enumerate(raw_lines, start=1):

            #
            # New Laravel Error?
            #
            if LARAVEL_TIMESTAMP_PATTERN.match(raw):

                #
                # Save previous error
                #
                if current_lines:

                    errors.append(

                        WebErrorBlockSchema(

                            error_id=f"ERR-{error_counter:05}",

                            title=current_lines[0].raw,

                            severity="UNKNOWN",

                            timestamp=current_lines[0].raw,

                            start_line=current_start_line,

                            end_line=current_lines[-1].line_number,

                            total_lines=len(current_lines),

                            lines=current_lines,

                        )

                    )

                    print(
                        f"Completed Error {error_counter} "
                        f"({current_start_line} - {current_lines[-1].line_number})"
                    )

                    error_counter += 1

                #
                # Start New Error
                #
                current_lines = []

                current_start_line = line_number

            #
            # Append line
            #
            current_lines.append(

                WebLogLineSchema(

                    line_number=line_number,

                    file=file_name,

                    raw=raw,

                )

            )

        #
        # Save Last Error
        #
        if current_lines:

            errors.append(

                WebErrorBlockSchema(

                    error_id=f"ERR-{error_counter:05}",

                    title=current_lines[0].raw,

                    severity="UNKNOWN",

                    timestamp=current_lines[0].raw,

                    start_line=current_start_line,

                    end_line=current_lines[-1].line_number,

                    total_lines=len(current_lines),

                    lines=current_lines,

                )

            )

            print(
                f"Completed Error {error_counter} "
                f"({current_start_line} - {current_lines[-1].line_number})"
            )

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