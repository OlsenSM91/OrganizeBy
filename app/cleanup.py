from pathlib import Path
from datetime import datetime, timedelta
import shutil
import json

UPLOAD_DIR = Path(__file__).parent / "uploads"

for session_dir in UPLOAD_DIR.iterdir():
    session_file = session_dir / "session.json"
    if session_file.exists():
        try:
            data = json.loads(session_file.read_text())
            created = datetime.fromisoformat(data.get("created"))
            days = min(int(data.get("storage_days", 1)), 3)
            if datetime.now() > created + timedelta(days=days):
                print(f"[CLEANUP] Deleting expired session: {session_dir.name}")
                shutil.rmtree(session_dir)
        except Exception as e:
            print(f"[ERROR] Failed to parse {session_file}: {e}")

