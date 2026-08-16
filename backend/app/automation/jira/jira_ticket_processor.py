from typing import Any

from app.automation.config.automation_config import (
    is_jira_auto_create_enabled,
)
from app.integrations.jira.service import JiraService


class JiraTicketProcessor:
    """
    Creates Jira tickets for automation analysis results.

    One AI analysis result
        ->
    One Jira ticket
    """

    def __init__(self) -> None:
        self._jira_service = None

    @property
    def jira_service(self) -> JiraService:

        if self._jira_service is None:
            self._jira_service = JiraService()

        return self._jira_service

    async def process(
        self,
        analysis: dict[str, Any],
    ) -> dict[str, Any]:

        enabled = (
            is_jira_auto_create_enabled()
        )

        result = {
            "auto_create_enabled": enabled,
            "created": False,
            "issue_key": None,
            "issue_id": None,
            "issue_url": None,
            "error": None,
        }

        if not enabled:
            return result

        try:

            jira_result = (
                await self.jira_service.create_ticket(
                    analysis=analysis,
                )
            )

            issue_key = (
                jira_result.get("key")
                or ""
            )

            issue_id = (
                jira_result.get("id")
                or ""
            )

            if not issue_key:
                raise RuntimeError(
                    "Jira created the issue "
                    "but did not return an issue key."
                )

            base_url = (
                self.jira_service.client.base_url
                .rstrip("/")
            )

            issue_url = (
                f"{base_url}/browse/"
                f"{issue_key}"
            )

            result.update(
                {
                    "created": True,
                    "issue_key": issue_key,
                    "issue_id": issue_id,
                    "issue_url": issue_url,
                }
            )

            return result

        except Exception as exc:

            result["error"] = str(exc)

            return result