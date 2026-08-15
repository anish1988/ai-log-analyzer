"""
Jira Cloud REST API client.

This module is responsible only for communicating with Jira.
Business logic and Jira description construction belong in
the Jira service layer.
"""

import os
from typing import Any

import httpx


class JiraClient:
    """
    Low-level Jira Cloud REST API client.
    """

    def __init__(self) -> None:
        self.base_url = (
            os.getenv("JIRA_BASE_URL", "")
            .strip()
            .rstrip("/")
        )

        self.email = (
            os.getenv("JIRA_EMAIL", "")
            .strip()
        )

        self.api_token = (
            os.getenv("JIRA_API_TOKEN", "")
            .strip()
        )

        self.project_key = (
            os.getenv("JIRA_PROJECT_KEY", "")
            .strip()
        )

        self.issue_type = (
            os.getenv("JIRA_ISSUE_TYPE", "Task")
            .strip()
        )

        self.timeout = 30.0

        self._validate_configuration()

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    def _validate_configuration(self) -> None:
        """
        Validate required Jira configuration.

        Secrets are intentionally never printed.
        """

        missing: list[str] = []

        if not self.base_url:
            missing.append("JIRA_BASE_URL")

        if not self.email:
            missing.append("JIRA_EMAIL")

        if not self.api_token:
            missing.append("JIRA_API_TOKEN")

        if not self.project_key:
            missing.append("JIRA_PROJECT_KEY")

        if not self.issue_type:
            missing.append("JIRA_ISSUE_TYPE")

        if missing:
            raise ValueError(
                "Missing Jira configuration: "
                + ", ".join(missing)
            )

    # =========================================================================
    # HTTP CLIENT
    # =========================================================================

    def _get_auth(self) -> tuple[str, str]:
        """
        Return Jira basic authentication credentials.

        Jira Cloud uses:
            email + API token
        """

        return (
            self.email,
            self.api_token,
        )

    def _get_headers(self) -> dict[str, str]:
        """
        Return common Jira API headers.
        """

        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    # =========================================================================
    # REQUEST HELPER
    # =========================================================================

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an HTTP request against Jira.

        Raises:
            RuntimeError:
                When Jira returns an unsuccessful response.
        """

        url = f"{self.base_url}{path}"

        try:

            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await client.request(
                    method=method,
                    url=url,
                    auth=self._get_auth(),
                    headers=self._get_headers(),
                    json=json,
                )

        except httpx.TimeoutException as exc:

            raise RuntimeError(
                "Jira request timed out."
            ) from exc

        except httpx.HTTPError as exc:

            raise RuntimeError(
                f"Unable to connect to Jira: {exc}"
            ) from exc

        # ---------------------------------------------------------------------
        # Successful response
        # ---------------------------------------------------------------------

        if response.is_success:

            if not response.content:
                return {}

            try:
                return response.json()

            except ValueError as exc:

                raise RuntimeError(
                    "Jira returned an invalid JSON response."
                ) from exc

        # ---------------------------------------------------------------------
        # Jira error response
        # ---------------------------------------------------------------------

        error_message = self._extract_error_message(
            response
        )

        raise RuntimeError(
            f"Jira API request failed "
            f"(HTTP {response.status_code}): "
            f"{error_message}"
        )

    # =========================================================================
    # ERROR HANDLING
    # =========================================================================

    @staticmethod
    def _extract_error_message(
        response: httpx.Response,
    ) -> str:
        """
        Extract a useful error message from Jira's response.
        """

        try:

            data = response.json()

        except ValueError:

            return response.text[:1000]

        error_messages = data.get(
            "errorMessages",
            [],
        )

        errors = data.get(
            "errors",
            {},
        )

        messages: list[str] = []

        if isinstance(
            error_messages,
            list,
        ):
            messages.extend(
                str(message)
                for message in error_messages
            )

        if isinstance(
            errors,
            dict,
        ):
            messages.extend(
                f"{field}: {message}"
                for field, message in errors.items()
            )

        if messages:
            return "; ".join(messages)

        return str(data)

    # =========================================================================
    # PROJECT
    # =========================================================================

    async def get_project(
        self,
    ) -> dict[str, Any]:
        """
        Retrieve the configured Jira project.
        """

        return await self._request(
            "GET",
            f"/rest/api/3/project/"
            f"{self.project_key}",
        )

    # =========================================================================
    # ISSUE TYPE
    # =========================================================================

    async def get_issue_types(
        self,
    ) -> list[dict[str, Any]]:
        """
        Retrieve issue types available for the project.
        """

        data = await self._request(
            "GET",
            f"/rest/api/3/project/"
            f"{self.project_key}/statuses",
        )

        if not isinstance(data, list):
            return []

        return [
            item
            for item in data
            if isinstance(item, dict)
        ]

    # =========================================================================
    # CREATE ISSUE
    # =========================================================================

    async def create_issue(
        self,
        *,
        summary: str,
        description: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Create a Jira issue.

        Parameters
        ----------
        summary:
            Jira issue summary/title.

        description:
            Jira Cloud Atlassian Document Format (ADF)
            document.
        """

        payload = {
            "fields": {
                "project": {
                    "key": self.project_key,
                },
                "summary": summary,
                "issuetype": {
                    "name": self.issue_type,
                },
                "description": description,
            }
        }

        return await self._request(
            "POST",
            "/rest/api/3/issue",
            json=payload,
        )

    # =========================================================================
    # ISSUE
    # =========================================================================

    async def get_issue(
        self,
        issue_key: str,
    ) -> dict[str, Any]:
        """
        Retrieve a Jira issue by key.
        """

        return await self._request(
            "GET",
            f"/rest/api/3/issue/{issue_key}",
        )