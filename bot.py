import os
import requests
import time

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
        point_map = {"0": 0, "15": 1, "30": 2, "40": 3, "A": 4, "Game": 5}
        first_to_serve = event.get("firstToServe")
        if first_to_serve is None:
            return None

        home_serving = first_to_serve == 1
        home_point = point_map.get(event["homeScore"]["point"], 0)
        away_point = point_map.get(event["awayScore"]["point"], 0)

        total_points = home_point + away_point
        if (total_points % 2 == 0 and home_serving) or (total_points % 2 == 1 and not home_serving):
            return "home"
        else:
            return "away"
    except Exception as e:
        print(f"Erro ao identificar sacador: {e}")
        return None

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
    current_period = event.get("lastPeriod", "desconhecido")

    game_key = f"{event_id}-{current_period}-{server}"
    if game_key in alerted_games:
        return

    if (server == "home" and home_score == "0" and away_score == "15") or \
       (server == "away" and away_score == "0" and home_score == "15"):
        mensagem = (
            f"🎾 *ALERTA*: {server_name} perdeu o *primeiro ponto no saque* contra {opponent_name}!\n"
            f"🏆 Torneio: {event['tournament']['name']}\n"
            f"📊 Set atual: {current_period}\n"
            f"🧮 Placar: {event['homeTeam']['name']} {home_score} x {away_score} {event['awayTeam']['name']}"
        )
        enviar_mensagem_telegram(mensagem)
        alerted_games.add(game_key)
        game_state[event_id] = {
            "server": server,
            "set": current_period,
            "status": "alertado"
        }

def verificar_fim_game(event):
    event_id = event["id"]
    if event_id not in game_state:
        return

    info = game_state[event_id]
    server = info["server"]
    current_period = event.get("lastPeriod", "desconhecido")
    home_score = event["homeScore"]["point"]
    away_score = event["awayScore"]["point"]

    if home_score == "Game" or away_score == "Game":
        vencedor = event["homeTeam"]["name"] if home_score == "Game" else event["awayTeam"]["name"]
        sacador = event["homeTeam"]["name"] if server == "home" else event["awayTeam"]["name"]
        simbolo = "✅" if sacador == vencedor else "❌"
        mensagem = (
            f"🏁 *Fim do game* no set {current_period}!\n"
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
