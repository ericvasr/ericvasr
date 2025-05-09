import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import json
import logging
import time
from tqdm import tqdm
import hashlib

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('git3d_fetcher')

# Carregar variáveis de ambiente de forma segura
try:
    from load_env import carregar_env, load_from_cache, save_to_cache
    if carregar_env():
        logger.info("✅ Ambiente carregado com sucesso")
    else:
        logger.warning("⚠️ Problemas ao carregar o ambiente")
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

# Criar uma chave de cache baseada no usuário e período
def create_cache_key(username, start_date, end_date):
    key_string = f"{username}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    return f"github_data_{hashlib.md5(key_string.encode()).hexdigest()}"

cache_key = create_cache_key(USERNAME, start_date, end_date)

# Verificar se temos dados em cache
cached_data = load_from_cache(cache_key)
if cached_data:
    logger.info("🔄 Usando dados em cache")
    data_json = cached_data
    
    # Extrair e processar dados em cache
    try:
        # Verifica se o arquivo de dados CSV já existe
        if os.path.exists('contrib_data.csv') and os.path.exists('github_user_data.json'):
            logger.info("✅ Arquivos de dados encontrados, pulando processamento")
            sys.exit(0)
    except Exception:
        # Se houver erro, continua para o processamento normal
        pass
else:
    logger.info("🌐 Cache não encontrado, buscando dados frescos da API")

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
    
    # Salvar em cache para uso futuro
    save_to_cache(cache_key, data_json)
    logger.info("💾 Dados salvos em cache para uso futuro")

try:
    # Extrair dados do usuário
    user_data = data_json['data']['user']
    contributions = user_data['contributionsCollection']
    weeks = contributions['contributionCalendar']['weeks']
    total_contributions = contributions['contributionCalendar']['totalContributions']
    
    # Aplicar validações de segurança aos dados
    def sanitize_data(data):
        """Sanitiza dados para evitar problemas de segurança"""
        if isinstance(data, dict):
            return {k: sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [sanitize_data(i) for i in data]
        elif isinstance(data, str):
            # Remover caracteres potencialmente perigosos
            return data.replace('<', '&lt;').replace('>', '&gt;')
        else:
            return data
    
    # Sanitizar dados do usuário
    user_data = sanitize_data(user_data)
    
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
    issues_count = contributions['issueContributions']['totalCount']
    pr_count = contributions['pullRequestContributions']['totalCount']
    
    # Obter lista de dias com contribuições
    contribution_days = []
    for week in weeks:
        for day in week['contributionDays']:
            date = day['date']
            contrib_count = day['contributionCount']
            weekday = day['weekday']
            color = day['color']
            
            contribution_days.append({
                'date': date,
                'contributionCount': contrib_count,
                'weekday': weekday,
                'color': color
            })
    
    # Converter para DataFrame para análise
    df = pd.DataFrame(contribution_days)
    
    # Analisar padrões de contribuição
    active_days = (df['contributionCount'] > 0).sum()
    inactive_days = len(df) - active_days
    
    # Calcular sequência atual
    current_streak = 0
    
    # Ordenar por data antes de calcular a sequência
    df = df.sort_values('date', ascending=False)
    
    for _, row in df.iterrows():
        if row['contributionCount'] > 0:
            current_streak += 1
        else:
            break
    
    # Calcular sequência máxima
    df = df.sort_values('date')
    max_streak = 0
    streak = 0
    
    for _, row in df.iterrows():
        if row['contributionCount'] > 0:
            streak += 1
        else:
            max_streak = max(max_streak, streak)
            streak = 0
    
    max_streak = max(max_streak, streak)  # Verificar última sequência

    # Preparar dados para salvamento
    user_stats = {
        'username': USERNAME,
        'name': user_data['name'],
        'total_contributions': total_contributions,
        'active_days': int(active_days),
        'inactive_days': int(inactive_days),
        'activity_rate': float(active_days) / len(df) * 100,
        'current_streak': current_streak,
        'max_streak': max_streak,
        'issues_count': issues_count,
        'pr_count': pr_count,
        'repositories': repo_contributions,
        'period_start': start_date.strftime('%Y-%m-%d'),
        'period_end': end_date.strftime('%Y-%m-%d'),
        'data_fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'avatar_url': user_data['avatarUrl']
    }
    
    # Salvar dados em CSV
    logger.info("💾 Salvando dados processados...")
    df.to_csv('contrib_data.csv', index=False)
    
    # Salvar estatísticas do usuário
    with open('github_user_data.json', 'w') as f:
        json.dump(user_stats, f, indent=2)
    
    # Resumo
    logger.info(f"✅ Processamento concluído para {USERNAME}")
    logger.info(f"📊 Total de contribuições: {total_contributions}")
    logger.info(f"📅 Período: {start_date.strftime('%Y-%m-%d')} a {end_date.strftime('%Y-%m-%d')}")
    logger.info(f"🔥 Sequência atual: {current_streak} dias")
    logger.info(f"🏆 Sequência máxima: {max_streak} dias")
    
except Exception as e:
    logger.error(f"❌ Erro ao processar dados: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1) 