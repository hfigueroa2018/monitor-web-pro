import json
import os

DB_FILE = "sites.json"

def load_sites():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Migra formato viejo [str] → nuevo [{},..]
        if data and isinstance(data[0], str):
            return [{"url": u, "chat_id": None} for u in data]
        return data
    except Exception:
        return []

def save_sites(sites):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(sites, f, indent=2, ensure_ascii=False)