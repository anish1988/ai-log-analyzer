import asyncssh

from app.config.servers import ServerConfig
from app.log_fetchers.ssh_client import _get_connection
from pathlib import Path
import os
import shlex

async def read_web_log(
    server: ServerConfig,
    log_path: str,
) -> list[str]:
    """
    Read complete web log file.

    Returns:
        list[str]
    """

    print("\n")
    print("=" * 100)
    print("STEP-6 : read_web_log()")
    print("=" * 100)

    print(f"Server ID : {server.id}")
    print(f"Server IP : {server.ip}")
    print(f"Path      : {log_path}")

    print("=" * 100)
    print("WEB LOG FETCHER")
    print("=" * 100)

    print(f"Server   : {server.id}")
    print(f"Log Path : {log_path}")

    #if server.ip in ("local", "127.0.0.1", "localhost"):

    if server.ip == "127.0.0.1":

        print("\n")
        print("=" * 100)
        print("LOCAL FILE SYSTEM DEBUG")
        print("=" * 100)

        print(f"Current Working Directory : {os.getcwd()}")
        print(f"Requested Path            : {log_path}")

        path = resolve_local_path(log_path)

        print("=" * 80)
        print("PATH RESOLUTION")
        print("=" * 80)
        print(f"Host Path      : {log_path}")
        print(f"Container Path : {path}")
        print(path)
        print(path.exists())
        print(path.is_file())
        print("=" * 80)

        print(f"Absolute Path             : {path.resolve()}")
        print(f"Exists                    : {path.exists()}")
        print(f"Is File                   : {path.is_file()}")
        print(f"Is Directory              : {path.is_dir()}")

        print("\nEnvironment Variables")
        print(f"LOCAL_LOG_ROOT = {os.getenv('LOCAL_LOG_ROOT')}")

        print("\nListing /var")
        if Path("/var").exists():
            print(list(Path("/var").iterdir()))
        else:
            print("/var DOES NOT EXIST")

        print("\nListing /var/log")
        if Path("/var/log").exists():
            for item in Path("/var/log").iterdir():
                print(f"  {item}")
        else:
            print("/var/log DOES NOT EXIST")

        print("\nListing Parent Directory")

        if path.parent.exists():
            for item in path.parent.iterdir():
                print(f"  {item.name}")
        else:
            print(f"Parent directory does not exist : {path.parent}")

        if not path.exists():
            print("\n❌ FILE NOT FOUND")
            return []

        print("\n✅ FILE FOUND")

        with open(path, "r", encoding="utf-8", errors="ignore") as fp:
            lines = fp.read().splitlines()

        print(f"Total Lines : {len(lines)}")

        return lines

    print("Mode : SSH")

    conn = await _get_connection(server)

    command = f"cat '{log_path}'"

    print(command)

    result = await conn.run(
        command,
        check=False,
    )

    #
    # File missing
    #

    if result.exit_status != 0:

        print(result.stderr)

        return []

    #
    # Convert to list
    #

    lines = result.stdout.splitlines()

    print(f"Total Lines : {len(lines)}")

    return lines


