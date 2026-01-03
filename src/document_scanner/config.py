import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


def load_config(config_path: Path) -> "ScannerConfig":
    load_dotenv()
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return ScannerConfig.from_dict(data)


@dataclass
class GraphConfig:
    enabled: bool = True
    client_id: str = ""
    tenant_id: str = ""
    authority: str | None = None
    scopes: list[str] = field(
        default_factory=lambda: [
            "https://graph.microsoft.com/Files.ReadWrite.All",
            "https://graph.microsoft.com/Calendars.ReadWrite",
            "offline_access",
        ]
    )


@dataclass
class HotfolderConfig:
    input_dir: Path
    processed_dir: Path
    failed_dir: Path
    archive_dir: Path


@dataclass
class LLMConfig:
    enabled: bool = True
    model: str = "gpt-4o-mini"
    temperature: float = 0
    api_key_env: str = "OPENAI_API_KEY"


@dataclass
class OCRConfig:
    enabled: bool = True
    tesseract_cmd: Optional[str] = None
    language: str = "deu"


@dataclass
class CalendarConfig:
    calendar_id: Optional[str] = None
    default_time: str = "09:00"


@dataclass
class OneDriveConfig:
    base_path: str


@dataclass
class ScannerConfig:
    hotfolder: HotfolderConfig
    onedrive: OneDriveConfig
    graph: GraphConfig
    llm: LLMConfig = field(default_factory=LLMConfig)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    calendar: CalendarConfig = field(default_factory=CalendarConfig)
    timezone: str = "Europe/Berlin"
    log_level: str = "INFO"

    @classmethod
    def from_dict(cls, data: dict) -> "ScannerConfig":
        env = os.environ
        hotfolder = HotfolderConfig(
            input_dir=Path(data["hotfolder"]["input_dir"]),
            processed_dir=Path(data["hotfolder"]["processed_dir"]),
            failed_dir=Path(data["hotfolder"]["failed_dir"]),
            archive_dir=Path(data["hotfolder"]["archive_dir"]),
        )
        graph_cfg = data.get("graph", {})
        tenant = env.get("GRAPH_TENANT_ID", graph_cfg.get("tenant_id", ""))
        graph = GraphConfig(
            enabled=graph_cfg.get("enabled", True),
            client_id=env.get("GRAPH_CLIENT_ID", graph_cfg.get("client_id", "")),
            tenant_id=tenant,
            authority=graph_cfg.get(
                "authority",
                f"https://login.microsoftonline.com/{tenant}" if tenant else "https://login.microsoftonline.com/common",
            ),
        )
        llm_cfg = data.get("llm", {})
        llm = LLMConfig(
            enabled=llm_cfg.get("enabled", True),
            model=llm_cfg.get("model", "gpt-4o-mini"),
            temperature=llm_cfg.get("temperature", 0),
            api_key_env=llm_cfg.get("api_key_env", "OPENAI_API_KEY"),
        )
        ocr_cfg = data.get("ocr", {})
        ocr = OCRConfig(
            enabled=ocr_cfg.get("enabled", True),
            tesseract_cmd=ocr_cfg.get("tesseract_cmd"),
            language=ocr_cfg.get("language", "deu"),
        )
        calendar_cfg = data.get("calendar", {})
        calendar = CalendarConfig(
            calendar_id=calendar_cfg.get("calendar_id"),
            default_time=calendar_cfg.get("default_time", "09:00"),
        )
        onedrive_cfg = data.get("onedrive", {})
        onedrive = OneDriveConfig(base_path=onedrive_cfg.get("base_path", "/Dokumente"))
        return cls(
            hotfolder=hotfolder,
            onedrive=onedrive,
            graph=graph,
            llm=llm,
            ocr=ocr,
            calendar=calendar,
            timezone=data.get("timezone", "Europe/Berlin"),
            log_level=data.get("log_level", "INFO"),
        )
