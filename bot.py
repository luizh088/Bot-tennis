import os
from telegram import Bot
import asyncio

TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

async def enviar_mensagem(mensagem):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=mensagem)

if __name__ == '__main__':
    mensagem = "🚀 Mensagem enviada automaticamente pelo meu bot rodando no Railway!"
    asyncio.run(enviar_mensagem(mensagem))
