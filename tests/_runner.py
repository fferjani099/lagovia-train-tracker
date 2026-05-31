from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_pytest_for_current_file(file_path: str) -> None:
    import pytest

    raise SystemExit(pytest.main([file_path]))

