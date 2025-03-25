import os
import requests
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SOFASCORE_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

# Set de identificadores únicos de alertas já enviados
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

            tournament_category = evento.get("tournament", {}).get("category", {}).get("name", "")
            unique_tournament_name = evento.get("tournament", {}).get("uniqueTournament", {}).get("name", "")

            if not (
                "ATP" in tournament_category or
                ("Challenger" in unique_tournament_name and evento.get("homeTeam", {}).get("gender") == "M")
            ):
                continue

            id_jogo = evento["id"]
            home = evento["homeTeam"]["shortName"]
            away = evento["awayTeam"]["shortName"]
            sacador_inicial = evento.get("firstToServe")  # 1 = home, 2 = away

            if sacador_inicial not in [1, 2]:
                continue

            # Somar total de games jogados em todos os sets
            home_total_games = 0
            away_total_games = 0
            for i in range(1, 6):
                home_total_games += evento["homeScore"].get(f"period{i}", 0)
                away_total_games += evento["awayScore"].get(f"period{i}", 0)
            total_games = home_total_games + away_total_games

            # Alternar sacador baseado no total de games
            if total_games % 2 == 0:
                sacador_atual = sacador_inicial
            else:
                sacador_atual = 2 if sacador_inicial == 1 else 1

            home_point = evento["homeScore"].get("point")
            away_point = evento["awayScore"].get("point")
            ponto = f"{home_point}-{away_point}"

            # Criar identificador único apenas por jogo e número de games (evita duplicação)
            game_id = f"{id_jogo}_{total_games}"

            if game_id in enviados:
                continue

            # Sacador perdeu o primeiro ponto
            if sacador_atual == 1 and ponto == "0-15":
                mensagem = f"🎾 *{home}* começou sacando e perdeu o 1º ponto contra *{away}* (Placar: {ponto})"
                enviados.add(game_id)
                print(f"[DEBUG] Notificação enviada - total_games: {total_games}, sacador: HOME ({home}), game_id: {game_id}")
                enviar_mensagem_telegram(mensagem)
            elif sacador_atual == 2 and ponto == "15-0":
                mensagem = f"🎾 *{away}* começou sacando e perdeu o 1º ponto contra *{home}* (Placar: {ponto})"
                enviados.add(game_id)
                print(f"[DEBUG] Notificação enviada - total_games: {total_games}, sacador: AWAY ({away}), game_id: {game_id}")
                enviar_mensagem_telegram(mensagem)
    except Exception as e:
        print(f"Erro ao verificar jogos: {e}")

# Loop contínuo (sem sleep, para Railway Background Worker)
while True:
    verificar_ponto_inicial()
    time.sleep(1)  # Opcional: remover no Railway e usar tasks/calls contínuas
