import requests
import pandas as pd
from datetime import datetime
import os
import sys

# Carregar variáveis de ambiente de forma segura
try:
    from load_env import carregar_env
    carregar_env()
except ImportError:
    pass  # Se não encontrar o módulo, continua com as variáveis de ambiente já definidas

# Token do GitHub - obtido de forma segura
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    # Verificar se estamos em ambiente CI
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        print("❌ Token do GitHub não encontrado nas variáveis de ambiente!")
        print("   Por favor, configure o segredo GH_TOKEN nas configurações do GitHub Actions.")
        sys.exit(1)
    else:
        # Apenas solicitar entrada interativa se não estivermos em CI
        print("❌ Token do GitHub não encontrado!")
        print("Configure o token em um arquivo .env ou defina a variável de ambiente GITHUB_TOKEN")
        
        # Para ambientes interativos
        try:
            if sys.stdin.isatty():  # Verifica se é um terminal interativo
                token_input = input("Cole seu token do GitHub aqui: ").strip()
                if token_input:
                    GITHUB_TOKEN = token_input
                    # Salva no ambiente para uso futuro
                    os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
                else:
                    sys.exit(1)
            else:
                sys.exit(1)  # Sai silenciosamente em ambiente não-interativo sem terminal
        except:
            sys.exit(1)  # Sai em caso de qualquer erro na entrada

USERNAME = "ericvasr"

# Query GraphQL para buscar dados de contribuição
query = """
query {
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
          }
        }
      }
    }
  }
}
""" % USERNAME

headers = {
    "Authorization": f"bearer {GITHUB_TOKEN}"
}

response = requests.post(
    'https://api.github.com/graphql',
    json={"query": query},
    headers=headers
)

try:
    data = response.json()
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
except KeyError:
    print("❌ Erro ao obter dados do GitHub:")
    print(response.json())
    sys.exit(1)

# Transformar em DataFrame
days = []
for week in weeks:
    for day in week['contributionDays']:
        days.append(day)

df = pd.DataFrame(days)
df['date'] = pd.to_datetime(df['date'])

# Garantir que o diretório exista antes de salvar
os.makedirs(os.path.dirname('contrib_data.csv') or '.', exist_ok=True)

df.to_csv("contrib_data.csv", index=False)
print("✅ Dados salvos em contrib_data.csv") 