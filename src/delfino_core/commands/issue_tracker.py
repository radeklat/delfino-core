from abc import ABC, abstractmethod
from base64 import b64encode

from click import Abort

from delfino_core.config import IssueTrackingConfig

try:
    import httpx
    from httpx import codes
except ImportError:
    pass


class _BaseIssuerTrackerClient(ABC):
    def __init__(self, settings: IssueTrackingConfig):
        self._settings = settings

    @abstractmethod
    def get_issue_title(self, issue_number: int) -> str:
        """Fetches the title of an issue using its issue number."""


class JiraClient(_BaseIssuerTrackerClient):
    def _headers(self) -> dict[str, str]:
        token = b64encode(f"{self._settings.username}:{self._settings.api_key}".encode()).decode()
        return {
            "Accept": "application/json",
            "Authorization": f"Basic {token}",
        }

    def get_issue_title(self, issue_number: int) -> str:
        issue_key = f"{self._settings.issue_prefix.rstrip('-')}-{issue_number}"
        url = f"{self._settings.tracker_url.rstrip('/')}/rest/api/3/issue/{issue_key}"

        response = httpx.get(url, headers=self._headers())

        if response.status_code == codes.OK:
            data = response.json()
            return data["fields"]["summary"]

        raise Abort(f"Failed to fetch issue: {response.status_code}, {response.text}")
