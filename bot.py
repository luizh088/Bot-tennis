import os
import asyncio
import aiohttp
from telegram import Bot

try:
    BOT_TOKEN = os.environ['BOT_TOKEN']
    CHAT_ID = os.environ['CHAT_ID']
    bot = Bot(token=BOT_TOKEN)
except KeyError as ke:
    print(f"Erro: Variável de ambiente não encontrada: {ke}")
    raise
except Exception as e:
    print(f"Erro ao inicializar o bot: {e}")
    raise

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
