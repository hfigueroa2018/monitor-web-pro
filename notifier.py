import requests
from notifier import send_alert
from uptime import record_check

def check_site(url: str) -> bool:
    try:
        print(f"🔍 Revisando {url} ...", end=" ")
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            print("✅ Online")
            record_check(url, True)
            return True
        else:
            print(f"⚠️  Código {r.status_code}")
            record_check(url, False)
            send_alert(f"⚠️ Alerta: {url} responde con código {r.status_code}")
            return False
    except Exception as e:
        print("❌ Fuera de línea")
        record_check(url, False)
        send_alert(f"❌ Alerta: {url} no responde. Error: {str(e)}")
        return False