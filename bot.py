import os
import requests
import time
import datetime

# Configurações iniciais
API_URL = "https://api.exemplo.com/tennis/live"  # Substitua pela URL real da API de jogos ao vivo
INTERVALO_VERIFICACAO = 300  # Intervalo de 5 minutos (300 segundos)

# Função para obter dados dos jogos ao vivo
def obter_jogos_ao_vivo():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()  # Supondo que a API retorne JSON
        else:
            print(f"Erro ao obter jogos: {response.status_code}")
            return []
    except Exception as e:
        print(f"Exceção ao obter jogos: {e}")
        return []

# Função para exibir os jogos ao vivo
def exibir_jogos_ao_vivo(jogos):
    if jogos:
        print(f"\n{datetime.datetime.now()}: Jogos ao vivo no momento:")
        for jogo in jogos:
            jogador1 = jogo['jogador1']
            jogador2 = jogo['jogador2']
            placar = jogo['placar']  # Ajuste conforme a estrutura real dos dados
            print(f"{jogador1} vs {jogador2} - Placar: {placar}")
    else:
        print(f"\n{datetime.datetime.now()}: Nenhum jogo ao vivo no momento.")

# Função principal de monitoramento
def monitorar_jogos():
    while True:
        jogos_ao_vivo = obter_jogos_ao_vivo()
        exibir_jogos_ao_vivo(jogos_ao_vivo)
        time.sleep(INTERVALO_VERIFICACAO)

# Execução do monitoramento
if __name__ == "__main__":
    monitorar_jogos()