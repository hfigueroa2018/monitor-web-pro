import requests
from notifier import send_alert

def check_site(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            send_alert(f"⚠️ Alerta: {url} responde con código {r.status_code}")
            return False
        return True
    except Exception as e:
        send_alert(f"❌ Alerta: {url} no responde. Error: {str(e)}")
        return False