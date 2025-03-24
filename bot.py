import os
import requests
import time
import re

# Variáveis de ambiente para token e ID do chat
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# URL da API da Sofascore
SOFASCORE_API_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

# Memória para controle de alertas enviados
alerted_games = set()

def obter_jogos_ao_vivo():
    try:
        response = requests.get(SOFASCORE_API_URL)
        response.raise_for_status()
        data = response.json()
        return data.get("events", [])
    except Exception as e:
        print(f"Erro ao obter jogos: {e}")
        return []

def identificar_sacador(event):
    try:
        first_to_serve = event.get("firstToServe")
        if first_to_serve not in [1, 2]:
            return None

        home_serving_first = first_to_serve == 1

        total_games = 0
        for i in range(1, 6):
            total_games += event["homeScore"].get(f"period{i}", 0)
            total_games += event["awayScore"].get(f"period{i}", 0)

        if (total_games % 2 == 0 and home_serving_first) or (total_games % 2 == 1 and not home_serving_first):
            return "home"
        else:
            return "away"
    except Exception as e:
        print(f"Erro ao identificar sacador: {e}")
        return None

def formatar_set_e_game(event):
    try:
        last_period_raw = event.get("lastPeriod", "period1")
        match = re.search(r"(\d+)", last_period_raw)
        if not match:
            return "Set desconhecido"

        period_index = int(match.group(1))
        set_nome = f"Set {period_index}"

        home_games = event["homeScore"].get(f"period{period_index}", 0)
        away_games = event["awayScore"].get(f"period{period_index}", 0)
        game_atual = home_games + away_games + 1

        return f"{set_nome} - Game {game_atual}"
    except Exception as e:
        print(f"Erro ao formatar set/game: {e}")
        return "Set desconhecido"

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

def verificar_ponto_perdido(event):
    event_id = event["id"]
    server = identificar_sacador(event)
    if not server:
        return

    match = re.search(r"(\d+)", event.get("lastPeriod", "period1"))
    set_index = int(match.group(1)) if match else 1
    home_games = event["homeScore"].get(f"period{set_index}", 0)
    away_games = event["awayScore"].get(f"period{set_index}", 0)
    game_id = home_games + away_games + 1
    game_key = f"{event_id}-set{set_index}-game{game_id}-{server}"

    if game_key in alerted_games:
        return

    home_score = event["homeScore"].get("point", "")
    away_score = event["awayScore"].get("point", "")

    if (server == "home" and home_score == "0" and away_score == "15") or \
       (server == "away" and away_score == "0" and home_score == "15"):

        server_name = event["homeTeam"]["name"] if server == "home" else event["awayTeam"]["name"]
        opponent_name = event["awayTeam"]["name"] if server == "home" else event["homeTeam"]["name"]
        set_info = formatar_set_e_game(event)

        mensagem = (
            f"\U0001F3BE *ALERTA*: {server_name} perdeu o *primeiro ponto no saque* contra {opponent_name}!\n"
            f"\U0001F3C6 Torneio: {event['tournament']['name']}\n"
            f"\U0001F4CA {set_info}\n"
            f"\U0001FAEE Placar: {event['homeTeam']['name']} {home_score} x {away_score} {event['awayTeam']['name']}"
        )

        enviar_mensagem_telegram(mensagem)
        alerted_games.add(game_key)

def main():
    print("Monitorando jogos de tênis ao vivo...")
    while True:
        eventos = obter_jogos_ao_vivo()
        for evento in eventos:
            verificar_ponto_perdido(evento)
        time.sleep(1)

if __name__ == "__main__":
    main()