async def read_web_log_incremental(
    server: ServerConfig,
    log_path: str,
    checkpoint=None,
) -> dict:
    """
    Phase 3.3 incremental log reader.

    Reads only the data appended after the last successful
    checkpoint.

    Checkpoint fields used:

        last_offset
        last_line_number
        file_size
        file_inode

    The function DOES NOT update the checkpoint.

    The checkpoint must be saved by the orchestrator only after
    the complete processing pipeline succeeds.

    Returns:

        {
            "lines": list[str],
            "start_line": int,
            "end_line": int,
            "start_offset": int,
            "end_offset": int,
            "file_size": int,
            "file_inode": int | None,
            "rotated": bool,
            "truncated": bool,
        }
    """

    # ============================================================
    # PREVIOUS CHECKPOINT
    # ============================================================

    previous_offset = (
        checkpoint.last_offset
        if checkpoint is not None
        else 0
    )

    previous_line = (
        checkpoint.last_line_number
        if checkpoint is not None
        else 0
    )

    previous_file_size = (
        checkpoint.file_size
        if checkpoint is not None
        else 0
    )

    previous_inode = (
        checkpoint.file_inode
        if checkpoint is not None
        else None
    )

    # ============================================================
    # LOCAL SERVER
    # ============================================================

    if server.ip == "127.0.0.1":

        path = resolve_local_path(log_path)

        if not path.exists() or not path.is_file():

            return {
                "lines": [],
                "start_line": previous_line + 1,
                "end_line": previous_line,
                "start_offset": previous_offset,
                "end_offset": previous_offset,
                "file_size": 0,
                "file_inode": None,
                "rotated": False,
                "truncated": False,
            }

        stat = path.stat()

        current_file_size = stat.st_size
        current_inode = stat.st_ino

        # --------------------------------------------------------
        # Detect rotation
        # --------------------------------------------------------

        rotated = (
            previous_inode is not None
            and current_inode != previous_inode
        )

        # --------------------------------------------------------
        # Detect truncation
        # --------------------------------------------------------

        truncated = (
            checkpoint is not None
            and current_file_size < previous_file_size
        )

        # --------------------------------------------------------
        # Decide where to start
        # --------------------------------------------------------

        if rotated or truncated:

            start_offset = 0
            start_line = 1

        else:

            start_offset = previous_offset
            start_line = previous_line + 1

        # --------------------------------------------------------
        # No new data
        # --------------------------------------------------------

        if current_file_size <= start_offset:

            return {
                "lines": [],
                "start_line": start_line,
                "end_line": previous_line,
                "start_offset": start_offset,
                "end_offset": current_file_size,
                "file_size": current_file_size,
                "file_inode": current_inode,
                "rotated": rotated,
                "truncated": truncated,
            }

        # --------------------------------------------------------
        # Read from byte offset
        # --------------------------------------------------------

        with open(
            path,
            "rb",
        ) as fp:

            fp.seek(start_offset)

            raw_data = fp.read()

        # --------------------------------------------------------
        # IMPORTANT:
        #
        # Do not checkpoint an incomplete final line.
        #
        # If the application is currently writing:
        #
        #     "ERROR something..."
        #
        # without a newline yet, we keep that partial line for
        # the next execution.
        # --------------------------------------------------------

        last_newline = raw_data.rfind(b"\n")

        if last_newline == -1:

            return {
                "lines": [],
                "start_line": start_line,
                "end_line": previous_line,
                "start_offset": start_offset,
                "end_offset": start_offset,
                "file_size": current_file_size,
                "file_inode": current_inode,
                "rotated": rotated,
                "truncated": truncated,
            }

        complete_data = raw_data[: last_newline + 1]

        end_offset = (
            start_offset
            + len(complete_data)
        )

        text = complete_data.decode(
            "utf-8",
            errors="ignore",
        )

        lines = text.splitlines()

        end_line = (
            start_line + len(lines) - 1
            if lines
            else previous_line
        )

        return {
            "lines": lines,
            "start_line": start_line,
            "end_line": end_line,
            "start_offset": start_offset,
            "end_offset": end_offset,
            "file_size": current_file_size,
            "file_inode": current_inode,
            "rotated": rotated,
            "truncated": truncated,
        }

    # ============================================================
    # REMOTE SERVER
    # ============================================================

    conn = await _get_connection(server)

    quoted_path = _shell_quote(log_path)

    # ============================================================
    # Get remote file metadata
    #
    # size + inode
    # ============================================================

    metadata_command = (
        "if test -f "
        + quoted_path
        + "; then "
        "stat -c '%s %i' "
        + quoted_path
        + "; "
        "else "
        "echo 'NOT_FOUND'; "
        "fi"
    )

    metadata_result = await conn.run(
        metadata_command,
        check=False,
    )

    metadata_output = (
        metadata_result.stdout.strip()
    )

    # ------------------------------------------------------------
    # File not found
    # ------------------------------------------------------------

    if (
        not metadata_output
        or metadata_output == "NOT_FOUND"
    ):

        return {
            "lines": [],
            "start_line": previous_line + 1,
            "end_line": previous_line,
            "start_offset": previous_offset,
            "end_offset": previous_offset,
            "file_size": previous_file_size,
            "file_inode": previous_inode,
            "rotated": False,
            "truncated": False,
        }

    # ------------------------------------------------------------
    # Parse:
    #
    #     size inode
    # ------------------------------------------------------------

    metadata_parts = metadata_output.split()

    if len(metadata_parts) < 2:

        raise RuntimeError(
            "Invalid remote file metadata returned for "
            f"{log_path}: {metadata_output}"
        )

    current_file_size = int(
        metadata_parts[0]
    )

    current_inode = int(
        metadata_parts[1]
    )

    # ============================================================
    # Detect rotation
    # ============================================================

    rotated = (
        previous_inode is not None
        and current_inode != previous_inode
    )

    # ============================================================
    # Detect truncation
    # ============================================================

    truncated = (
        checkpoint is not None
        and current_file_size < previous_file_size
    )

    # ============================================================
    # Decide starting position
    # ============================================================

    if rotated or truncated:

        start_offset = 0
        start_line = 1

    else:

        start_offset = previous_offset
        start_line = previous_line + 1

    # ============================================================
    # No new data
    # ============================================================

    if current_file_size <= start_offset:

        return {
            "lines": [],
            "start_line": start_line,
            "end_line": previous_line,
            "start_offset": start_offset,
            "end_offset": current_file_size,
            "file_size": current_file_size,
            "file_inode": current_inode,
            "rotated": rotated,
            "truncated": truncated,
        }

    # ============================================================
    # Read only new bytes
    #
    # tail -c +N uses a 1-based byte position.
    #
    # Our checkpoint offset is 0-based.
    #
    # Therefore:
    #
    #     start_byte = start_offset + 1
    # ============================================================

    start_byte = start_offset + 1

    command = (
        "tail -c +"
        + str(start_byte)
        + " "
        + quoted_path
    )

    result = await conn.run(
        command,
        check=False,
    )

    if result.exit_status != 0:

        raise RuntimeError(
            "Failed to read incremental remote log. "
            f"Server={server.id}, "
            f"File={log_path}, "
            f"Error={result.stderr.strip()}"
        )

    # asyncssh decodes stdout as text.
    raw_text = result.stdout

    if not raw_text:

        return {
            "lines": [],
            "start_line": start_line,
            "end_line": previous_line,
            "start_offset": start_offset,
            "end_offset": start_offset,
            "file_size": current_file_size,
            "file_inode": current_inode,
            "rotated": rotated,
            "truncated": truncated,
        }

    # ------------------------------------------------------------
    # Do not consume an incomplete final line.
    # ------------------------------------------------------------

    last_newline_index = raw_text.rfind("\n")

    if last_newline_index == -1:

        return {
            "lines": [],
            "start_line": start_line,
            "end_line": previous_line,
            "start_offset": start_offset,
            "end_offset": start_offset,
            "file_size": current_file_size,
            "file_inode": current_inode,
            "rotated": rotated,
            "truncated": truncated,
        }

    complete_text = raw_text[
        : last_newline_index + 1
    ]

    lines = complete_text.splitlines()

    # ------------------------------------------------------------
    # The SSH response is text.
    #
    # Calculate the consumed byte count using UTF-8.
    # ------------------------------------------------------------

    consumed_bytes = len(
        complete_text.encode("utf-8")
    )

    end_offset = (
        start_offset
        + consumed_bytes
    )

    end_line = (
        start_line + len(lines) - 1
        if lines
        else previous_line
    )

    return {
        "lines": lines,
        "start_line": start_line,
        "end_line": end_line,
        "start_offset": start_offset,
        "end_offset": end_offset,
        "file_size": current_file_size,
        "file_inode": current_inode,
        "rotated": rotated,
        "truncated": truncated,
    }


def resolve_local_path(log_path: str) -> Path:

    print("=" * 100)
    print("RESOLVE LOCAL PATH")
    print("=" * 100)

    print(f"Incoming Path : {log_path}")

    host_root = os.getenv("LOCAL_LOG_ROOT")

    print(f"LOCAL_LOG_ROOT : {host_root}")

    #
    # No host mapping configured
    #
    if not host_root:

        print("LOCAL_LOG_ROOT not configured.")

        return Path(log_path)

    #
    # Remove leading slash
    #
    relative_path = log_path.lstrip("/")

    print(f"Relative Path : {relative_path}")

    container_path = Path(host_root) / relative_path

    print(f"Container Path : {container_path}")

    print(f"Exists : {container_path.exists()}")

    return container_path




def _shell_quote(value: str) -> str:
    """
    Safely quote a value before using it in a remote shell command.
    """

    return shlex.quote(value)   