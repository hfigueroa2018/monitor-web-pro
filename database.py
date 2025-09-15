import json

DB_FILE = "db.json"

def load_sites():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_sites(sites):
    with open(DB_FILE, "w") as f:
        json.dump(sites, f)