import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print(f"TOKEN: {TOKEN}")
print(f"CHAT_ID: {CHAT_ID}")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": str(CHAT_ID),
    "text": "Teste de envio",
    "parse_mode": "Markdown"
}

print("== Enviando mensagem de teste ==")
r = requests.post(url, data=payload)
print("Status:", r.status_code)
print("Resposta:", r.text)