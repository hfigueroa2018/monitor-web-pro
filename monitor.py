import requests
import time

from metrics import record_metric
from models import Site

TIMEOUT = 15
ALLOWED_CODES = {200, 201, 202, 203, 204, 205, 206,
                 301, 302, 303, 304, 307, 308}
HEADERS = {"User-Agent": "Monitor-Web-Pro/1.0"}

def check_site(site) -> bool:
    url = site.url
    start = time.time()
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True, headers=HEADERS, verify=True)
        elapsed = int((time.time() - start) * 1000)
        print(f"[DEBUG] {url} -> status: {r.status_code}")

        if r.status_code in ALLOWED_CODES:
            print(f"✅ Online en {elapsed} ms")
            record_metric(site, "up", elapsed)
            return True
        else:
            print(f"⚠️  Código {r.status_code}")
            record_metric(site, "down", 0)
            return False
    except Exception as e:
        print(f"❌ Fuera de línea: {e}")
        record_metric(site, "down", 0)
        return False
