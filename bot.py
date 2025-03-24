import os
import requests
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

# Guarda estado do jogo para detectar mudanças
estado_anterior = {}

def enviar_alerta(texto):
    print("Enviando alerta...")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto
    }
    response = requests.post(url, data=payload)
    print("Status do envio:", response.status_code)
    print("Resposta da API:", response.text)

def identificar_sacador(evento):
    first_to_serve = evento.get("firstToServe")
    home_id = evento.get("homeTeam", {}).get("id")
    away_id = evento.get("awayTeam", {}).get("id")
    return home_id if first_to_serve == 1 else away_id

def monitorar():
    while True:
        try:
            response = requests.get(API_URL)
            eventos = response.json().get("events", [])

            for evento in eventos:
                try:
                    event_id = evento["id"]
                    home = evento.get("homeTeam", {}).get("shortName", "Desconhecido")
                    away = evento.get("awayTeam", {}).get("shortName", "Desconhecido")
                    home_id = evento["homeTeam"]["id"]
                    away_id = evento["awayTeam"]["id"]
                    sacador = identificar_sacador(evento)

                    home_point = evento.get("homeScore", {}).get("point")
                    away_point = evento.get("awayScore", {}).get("point")

                    if home_point is None or away_point is None:
                        continue

                    # Verifica mudança de game
                    estado_anterior_evento = estado_anterior.get(event_id, {})
                    ponto_anterior = estado_anterior_evento.get("pontos")
                    sacador_anterior = estado_anterior_evento.get("sacador")

                    pontos_atual = f"{home_point}-{away_point}"

                    # Sacador perdeu o primeiro ponto do game
                    if ponto_anterior != pontos_atual:
                        if pontos_atual in ["0-15", "0-30", "0-40"]:
                            if sacador == home_id and home_point == "0":
                                enviar_alerta(f"**ALERTA:** {home} sacando perdeu o primeiro ponto!\nPlacar: {home} {home_point} x {away_point} {away}")
                            elif sacador == away_id and away_point == "0":
                                enviar_alerta(f"**ALERTA:** {away} sacando perdeu o primeiro ponto!\nPlacar: {home} {home_point} x {away_point} {away}")

                    # Detectar fim do game
                    if ponto_anterior and pontos_atual == "0-0":
                        sacador_nome = home if sacador_anterior == home_id else away
                        vencedor = home if home_point == "0" else away
                        enviar_alerta(f"Game encerrado! {sacador_nome} sacava e o vencedor do game foi {vencedor}.")

                    # Atualiza estado do evento
                    estado_anterior[event_id] = {
                        "pontos": pontos_atual,
                        "sacador": sacador
                    }

                except Exception as e:
                    print(f"[Erro ao processar evento] {e}")

        except Exception as e:
            print(f"[Erro na requisição] {e}")

        time.sleep(1)

if __name__ == "__main__":
    print("Bot iniciado...")
    monitorar()