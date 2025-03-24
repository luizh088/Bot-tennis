import requests
import time
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Armazena alertas enviados para evitar duplicação
alertas_enviados = set()

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Erro ao enviar alerta:", e)

def monitorar():
    url = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

    while True:
        try:
            resp = requests.get(url)
            eventos = resp.json().get("events", [])

            for ev in eventos:
                try:
                    home = ev.get("homeTeam", {}).get("name")
                    away = ev.get("awayTeam", {}).get("name")
                    score_home = ev.get("homeScore", {}).get("point")
                    score_away = ev.get("awayScore", {}).get("point")
                    serving = ev.get("firstToServe")
                    event_id = ev.get("id")

                    if None in (home, away, score_home, score_away):
                        continue

                    sacador = home if serving == 1 else away
                    placar = f"{score_home}-{score_away}"

                    if placar == "0-15" and event_id not in alertas_enviados:
                        msg = f"ALERTA: {sacador} perdeu o 1º ponto no game de saque!\nJogo: {home} x {away}"
                        send_alert(msg)
                        alertas_enviados.add(event_id)

                except Exception as e:
                    print("Erro ao processar evento:", e)

        except Exception as e:
            print("Erro na requisição:", e)

        time.sleep(1)

if __name__ == "__main__":
    monitorar()