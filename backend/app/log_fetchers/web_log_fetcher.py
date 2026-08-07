import asyncssh

from app.config.servers import ServerConfig
from app.log_fetchers.ssh_client import _get_connection
from pathlib import Path
import os

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