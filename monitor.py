import requests
import time
from notifier import send_alert

def check_site(url: str) -> bool:
    """
    Revisa si la URL responde 200.
    Devuelve True si está OK; False si falló.
    Envía alerta por Telegram + mail en caso de error.
    """
    try:
        print(f"🔍 Revisando {url} ...", end=" ")
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            print("✅ Online")
            return True
        else:
            print(f"⚠️  Código {r.status_code}")
            send_alert(f"⚠️ Alerta: {url} responde con código {r.status_code}")
            return False
    except Exception as e:
        print("❌ Fuera de línea")
        send_alert(f"❌ Alerta: {url} no responde. Error: {str(e)}")
        return False


def live_status_bar(url: str) -> None:
    """
    Muestra una barra de progreso simple 0-100 % mientras revisa.
    Es solo visual en la consola; no afecta la lógica.
    """
    print(f"\n🔗 Monitoreando {url}")
    for i in range(0, 101, 10):
        bar = "█" * (i // 10) + "░" * (10 - i // 10)
        print(f"\r[{bar}] {i} %", end="", flush=True)
        time.sleep(0.05)
    print()  # salto de línea final
    check_site(url)


# Si lo ejecutas directamente: prueba
if __name__ == "__main__":
    live_status_bar("https://google.com")