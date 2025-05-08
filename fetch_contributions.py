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
    print("❌ Token do GitHub não encontrado!")
    print("Configure o token em um arquivo .env ou defina a variável de ambiente GITHUB_TOKEN")
    sys.exit(1)

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

df.to_csv("contrib_data.csv", index=False)
print("✅ Dados salvos em contrib_data.csv") 