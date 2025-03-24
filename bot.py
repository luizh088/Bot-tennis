import os
import requests
import time
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SOFASCORE_API_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"
alerted_games = set()
game_state = {}

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
        if first_to_serve is None:
            return None

        home_serving_first = first_to_serve == 1

        # Soma todos os games jogados em todos os sets
        total_games = 0
        for i in range(1, 6):  # até 5 sets
            home_games = event["homeScore"].get(f"period{i}")
            away_games = event["awayScore"].get(f"period{i}")
            if home_games is not None and away_games is not None:
                total_games += home_games + away_games

        # Define o sacador com base na ordem de saque e total de games jogados
        if (total_games % 2 == 0 and home_serving_first) or \
           (total_games % 2 == 1 and not home_serving_first):
            return "home"
        else:
            return "away"
    except Exception as e:
        print(f"Erro ao identificar sacador: {e}")
        return None

def formatar_set_e_game(event):
    try:
        last_period_raw = event.get("lastPeriod", "period1")

        # Extrai número do set (ex: "period2" → 2)
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

    server_name = event["homeTeam"]["name"] if server == "home" else event["awayTeam"]["name"]
    opponent_name = event["awayTeam"]["name"] if server == "home" else event["homeTeam"]["name"]
    home_score = event["homeScore"]["point"]
    away_score = event["awayScore"]["point"]
    set_info = formatar_set_e_game(event)

    game_key = f"{event_id}-{set_info}-{server}"
    if game_key in alerted_games:
        return

    if (server == "home" and home_score == "0" and away_score == "15") or \
       (server == "away" and away_score == "0" and home_score == "15"):
        mensagem = (
            f"🎾 *ALERTA*: {server_name} perdeu o *primeiro ponto no saque* contra {opponent_name}!\n"
            f"🏆 Torneio: {event['tournament']['name']}\n"
            f"📊 {set_info}\n"
            f"🧮 Placar: {event['homeTeam']['name']} {home_score} x {away_score} {event['awayTeam']['name']}"
        )
        enviar_mensagem_telegram(mensagem)
        alerted_games.add(game_key)
        game_state[event_id] = {
            "server": server,
            "set_info": set_info,
            "status": "alertado"
        }

def verificar_fim_game(event):
    event_id = event["id"]
    if event_id not in game_state:
        return

    info = game_state[event_id]
    server = info["server"]
    set_info = formatar_set_e_game(event)
    home_score = event["homeScore"]["point"]
    away_score = event["awayScore"]["point"]

    if home_score == "Game" or away_score == "Game":
        vencedor = event["homeTeam"]["name"] if home_score == "Game" else event["awayTeam"]["name"]
        sacador = event["homeTeam"]["name"] if server == "home" else event["awayTeam"]["name"]
        simbolo = "✅" if sacador == vencedor else "❌"
        mensagem = (
            f"🏁 *Fim do game!* ({set_info})\n"
            f"🎾 {sacador} sacou e {simbolo} *{'venceu' if simbolo == '✅' else 'perdeu'}* o game!\n"
            f"📊 Placar final do game: {event['homeTeam']['name']} {home_score} x {away_score} {event['awayTeam']['name']}"
        )
        enviar_mensagem_telegram(mensagem)
        del game_state[event_id]

def main():
    print("Iniciando monitoramento dos jogos de tênis...")
    while True:
        eventos = obter_jogos_ao_vivo()
        for evento in eventos:
            verificar_ponto_perdido(evento)
            verificar_fim_game(evento)
        time.sleep(1)

if __name__ == "__main__":
    main()
