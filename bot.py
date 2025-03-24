import os
import aiohttp
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

jogos_alertados = {}

def formata_placar(event):
    try:
        p1 = event["homeScore"].get("period1", 0)
        p2 = event["awayScore"].get("period1", 0)
        return f"{p1}-{p2}"
    except:
        return "Sem placar"

async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)

async def monitorar():
    url = "https://api.sofascore.com/api/v1/sport/tennis/events/live"

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url) as response:
                    data = await response.json()

                for event in data.get("events", []):
                    try:
                        match_id = event["id"]
                        home = event["homeTeam"]["name"]
                        away = event["awayTeam"]["name"]
                        score_home = event.get("homeScore", {}).get("point", "0")
                        score_away = event.get("awayScore", {}).get("point", "0")
                        sacador = home if event.get("firstToServe") == 1 else away
                        adversario = away if sacador == home else home

                        ponto = f"{score_home}-{score_away}" if sacador == home else f"{score_away}-{score_home}"

                        # Alerta 0-15
                        if ponto == "0-15" and match_id not in jogos_alertados:
                            jogos_alertados[match_id] = {"sacador": sacador}
                            placar = formata_placar(event)
                            await send_telegram_message(
                                f"**ALERTA**: {sacador} perdeu o primeiro ponto no saque contra {adversario}!\nPlacar atual do set: {placar}"
                            )

                        # Game reiniciado (0-0) depois do alerta
                        if match_id in jogos_alertados and ponto == "0-0":
                            vencedor = sacador if score_home == "15" else adversario
                            await send_telegram_message(
                                f"**FIM DO GAME**\n{sacador} sacava contra {adversario}\n**{vencedor} venceu o game**"
                            )
                            del jogos_alertados[match_id]

                    except Exception as e:
                        print(f"Erro no evento: {e}")

            except Exception as e:
                print(f"Erro geral: {e}")

# Execução
if __name__ == "__main__":
    asyncio.run(monitorar())