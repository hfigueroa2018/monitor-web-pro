import json
import os

DB_FILE = "sites.json"

def load_sites():
    """
    Carga la lista de sitios desde el archivo JSON.
    Si el archivo no existe o está corrupto, devuelve una lista vacía.
    """
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Aseguramos que sea una lista
            if isinstance(data, list):
                return data
            else:
                return []
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        return []

def save_sites(sites):
    """
    Guarda la lista de sitios en el archivo JSON.
    """
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(sites, f, indent=2, ensure_ascii=False)
    except IOError as e:
        # Log del error (opcional)
        print(f"Error al guardar sitios: {e}")
        raise