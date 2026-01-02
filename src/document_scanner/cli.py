import argparse
import logging
import sys
from pathlib import Path

from .config import load_config
from .graph import GraphClient
from .processor import DocumentProcessor
from .watcher import watch_directory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_service(config_path: Path):
    cfg = load_config(config_path)
    root_dir = Path(__file__).resolve().parents[2]
    processor = DocumentProcessor(cfg, root_dir / "config" / "llm_schema.json")
    graph = GraphClient(cfg.graph)

    def handle(path: Path):
        try:
            report_path, extracted = processor.process_file(path)
            onedrive_link = processor.upload(graph, report_path, extracted)
            processor.create_calendar_event(graph, extracted, onedrive_link)
            archive_target = cfg.hotfolder.archive_dir / path.name
            archive_target.parent.mkdir(parents=True, exist_ok=True)
            path.rename(archive_target)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Fehler bei Verarbeitung %s: %s", path, exc)
            fail_target = cfg.hotfolder.failed_dir / path.name
            fail_target.parent.mkdir(parents=True, exist_ok=True)
            path.rename(fail_target)

    observer = watch_directory(cfg.hotfolder.input_dir, handle)
    try:
        observer.join()
    except KeyboardInterrupt:
        logger.info("Beende Service")
        observer.stop()
        observer.join()


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="Dokumenten-Scanner Service")
    parser.add_argument("config", type=Path, help="Pfad zur config.yaml")
    args = parser.parse_args(argv)
    run_service(args.config)


if __name__ == "__main__":
    main()
