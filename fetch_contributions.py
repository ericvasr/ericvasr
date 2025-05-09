import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import json
import logging
import time
from tqdm import tqdm

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('git3d_fetcher')

# Carregar variáveis de ambiente de forma segura
try:
    from load_env import carregar_env
    carregar_env()
    logger.info("✅ Ambiente carregado com sucesso")
except ImportError:
    logger.warning("⚠️ Módulo load_env não encontrado, usando variáveis de ambiente existentes")

# Token do GitHub - obtido de forma segura
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    # Verificar se estamos em ambiente CI
    if os.getenv("CI") or os.getenv("GITHUB_ACTIONS"):
        logger.error("❌ Token do GitHub não encontrado nas variáveis de ambiente!")
        logger.error("   Por favor, configure o segredo GH_TOKEN nas configurações do GitHub Actions.")
        sys.exit(1)
    else:
        # Apenas solicitar entrada interativa se não estivermos em CI
        logger.warning("❌ Token do GitHub não encontrado!")
        logger.warning("Configure o token em um arquivo .env ou defina a variável de ambiente GITHUB_TOKEN")
        
        # Para ambientes interativos
        try:
            if sys.stdin.isatty():  # Verifica se é um terminal interativo
                token_input = input("Cole seu token do GitHub aqui: ").strip()
                if token_input:
                    GITHUB_TOKEN = token_input
                    # Salva no ambiente para uso futuro
                    os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
                    logger.info("✅ Token configurado com sucesso")
                else:
                    logger.error("❌ Token não fornecido. Saindo.")
                    sys.exit(1)
            else:
                logger.error("❌ Ambiente não-interativo e token não disponível. Saindo.")
                sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Erro ao obter token: {str(e)}")
            sys.exit(1)

USERNAME = "ericvasr"
logger.info(f"🔍 Buscando dados para o usuário: {USERNAME}")

# Definir período para busca (1 ano por padrão)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
start_date_str = start_date.strftime("%Y-%m-%dT00:00:00Z")

