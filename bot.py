import requests
import time
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MESSAGE = "ALERTA: Game começou 0-30 contra o sacador!"

def send_alert():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": MESSAGE}
    requests.post(url, data=payload)

while True:
    send_alert()
    time.sleep(300)  # Espera 5 minutos (300 segundos)