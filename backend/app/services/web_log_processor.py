from pathlib import Path
from typing import List
import re

from app.schemas.log_analysis import (
    WebErrorBlockSchema,
    WebLogFetchResponse,
    WebLogFileSchema,
    WebLogLineSchema,
)

class WebLogProcessor:

    """
    Convert a complete log file into structured JSON.

    Responsibilities

        • Read every line

        • Detect start of every log entry

        • Group multiline entries

        • Build Error Blocks

        • Return WebLogFetchResponse
    """

    #######################################################################
    #
    # PUBLIC
    #
    #######################################################################

    def process(
        self,
        *,
        server: str,
        log_type: str,
        file_path: str,
        raw_lines: list[str],
    ) -> WebLogFetchResponse:

        print("\n")
        print("=" * 100)
        print("WEB LOG PROCESSOR")
        print("=" * 100)

        print(f"Server      : {server}")
        print(f"Log Type    : {log_type}")
        print(f"File        : {file_path}")
        print(f"Input Lines : {len(raw_lines)}")

        file_name = Path(file_path).name

        errors: list[WebErrorBlockSchema] = []

        current_block: list[WebLogLineSchema] = []

        start_line = 1

        error_number = 1

        #
        # Walk through every physical line
        #
        for line_number, raw in enumerate(raw_lines, start=1):

            line = self._create_line(
                file=file_name,
                line_number=line_number,
                raw=raw,
            )

            #
            # New log entry ?
            #
            if self._is_new_entry(raw):

                #
                # Save previous block
                #
                if current_block:

                    print(
                        f"Creating Error Block "
                        f"{error_number} "
                        f"({start_line}-{line_number-1})"
                    )

                    errors.append(

                        self._create_error(

                            error_number=error_number,

                            start_line=start_line,

                            end_line=line_number - 1,

                            lines=current_block,

                        )

                    )

                    error_number += 1

                #
                # Start new block
                #
                current_block = [line]

                start_line = line_number

            else:

                #
                # Continuation line
                #
                current_block.append(line)

        #
        # Last Block
        #
        if current_block:

            print(
                f"Creating Final Error Block "
                f"{error_number}"
            )

            errors.append(

                self._create_error(

                    error_number=error_number,

                    start_line=start_line,

                    end_line=len(raw_lines),

                    lines=current_block,

                )

            )

        print(f"Total Error Blocks : {len(errors)}")

        result = WebLogFileSchema(

            server=server,

            log_type=log_type,

            file_name=file_name,

            file_path=file_path,

            total_lines=len(raw_lines),

            total_errors=len(errors),

            errors=errors,

        )

        return WebLogFetchResponse(

            success=True,

            message="Log processed successfully.",

            results=[result],

        )

    #######################################################################
    #
    # PRIVATE
    #
    #######################################################################

    def _create_line(
        self,
        *,
        file: str,
        line_number: int,
        raw: str,
    ) -> WebLogLineSchema:

        return WebLogLineSchema(

            line_number=line_number,

            file=file,

            raw=raw.rstrip(),

        )

    def _is_new_entry(
        self,
        raw: str,
    ) -> bool:

        """
        Apache

        [Wed Aug 05 ...]

        Laravel

        [2026-08-05 ...]

        PHP

        [05-Aug-2026 ...]

        Today we simply detect '['.

        Later we can improve with Regex.
        """

        return raw.lstrip().startswith("[")

    def _create_error(
        self,
        *,
        error_number: int,
        start_line: int,
        end_line: int,
        lines: list[WebLogLineSchema],
    ) -> WebErrorBlockSchema:

        title = ""

        if lines:

            title = lines[0].raw

        return WebErrorBlockSchema(

            error_id=f"ERR-{error_number:05}",

            title=title,

            severity="UNKNOWN",

            timestamp=None,

            start_line=start_line,

            end_line=end_line,

            total_lines=len(lines),

            lines=lines,

        )