# Query GraphQL avançada para buscar mais dados
query = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    name
    login
    avatarUrl
    url
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            weekday
            color
          }
        }
      }
      commitContributionsByRepository(maxRepositories: 10) {
        repository {
          name
          nameWithOwner
          url
          stargazerCount
          forkCount
        }
        contributions {
          totalCount
        }
      }
      issueContributions(first: 100) {
        totalCount
        nodes {
          issue {
            title
            url
            repository {
              name
            }
            createdAt
          }
        }
      }
      pullRequestContributions(first: 100) {
        totalCount
        nodes {
          pullRequest {
            title
            url
            repository {
              name
            }
            createdAt
          }
        }
      }
    }
  }
}
"""

variables = {
    "username": USERNAME,
    "from": start_date_str,
    "to": end_date.strftime("%Y-%m-%dT23:59:59Z")
}

headers = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# Função para fazer requisição com retry
def request_with_retry(query, variables, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.post(
                'https://api.github.com/graphql',
                json={"query": query, "variables": variables},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                wait_time = int(response.headers.get('Retry-After', 60))
                logger.warning(f"⚠️ Rate limit atingido. Aguardando {wait_time} segundos...")
                time.sleep(wait_time)
                retries += 1
            else:
                logger.error(f"❌ Erro na requisição: {response.status_code}")
                logger.error(f"Resposta: {response.text}")
                retries += 1
                time.sleep(5)
        except Exception as e:
            logger.error(f"❌ Erro na requisição: {str(e)}")
            retries += 1
            time.sleep(5)
    
    logger.error("❌ Número máximo de tentativas excedido")
    return None

logger.info("🌐 Fazendo requisição à API do GitHub...")
data_json = request_with_retry(query, variables)

if not data_json:
    logger.error("❌ Falha ao obter dados. Saindo.")
    sys.exit(1)

try:
    # Extrair dados do usuário
    user_data = data_json['data']['user']
    contributions = user_data['contributionsCollection']
    weeks = contributions['contributionCalendar']['weeks']
    total_contributions = contributions['contributionCalendar']['totalContributions']
    
    # Extrair dados de contribuições por repositório
    repo_contributions = []
    for repo_contrib in contributions['commitContributionsByRepository']:
        repo_data = {
            'repository': repo_contrib['repository']['name'],
            'repository_full': repo_contrib['repository']['nameWithOwner'],
            'url': repo_contrib['repository']['url'],
            'stars': repo_contrib['repository']['stargazerCount'],
            'forks': repo_contrib['repository']['forkCount'],
            'commits': repo_contrib['contributions']['totalCount']
        }
        repo_contributions.append(repo_data)
    
    # Extrair dados de issues e PRs
    issue_count = contributions['issueContributions']['totalCount']
    pr_count = contributions['pullRequestContributions']['totalCount']
    
    logger.info(f"✅ Dados obtidos com sucesso: {total_contributions} contribuições, {issue_count} issues, {pr_count} PRs")
except KeyError as e:
    logger.error(f"❌ Erro ao extrair dados da resposta: {str(e)}")
    logger.error(f"Resposta: {json.dumps(data_json, indent=2)}")
    sys.exit(1)

# Transformar contribuições diárias em DataFrame
days = []
for week in tqdm(weeks, desc="Processando semanas"):
    for day in week['contributionDays']:
        days.append(day)

df = pd.DataFrame(days)
df['date'] = pd.to_datetime(df['date'])

# Adicionar transformações e colunas adicionais
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year
df['month_name'] = df['date'].dt.month_name()
df['day_name'] = df['date'].dt.day_name()
df['week_of_year'] = df['date'].dt.isocalendar().week

# Garantir que o diretório exista antes de salvar
os.makedirs(os.path.dirname('contrib_data.csv') or '.', exist_ok=True)

# Salvar dados em múltiplos formatos
df.to_csv("contrib_data.csv", index=False)
logger.info("✅ Dados de contribuições diárias salvos em contrib_data.csv")

# Salvar dados de repositórios
if repo_contributions:
    repo_df = pd.DataFrame(repo_contributions)
    repo_df.to_csv("repo_contributions.csv", index=False)
    logger.info(f"✅ Dados de {len(repo_contributions)} repositórios salvos em repo_contributions.csv")

# Salvar metadados gerais
metadata = {
    "username": USERNAME,
    "name": user_data.get('name'),
    "avatar_url": user_data.get('avatarUrl'),
    "profile_url": user_data.get('url'),
    "total_contributions": total_contributions,
    "issue_count": issue_count,
    "pr_count": pr_count,
    "date_range": {
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d")
    },
    "top_repositories": [r['repository'] for r in repo_contributions[:5]] if repo_contributions else [],
    "data_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

with open("github_user_data.json", "w") as f:
    json.dump(metadata, f, indent=2)
    logger.info("✅ Metadados do usuário salvos em github_user_data.json")

# Gerar estatísticas resumidas
stats = {
    "daily_average": df['contributionCount'].mean(),
    "weekday_totals": df.groupby('day_name')['contributionCount'].sum().to_dict(),
    "monthly_totals": df.groupby('month_name')['contributionCount'].sum().to_dict(),
    "streak_info": {
        "current_streak": 0,
        "max_streak": 0
    }
}

# Calcular sequências
streak = 0
current_streak = 0
sorted_df = df.sort_values('date')
for _, row in sorted_df.iterrows():
    if row['contributionCount'] > 0:
        current_streak += 1
    else:
        current_streak = 0
    streak = max(streak, current_streak)

# Verificar sequência atual
current_streak = 0
for i in range(len(sorted_df)-1, -1, -1):
    if sorted_df.iloc[i]['contributionCount'] > 0:
        current_streak += 1
    else:
        break

stats["streak_info"]["current_streak"] = current_streak
stats["streak_info"]["max_streak"] = streak

with open("contrib_stats.json", "w") as f:
    json.dump(stats, f, indent=2)
    logger.info("✅ Estatísticas calculadas e salvas em contrib_stats.json")

logger.info(f"🎉 Processo finalizado com sucesso! Coletados dados de {len(df)} dias.")
logger.info(f"📊 Total de contribuições: {total_contributions}")
logger.info(f"🚀 Sequência atual: {current_streak} dias | Sequência máxima: {streak} dias") 