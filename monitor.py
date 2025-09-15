import requests
import time
from notifier import send_alert
from uptime import record_check
from metrics import record_metric

def check_site(url: str) -> bool:
    start = time.time()
    try:
        r = requests.get(url, timeout=10)
        elapsed = int((time.time() - start) * 1000)
        if r.status_code == 200:
            print(f"✅ Online en {elapsed} ms")
            record_check(url, True)
            record_metric(url, "up", elapsed)
            return True
        else:
            print(f"⚠️  Código {r.status_code}")
            record_check(url, False)
            record_metric(url, "down", 0)
            send_alert(f"⚠️ Alerta: {url} responde con código {r.status_code}")
            return False
    except Exception as e:
        print("❌ Fuera de línea")
        record_check(url, False)
        record_metric(url, "down", 0)
        send_alert(f"❌ Alerta: {url} no responde. Error: {str(e)}")
        return False