import os
import asyncio
import aiohttp
from telegram import Bot

BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
bot = Bot(token=BOT_TOKEN)

games_notifications = {}

async def fetch_live_events(session):
    url = 'https://api.sofascore.com/api/v1/sport/tennis/events/live'
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def fetch_point_by_point(session, event_id):
    url = f'https://api.sofascore.com/api/v1/event/{event_id}/point-by-point'
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def process_game(session, event):
    event_id = event['id']
    home_name = event['homeTeam']['shortName']
    away_name = event['awayTeam']['shortName']
    game_slug = f"{home_name} x {away_name}"

    point_data = await fetch_point_by_point(session, event_id)

    # Log completo dos dados retornados da API para diagnóstico
    print(f"\nDados brutos da API para {game_slug}:\n{point_data}\n")

    if "serverPlayer" not in point_data or "currentGame" not in point_data:
        print(f"Jogo {game_slug} ignorado por falta de dados essenciais.")
        return

    server_id = point_data["serverPlayer"]
    current_game_number = point_data["currentGame"]

    if games_notifications.get(event_id) == current_game_number:
        return

    current_set = next(
        (s for s in point_data["sets"] if s["setNumber"] == point_data["currentSet"]),
        None
    )

    if not current_set:
        return

    current_game = next(
        (g for g in current_set["games"] if g["gameNumber"] == current_game_number),
        None
    )

    if current_game:
        points = current_game.get("points", [])

        if len(points) == 1 and points[0]["winningPlayer"] != server_id:
            server_name = home_name if server_id == event['homeTeam']['id'] else away_name
            receiver_name = away_name if server_name == home_name else home_name

            message = (f"⚠️ {server_name} perdeu o primeiro ponto sacando contra "
                       f"{receiver_name} ({game_slug}, game {current_game_number}).")

            await bot.send_message(chat_id=CHAT_ID, text=message)
            print(f"Notificação enviada: {message}")
            games_notifications[event_id] = current_game_number
async def monitor_all_games():
    await bot.send_message(chat_id=CHAT_ID, text="✅ Bot iniciado corretamente e enviando notificações!")
    print("Mensagem teste enviada ao Telegram.")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                live_events = await fetch_live_events(session)
                events = live_events.get('events', [])
                print(f"Número de jogos sendo monitorados: {len(events)}")

                tasks = [process_game(session, event) for event in events]
                await asyncio.gather(*tasks)

                await asyncio.sleep(10)
            except Exception as e:
                print(f"Erro na execução: {e}")
                await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        print("Bot inicializando corretamente.")
        asyncio.run(monitor_all_games())
    except Exception as e:
        print(f"Erro fatal ao iniciar o bot: {e}")
