import os
import requests
import time
import urllib3

# Configurações iniciais
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://api.exemplo.com/tennis/live"  # Substitua pela URL real da API de jogos ao vivo

# Desabilitar avisos de insegurança (caso desabilite a verificação SSL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Função para enviar mensagens no Telegram
def enviar_alerta(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Erro ao enviar alerta: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exceção ao enviar alerta: {e}")

# Função para obter dados dos jogos ao vivo
def obter_jogos_ao_vivo():
    try:
        response = requests.get(API_URL, verify=False)  # Desabilitar verificação SSL
        if response.status_code == 200:
            return response.json()  # Supondo que a API retorne JSON
        else:
            print(f"Erro ao obter jogos: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exceção ao obter jogos: {e}")
        return []

# Função principal de monitoramento
def monitorar_jogos():
    jogos_monitorados = {}  # Dicionário para armazenar o estado dos jogos monitorados

    while True:
        jogos_ao_vivo = obter_jogos_ao_vivo()

        for jogo in jogos_ao_vivo:
            jogo_id = jogo['id']
            sacador = jogo['sacador']
            pontos = jogo['pontos']  # Estrutura que contém os pontos atuais do game
            game_em_andamento = jogo['game_em_andamento']  # Indicador se o game está em andamento

            # Inicializa o estado do jogo se ainda não estiver monitorado
            if jogo_id not in jogos_monitorados:
                jogos_monitorados[jogo_id] = {
                    'sacador': sacador,
                    'primeiro_ponto_perdido': False,
                    'game_concluido': False,
                    'vencedor_game': None
                }

            estado_jogo = jogos_monitorados[jogo_id]

            # Verifica se o sacador perdeu o primeiro ponto do game
            if not estado_jogo['primeiro_ponto_perdido'] and pontos:
                primeiro_ponto = pontos[0]
                if primeiro_ponto['vencedor'] != sacador:
                    mensagem = f"Alerta: No jogo {jogo_id}, o sacador {sacador} perdeu o primeiro ponto do game."
                    enviar_alerta(mensagem)
                    estado_jogo['primeiro_ponto_perdido'] = True

            # Se o sacador perdeu o primeiro ponto, monitorar o resultado do game
            if estado_jogo['primeiro_ponto_perdido'] and not estado_jogo['game_concluido']:
                if not game_em_andamento:
                    vencedor_game = jogo['vencedor_game']
                    if vencedor_game == sacador:
                        mensagem = f"O sacador {sacador} conseguiu virar e venceu o game no jogo {jogo_id}. ✅"
                    else:
                        mensagem = f"O sacador {sacador} perdeu o game no jogo {jogo_id}. ❌"
                    enviar_alerta(mensagem)
                    estado_jogo['game_concluido'] = True
                    estado_jogo['vencedor_game'] = vencedor_game

        # Aguarda 1 segundo antes de verificar novamente
        time.sleep(1)

# Execução do monitoramento
if __name__ == "__main__":
    monitorar_jogos()