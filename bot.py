import requests
import time
import telegram

TOKEN = 'SEU_TOKEN_DO_BOT'
CHAT_ID = 'SEU_CHAT_ID'
bot = telegram.Bot(token=TOKEN)

enviados = set()

while True:
    try:
        resposta = requests.get("https://api.sofascore.com/api/v1/sport/tennis/events/live")
        dados = resposta.json()

        for evento in dados.get("events", []):
            if evento.get("status", {}).get("type") != "inprogress":
                continue

            # Filtro para jogos masculinos da ATP ou Challenger
            categoria = evento.get("tournament", {}).get("category", {}).get("name", "").lower()
            genero = evento.get("homeTeam", {}).get("gender")

            if genero != "M" or not ("atp" in categoria or "challenger" in categoria):
                continue

            id_jogo = evento["id"]
            home = evento["homeTeam"]["shortName"]
            away = evento["awayTeam"]["shortName"]
            first_to_serve = evento.get("firstToServe")

            home_sets = sum([evento["homeScore"].get(f"period{i}", 0) for i in range(1, 6)])
            away_sets = sum([evento["awayScore"].get(f"period{i}", 0) for i in range(1, 6)])
            total_games = home_sets + away_sets

            sacador_inicial = first_to_serve
            if sacador_inicial:
                sacador_atual = sacador_inicial if total_games % 2 == 0 else 2 if sacador_inicial == 1 else 1
            else:
                continue  # pula se não sabemos quem sacou primeiro

            home_point = evento["homeScore"].get("point", "")
            away_point = evento["awayScore"].get("point", "")
            placar = f"{home_point}-{away_point}"

            # Verifica se é o primeiro ponto do game e quem sacou
            if sacador_atual == 1 and placar == "0-15":
                game_id = f"{id_jogo}_{total_games}_0-15"
                if game_id not in enviados:
                    enviados.add(game_id)
                    msg = f"🎾 *{home}* começou sacando e perdeu o 1º ponto contra *{away}* (Placar: {placar})"
                    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

            elif sacador_atual == 2 and placar == "15-0":
                game_id = f"{id_jogo}_{total_games}_15-0"
                if game_id not in enviados:
                    enviados.add(game_id)
                    msg = f"🎾 *{away}* começou sacando e perdeu o 1º ponto contra *{home}* (Placar: {placar})"
                    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

    except Exception as e:
        print(f"Erro: {e}")

    time.sleep(3)
