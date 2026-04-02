"""Entry point – copies .env.example to .env if missing, then starts the server."""
import os
import shutil
from pathlib import Path

BASE = Path(__file__).parent

# Bootstrap .env
if not (BASE / ".env").exists() and (BASE / ".env.example").exists():
    shutil.copy(BASE / ".env.example", BASE / ".env")
    print("Created .env from .env.example — update it with your API keys.")

# Ensure upload dir
(BASE / "static" / "uploads").mkdir(parents=True, exist_ok=True)

from app import app  # noqa: E402 — import after env setup

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  Job Hunt Dashboard running at http://127.0.0.1:{port}\n")
    app.run(debug=True, host="127.0.0.1", port=port)
