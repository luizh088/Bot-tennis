import os
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

# Guardar alertas já enviados
alertas_enviados = {}

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    resposta = requests.post(url, json=payload)
    print("Status do envio:", resposta.status_code)
    print("Resposta da API:", resposta.text)

def formatar_placar(home, away, game_score):
    home_point = game_score.get("home", "")
    away_point = game_score.get("away", "")
    return f"{home} {home_point} x {away_point} {away}"

def verificar_ponto_perdido(event):
    event_id = event["id"]
    home = event["homeTeam"]["shortName"]
    away = event["awayTeam"]["shortName"]
    server = event.get("firstToServe", 1)  # 1 = home, 2 = away

    home_point = event["homeScore"]["point"]
    away_point = event["awayScore"]["point"]

    game_key = f"{event_id}-{event['period']}-{server}"

    # Verifica se já mandamos alerta pra esse game
    if game_key in alertas_enviados:
        return

    perdeu_saque = False

    # Sacador perdeu o primeiro ponto?
    if server == 1 and home_point == "0" and away_point == "15":
        perdeu_saque = True
        sacador = home
        adversario = away
    elif server == 2 and away_point == "0" and home_point == "15":
        perdeu_saque = True
        sacador = away
        adversario = home
    else:
        return

    # Alerta novo
    alertas_enviados[game_key] = True

    torneio = event["tournament"]["name"]
    set_atual = event.get("lastPeriod", "Desconhecido")
    placar_atual = formatar_placar(home, away, event["homeScore"]) if server == 1 else formatar_placar(home, away, event["awayScore"])

    texto = (
        f"*ALERTA*: {sacador} perdeu o primeiro ponto no saque contra {adversario}!\n"
        f"Torneio: {torneio}\n"
        f"Set atual: {set_atual}\n"
        f"Placar atual: {placar_atual}"
    )
    enviar_mensagem(texto)

def mostrar_jogos_ao_vivo(events):
    for event in events:
        home = event["homeTeam"]["shortName"]
        away = event["awayTeam"]["shortName"]
        texto = f"**AO VIVO**: {home} x {away}\nPlacar: {formatar_placar(home, away, event['homeScore'])}"
        enviar_mensagem(texto)

def obter_jogos():
    try:
        resposta = requests.get(API_URL)
        if resposta.status_code == 200:
            return resposta.json().get("events", [])
        else:
            print("Erro ao obter jogos:", resposta.status_code)
    except Exception as e:
        print("Exceção ao obter jogos:", e)
    return []

def main():
    print("Iniciando monitoramento dos jogos de tênis...")
    while True:
        eventos = obter_jogos()
        if not eventos:
            print("Nenhum jogo ao vivo no momento.")
        for evento in eventos:
            verificar_ponto_perdido(evento)
        time.sleep(5)

if __name__ == "__main__":
    main()