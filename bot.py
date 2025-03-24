import os
import time
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    try:
        response = requests.post(url, data=payload)
        print("Status do envio:", response.status_code)
        print("Resposta da API:", response.text)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def format_score(home_score, away_score):
    sets = []
    max_sets = max(len(home_score), len(away_score))
    for i in range(max_sets):
        h = home_score[i] if i < len(home_score) else ""
        a = away_score[i] if i < len(away_score) else ""
        sets.append(f"{h}-{a}")
    return " | ".join(sets)

def obter_jogos_ao_vivo():
    try:
        response = requests.get(API_URL)
        if response.status_code != 200:
            print(f"Erro ao obter dados: {response.status_code}")
            return

        data = response.json()
        eventos = data.get("events", [])

        if not eventos:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{agora}: Nenhum jogo ao vivo no momento.")
            return

        for evento in eventos:
            try:
                home = evento["homeTeam"]["shortName"]
                away = evento["awayTeam"]["shortName"]
                home_score = evento["homeScore"].get("periods", {})
                away_score = evento["awayScore"].get("periods", {})

                home_set_scores = [str(v) for k, v in sorted(home_score.items())]
                away_set_scores = [str(v) for k, v in sorted(away_score.items())]

                score_str = format_score(home_set_scores, away_set_scores)
                mensagem = f"**AO VIVO**: {home} x {away}\nPlacar: {score_str}"
                print(mensagem)
                send_message(mensagem)

            except Exception as e:
                print(f"Erro ao processar evento: {e}")

    except Exception as e:
        print(f"Exceção ao obter jogos: {e}")

def main():
    while True:
        obter_jogos_ao_vivo()
        time.sleep(300)  # 5 minutos

if __name__ == "__main__":
    main()