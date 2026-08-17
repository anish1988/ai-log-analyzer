import os


def is_jira_auto_create_enabled() -> bool:
    """
    Return whether automation is allowed to create Jira tickets.

    Accepted truthy values:
        true
        1
        yes
        on
    """

    value = os.getenv(
        "JIRA_AUTO_CREATE_ENABLED",
        "false",
    )

    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "on",
    }