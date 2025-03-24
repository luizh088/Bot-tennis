import os
import requests
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SOFASCORE_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

enviados = set()

def enviar_mensagem_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print("Status do envio:", response.status_code)
        print("Resposta da API:", response.text)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def verificar_ponto_inicial():
    try:
        resposta = requests.get(SOFASCORE_URL)
        dados = resposta.json()

        for evento in dados.get("events", []):
            if evento.get("status", {}).get("type") != "inprogress":
                continue

            id_jogo = evento["id"]
            home = evento["homeTeam"]["shortName"]
            away = evento["awayTeam"]["shortName"]
            first_to_serve = evento.get("firstToServe")

            # Somar total de games jogados em todos os sets
            home_total_games = 0
            away_total_games = 0
            for i in range(1, 6):
                home_total_games += evento["homeScore"].get(f"period{i}", 0)
                away_total_games += evento["awayScore"].get(f"period{i}", 0)
            total_games = home_total_games + away_total_games

            # Identificador único por game
            identificador = f"{id_jogo}-{total_games}"
            if identificador in enviados:
                continue

            # Determinar sacador atual
            if first_to_serve == 1:
                sacador_atual = 1 if total_games % 2 == 0 else 2
            else:
                sacador_atual = 2 if total_games % 2 == 0 else 1

            home_point = evento["homeScore"].get("point")
            away_point = evento["awayScore"].get("point")
            ponto = f"{home_point}-{away_point}"

            # Sacador perdeu o primeiro ponto
            if sacador_atual == 1 and ponto == "0-15":
                mensagem = f"🎾 *{home}* começou sacando e perdeu o 1º ponto contra *{away}* (Placar: {ponto})"
                enviados.add(identificador)
                enviar_mensagem_telegram(mensagem)
            elif sacador_atual == 2 and ponto == "15-0":
                mensagem = f"🎾 *{away}* começou sacando e perdeu o 1º ponto contra *{home}* (Placar: {ponto})"
                enviados.add(identificador)
                enviar_mensagem_telegram(mensagem)
    except Exception as e:
        print(f"Erro ao verificar jogos: {e}")

# Loop contínuo (sem sleep, para Railway Background Worker)
while True:
    verificar_ponto_inicial()
    time.sleep(5)  # Opcional: remover no Railway e usar tasks/calls contínuas
