import os
import requests
import time
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"  # API REAL

sacadores_alertados = {}
status_ultimo_alerta = {}

def enviar_mensagem(texto):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"\nEnviando alerta...\nStatus do envio: {response.status_code}\nResposta da API: {response.text}\n")

def formatar_placar(home, away):
    sets = []
    for i in range(1, 6):
        s_home = home.get(f'period{i}')
        s_away = away.get(f'period{i}')
        if s_home is not None or s_away is not None:
            sets.append(f"{s_home if s_home is not None else 0} x {s_away if s_away is not None else 0}")
    return " | ".join(sets)

def monitorar_jogos():
    while True:
        try:
            response = requests.get(API_URL)
            data = response.json()
            eventos = data.get("events", [])

            if not eventos:
                print(f"{datetime.now()}: Nenhum jogo ao vivo no momento.")
                time.sleep(300)
                continue

            for jogo in eventos:
                home = jogo["homeTeam"]["name"]
                away = jogo["awayTeam"]["name"]
                current_set = jogo.get("lastPeriod", "Desconhecido")
                tournament = jogo["tournament"]["name"]
                event_id = jogo["id"]
                first_to_serve = jogo.get("firstToServe", 1)

                score_home = jogo["homeScore"]
                score_away = jogo["awayScore"]
                point_home = score_home.get("point", "")
                point_away = score_away.get("point", "")
                placar = formatar_placar(score_home, score_away)

                sacador = home if first_to_serve == 1 else away
                recebedor = away if first_to_serve == 1 else home
                chave = f"{event_id}_{current_set}"

                if point_home == "15" and point_away == "0" and sacador == home:
                    if sacadores_alertados.get(chave) != "alertado":
                        mensagem = f"ALERTA: {home} perdeu o primeiro ponto no saque contra {away}!\nTorneio: {tournament}\nSet atual: {current_set}\nPlacar atual: {home} {point_home} x {point_away} {away}"
                        enviar_mensagem(mensagem)
                        sacadores_alertados[chave] = "alertado"
                        status_ultimo_alerta[chave] = "sacador"

                elif point_away == "15" and point_home == "0" and sacador == away:
                    if sacadores_alertados.get(chave) != "alertado":
                        mensagem = f"ALERTA: {away} perdeu o primeiro ponto no saque contra {home}!\nTorneio: {tournament}\nSet atual: {current_set}\nPlacar atual: {home} {point_home} x {point_away} {away}"
                        enviar_mensagem(mensagem)
                        sacadores_alertados[chave] = "alertado"
                        status_ultimo_alerta[chave] = "sacador"

                if sacadores_alertados.get(chave) == "alertado":
                    if point_home == "" and point_away == "":
                        if score_home["current"] > score_away["current"]:
                            vencedor = home
                        else:
                            vencedor = away

                        if vencedor == sacador:
                            resultado = "✅ VENCEU o game!"
                        else:
                            resultado = "❌ PERDEU o game!"

                        enviar_mensagem(f"{sacador} {resultado}\nJogo: {home} x {away}\nPlacar: {placar}")
                        sacadores_alertados[chave] = "resolvido"

        except Exception as e:
            print(f"Exceção ao obter jogos: {e}")

        time.sleep(1)

if __name__ == "__main__":
    print("Iniciando monitoramento dos jogos de tênis...")
    monitorar_jogos()