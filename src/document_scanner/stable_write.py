import time
from pathlib import Path
from typing import Optional


def wait_for_stable_file(path: Path, timeout: float = 30.0, interval: float = 0.5) -> bool:
    """Return True when file size stays constant for two checks within timeout."""
    end_time = time.time() + timeout
    last_size: Optional[int] = None
    while time.time() < end_time:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            time.sleep(interval)
            continue
        if size == 0:
            time.sleep(interval)
            continue
        if last_size is None:
            last_size = size
            time.sleep(interval)
            continue
        if size == last_size:
            return True
        last_size = size
        time.sleep(interval)
    return False
