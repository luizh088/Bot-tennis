import requests
import os
import time

# Variáveis de ambiente
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# DEBUG: Verificar se variáveis estão corretas
print("== Testando variáveis de ambiente ==")
print("Tamanho do TOKEN:", len(TOKEN) if TOKEN else "TOKEN não definido")
print("Início do TOKEN:", TOKEN[:20] if TOKEN else "N/A")
print("Fim do TOKEN:", TOKEN[-10:] if TOKEN else "N/A")
print("CHAT_ID:", CHAT_ID)

# Teste de envio
def testar_envio():
    print("== Testando envio de mensagem ==")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "Teste: o bot está ativo e o token foi lido corretamente!"
    }
    try:
        response = requests.post(url, data=payload)
        print("Status do envio:", response.status_code)
        print("Resposta da API:", response.text)
    except Exception as e:
        print("Erro ao enviar:", e)

# Função principal
if __name__ == "__main__":
    testar_envio()
    # Loop para manter o container ativo
    while True:
        time.sleep(60)