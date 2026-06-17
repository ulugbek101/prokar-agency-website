import threading
import requests
from django.conf import settings


def _dispatch(token, chat_ids, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    for chat_id in chat_ids:
        try:
            requests.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=5,
            )
        except Exception:
            pass


def send_feedback_notification(feedback):
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_ids = getattr(settings, "TELEGRAM_ADMIN_IDS", [])
    if not token or not chat_ids:
        return

    phone = feedback.phone.strip()
    phone_digits = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

    text = (
        f"<b>{feedback.full_name}</b>\n"
        f'<a href="tel:{phone_digits}">{phone}</a>\n\n'
        f"<i>{feedback.body}</i>"
    )

    threading.Thread(
        target=_dispatch,
        args=(token, chat_ids, text),
        daemon=True,
    ).start()
