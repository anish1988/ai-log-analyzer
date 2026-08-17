"""
Phase 3.6 - Automation Log Source Resolver.

Resolves configured Web/DB logs to the first physical file
that actually exists.

Phase 3.6 scope:

    WEB:
        apache
        mysql
        syslog

    DB:
        mysql

Telephony is intentionally excluded.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import shlex

from app.config.log_files import (
    LogFileConfig,
)

from app.config.servers import (
    ServerConfig,
)

from app.log_fetchers.log_paths import (
    LOCAL_LOG_PATHS,
    REMOTE_LOG_PATHS,
)

from app.log_fetchers.path_resolver import (
    ResolvedLogPath,
    resolve_log_file_candidates,
)

from app.log_fetchers.ssh_client import (
    _get_connection,
)

from app.log_fetchers.web_log_fetcher import (
    resolve_local_path,
)


@dataclass(frozen=True)
class AutomationLogSource:

    server_id: str

    log_id: str

    log_type: str

    service: str

    filename: str

    file_path: str

    is_gzipped: bool

    is_dated: bool


class AutomationLogSourceResolver:

    LOCAL_HOSTS = {
        "local",
        "localhost",
        "127.0.0.1",
    }

    SUPPORTED_SERVICES = {
        "apache",
        "mysql",
        "syslog",
    }

    def resolve_candidates(
        self,
        *,
        server: ServerConfig,
        log_config: LogFileConfig,
        target_date: date | None = None,
    ) -> list[AutomationLogSource]:

        target_date = (
            target_date
            or date.today()
        )

        candidates = (
            resolve_log_file_candidates(
                log_config,
                target_date,
            )
        )

        log_type = (
            self._resolve_log_type(
                log_config
            )
        )

        sources: list[
            AutomationLogSource
        ] = []

        for candidate in candidates:

            if (
                candidate.service
                not in self.SUPPORTED_SERVICES
            ):

                raise ValueError(
                    "Unsupported Phase 3.6 service: "
                    f"{candidate.service}"
                )

            paths = (
                self._build_candidate_paths(
                    server=server,
                    candidate=candidate,
                )
            )

            for file_path in paths:

                sources.append(
                    AutomationLogSource(
                        server_id=server.id,
                        log_id=log_config.id,
                        log_type=log_type,
                        service=candidate.service,
                        filename=candidate.filename,
                        file_path=file_path,
                        is_gzipped=(
                            candidate.is_gzipped
                        ),
                        is_dated=(
                            candidate.is_dated
                        ),
                    )
                )

        return sources

    async def discover(
        self,
        *,
        server: ServerConfig,
        log_config: LogFileConfig,
        target_date: date | None = None,
    ) -> AutomationLogSource | None:
        """
        Find the first physical file that exists.

        Candidate order:

            1. resolver candidate order
            2. configured directory order

        No file contents are read here.
        """

        sources = (
            self.resolve_candidates(
                server=server,
                log_config=log_config,
                target_date=target_date,
            )
        )

        for source in sources:

            exists = await self._file_exists(
                server=server,
                file_path=source.file_path,
            )

            print(
                "FILE DISCOVERY | "
                f"server={server.id} | "
                f"log={source.log_id} | "
                f"path={source.file_path} | "
                f"exists={exists}"
            )

            if exists:

                print(
                    "FILE DISCOVERY SUCCESS | "
                    f"server={server.id} | "
                    f"log={source.log_id} | "
                    f"path={source.file_path}"
                )

                return source

        print(
            "FILE DISCOVERY | "
            f"No physical file found | "
            f"server={server.id} | "
            f"log={log_config.id}"
        )

        return None

    async def _file_exists(
        self,
        *,
        server: ServerConfig,
        file_path: str,
    ) -> bool:

        if (
            server.ip.lower()
            in self.LOCAL_HOSTS
        ):

            path = resolve_local_path(
                file_path
            )

            return (
                path.exists()
                and path.is_file()
            )

        connection = await _get_connection(
            server
        )

        command = (
            "test -f "
            + shlex.quote(file_path)
        )

        result = await connection.run(
            command,
            check=False,
        )

        return (
            result.exit_status == 0
        )

    @staticmethod
    def _build_candidate_paths(
        *,
        server: ServerConfig,
        candidate: ResolvedLogPath,
    ) -> list[str]:

        if (
            server.ip.lower()
            in AutomationLogSourceResolver.LOCAL_HOSTS
        ):

            registry = (
                LOCAL_LOG_PATHS
            )

        else:

            registry = (
                REMOTE_LOG_PATHS
            )

        directories = registry.get(
            candidate.service,
            [],
        )

        if not directories:

            raise ValueError(
                "No filesystem directories configured "
                f"for service '{candidate.service}'."
            )

        paths: list[str] = []

        for directory in directories:

            filename = candidate.filename

            #
            # Preserve existing Apache RHEL naming.
            #
            if "httpd" in directory:

                filename = (
                    filename
                    .replace(
                        "access.log",
                        "access_log",
                    )
                    .replace(
                        "error.log",
                        "error_log",
                    )
                )

            paths.append(
                f"{directory}/{filename}"
            )

        return paths

    @staticmethod
    def _resolve_log_type(
        log_config: LogFileConfig,
    ) -> str:

        mapping = {

            "web-apache-access":
                "apache_access",

            "web-apache-error":
                "apache_error",

            "web-syslog":
                "syslog",

            "web-mysql":
                "mysql_slow",

            "db-slow-query":
                "mysql_slow",
        }

        try:

            return mapping[
                log_config.id
            ]

        except KeyError:

            raise ValueError(
                "No Phase 3.6 log-type mapping exists "
                f"for '{log_config.id}'."
            )