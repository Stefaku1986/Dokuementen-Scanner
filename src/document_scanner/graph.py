import logging
from datetime import datetime, time
from pathlib import Path
from typing import Optional

import msal
import requests
from zoneinfo import ZoneInfo

from .config import CalendarConfig, GraphConfig, OneDriveConfig

logger = logging.getLogger(__name__)


class GraphClient:
    def __init__(self, graph_cfg: GraphConfig):
        self.graph_cfg = graph_cfg
        if not graph_cfg.client_id:
            raise ValueError(
                "GraphClient benötigt eine client_id. Setze graph.enabled: false, falls Graph nicht genutzt werden soll."
            )
        authority = graph_cfg.authority or "https://login.microsoftonline.com/common"
        self.app = msal.PublicClientApplication(
            graph_cfg.client_id, authority=authority
        )
        self._token: Optional[dict] = None

    def _acquire_token(self) -> str:
        if self._token and "access_token" in self._token:
            return self._token["access_token"]
        flow = self.app.initiate_device_flow(scopes=self.graph_cfg.scopes)
        if "user_code" not in flow:
            raise RuntimeError("Keine Device-Code-Antwort erhalten")
        logger.info("Oeffne https://microsoft.com/devicelogin und gebe den Code %s ein", flow["user_code"])
        result = self.app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            raise RuntimeError(f"Token konnte nicht geholt werden: {result}")
        self._token = result
        return result["access_token"]

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._acquire_token()}"}

    def upload_file(self, onedrive: OneDriveConfig, target_relative: str, file_path: Path) -> str:
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:{onedrive.base_path}/{target_relative}:/content"
        logger.info("Uploade Datei nach OneDrive: %s", url)
        with file_path.open("rb") as f:
            response = requests.put(url, headers=self._headers(), data=f)
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Upload fehlgeschlagen: {response.status_code} {response.text}")
        return response.json().get("webUrl", target_relative)

    def create_calendar_event(
        self,
        calendar_cfg: CalendarConfig,
        title: str,
        event_date: datetime,
        description: str,
        amount: float,
        currency: str,
    ) -> str:
        calendar = calendar_cfg.calendar_id or "primary"
        url = f"https://graph.microsoft.com/v1.0/me/calendars/{calendar}/events"
        payload = {
            "subject": title,
            "body": {"contentType": "text", "content": description},
            "start": {"dateTime": event_date.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": (event_date.replace(minute=59)).isoformat(), "timeZone": "UTC"},
            "location": {"displayName": "Automatischer Reminder"},
        }
        response = requests.post(url, headers={**self._headers(), "Content-Type": "application/json"}, json=payload)
        if response.status_code not in (200, 201):
            raise RuntimeError(f"Event konnte nicht angelegt werden: {response.status_code} {response.text}")
        return response.json().get("id", "")
