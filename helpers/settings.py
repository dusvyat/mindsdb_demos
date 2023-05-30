from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent.parent.resolve()
DEMO_DB_PATH = (PACKAGE_ROOT / 'data' / 'qa' / 'qa.db').as_posix()
