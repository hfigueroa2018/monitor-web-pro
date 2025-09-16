import os
from telegram_notifier import send_telegram

DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _to_list(ids):
    if not ids:
        return []
    if isinstance(ids, list):
        arr = ids
    else:
        arr = [x.strip() for x in str(ids).replace(";", ",").split(",")]
    return [x for x in arr if x]


def send_alert(message: str, chat_ids=None):
    try:
        targets = _to_list(chat_ids) or _to_list(DEFAULT_CHAT_ID)
        if not targets:
            print("[NOTIFIER] Sin chat_id(s) configurado(s)")
            return False
        ok_any = False
        for cid in targets:
            if send_telegram(message, cid):
                ok_any = True
        return ok_any
    except Exception as e:
        print("[NOTIFIER] Error enviando alerta:", e)
        return False