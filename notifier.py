from telegram_notifier import send_telegram

def send_alert(message: str):
    print("Enviando alerta por Telegram...")
    send_telegram(message)