import requests
import time
import os

# Pegando as variáveis do ambiente (Render ou local)
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MESSAGE = "ALERTA: Game começou 0-30 contra o sacador!"

def send_alert():
    if not TOKEN or not CHAT_ID:
        print("Erro: BOT_TOKEN ou CHAT_ID não configurado.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": MESSAGE
    }

    try:
        response = requests.post(url, data=payload)
        print(f"Status do envio: {response.status_code}")
        print(f"Resposta da API: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# Loop infinito para envio contínuo (simulação)
while True:
    print("Enviando alerta...")
    send_alert()
    time.sleep(30)  # Aguarda 30 segundos entre envios (ajustável)