import os
import requests
import time

# Pega variáveis do ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)

def testar_envio():
    print("== Testando envio de mensagem ==")
    if not BOT_TOKEN or not CHAT_ID:
        print("Erro: BOT_TOKEN ou CHAT_ID não definidos.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "Mensagem de teste via Railway",
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        print("Status do envio:", response.status_code)
        print("Resposta da API:", response.text)
    except Exception as e:
        print("Erro ao tentar enviar:", e)

# Chamada para teste antes de iniciar o monitoramento
testar_envio()

# Após confirmar que o envio funciona, você pode colocar a lógica de monitoramento aqui:
# def monitorar_jogos():
#     while True:
#         ...
#         time.sleep(1)

# if __name__ == "__main__":
#     monitorar_jogos()