import requests
import time

# Substitua com os seus dados
TOKEN = 'SEU_TOKEN_DO_BOT'
CHAT_ID = 'SEU_CHAT_ID'
URL_TELEGRAM = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

# Set para controlar notificações já enviadas
enviados = set()

while True:
    try:
        resposta = requests.get("https://api.sofascore.com/api/v1/sport/tennis/events/live")
        dados = resposta.json()

        for evento in dados.get("events", []):
            if evento.get("status", {}).get("type") != "inprogress":
                continue

            # Filtrar apenas torneios ATP e Challenger masculino
            categoria = evento.get("tournament", {}).get("category", {}).get("name", "").lower()
            genero = evento.get("homeTeam", {}).get("gender", "")

            if genero != "M" or not ("atp" in categoria or "challenger" in categoria):
                continue

            id_jogo = evento["id"]
            home = evento["homeTeam"]["shortName"]
            away = evento["awayTeam"]["shortName"]
            first_to_serve = evento.get("firstToServe")

            # Cálculo do total de games disputados
            home_games = sum([evento["homeScore"].get(f"period{i}", 0) for i in range(1, 6)])
            away_games = sum([evento["awayScore"].get(f"period{i}", 0) for i in range(1, 6)])
            total_games = home_games + away_games

            # Determinar sacador atual com base no primeiro a sacar e no número total de games
            if not first_to_serve:
                continue  # pula se não sabemos quem começou sacando

            sacador_atual = first_to_serve if total_games % 2 == 0 else 2 if first_to_serve == 1 else 1

            home_point = evento["homeScore"].get("point", "")
            away_point = evento["awayScore"].get("point", "")
            placar = f"{home_point}-{away_point}"

            # Verificar se é o primeiro ponto do game
            if sacador_atual == 1 and placar == "0-15":
                game_id = f"{id_jogo}_{total_games}_0-15"
                if game_id not in enviados:
                    enviados.add(game_id)
                    mensagem = f"🎾 *{home}* começou sacando e perdeu o 1º ponto contra *{away}* (Placar: {placar})"
                    requests.post(URL_TELEGRAM, data={
                        'chat_id': CHAT_ID,
                        'text': mensagem,
                        'parse_mode': 'Markdown'
                    })

            elif sacador_atual == 2 and placar == "15-0":
                game_id = f"{id_jogo}_{total_games}_15-0"
                if game_id not in enviados:
                    enviados.add(game_id)
                    mensagem = f"🎾 *{away}* começou sacando e perdeu o 1º ponto contra *{home}* (Placar: {placar})"
                    requests.post(URL_TELEGRAM, data={
                        'chat_id': CHAT_ID,
                        'text': mensagem,
                        'parse_mode': 'Markdown'
                    })

    except Exception as e:
        print(f"Erro: {e}")

    time.sleep(3)
