import threading
import time
from pathlib import Path

from document_scanner.stable_write import wait_for_stable_file


def test_wait_for_stable_file(tmp_path):
    target = tmp_path / "file.bin"

    def writer():
        with target.open("wb") as f:
            f.write(b"123")
            time.sleep(0.2)
            f.write(b"456")

    thread = threading.Thread(target=writer)
    thread.start()
    assert wait_for_stable_file(target, timeout=5, interval=0.1)
    thread.join()
