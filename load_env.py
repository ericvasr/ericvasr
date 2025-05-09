"""
Utilitário para carregar variáveis de ambiente de forma segura.
"""
import os
import sys
import logging
from datetime import datetime
import json

# Configuração de logging
logger = logging.getLogger('git3d_config')

def carregar_env():
    """Carrega variáveis de ambiente de arquivo .env e valida configurações essenciais"""
    try:
        # Verifica se o arquivo .env existe
        if os.path.exists('.env'):
            logger.info("🔑 Carregando variáveis de ambiente do arquivo .env")
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        # Configurações de cache
        if 'GIT3D_CACHE_ENABLED' not in os.environ:
            os.environ['GIT3D_CACHE_ENABLED'] = 'true'
        
        if 'GIT3D_CACHE_DURATION' not in os.environ:
            os.environ['GIT3D_CACHE_DURATION'] = '86400'  # 24 horas em segundos
        
        # Valida token do GitHub
        validate_github_token()
        
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao carregar variáveis de ambiente: {str(e)}")
        return False

def validate_github_token():
    """Valida se o token do GitHub está configurado e parece válido"""
    token = os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
    
    if not token:
        logger.warning("⚠️ Token do GitHub não encontrado nas variáveis de ambiente")
        return False
    
    # Validação básica do formato do token
    if not (len(token) >= 40 and not token.startswith('ghp_') and not token.startswith('github_pat_')):
        logger.warning("⚠️ O token do GitHub parece estar em um formato inválido")
    
    return True

def save_to_cache(cache_key, data, expiry_seconds=None):
    """Salva dados em cache com expiração configurável"""
    if os.getenv('GIT3D_CACHE_ENABLED', 'true').lower() != 'true':
        return False
    
    if expiry_seconds is None:
        expiry_seconds = int(os.getenv('GIT3D_CACHE_DURATION', '86400'))
    
    cache_dir = os.path.join(os.getcwd(), '.cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    cache_data = {
        'data': data,
        'expires_at': (datetime.now().timestamp() + expiry_seconds)
    }
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao salvar cache: {str(e)}")
        return False

def load_from_cache(cache_key):
    """Carrega dados do cache se ainda forem válidos"""
    if os.getenv('GIT3D_CACHE_ENABLED', 'true').lower() != 'true':
        return None
    
    cache_dir = os.path.join(os.getcwd(), '.cache')
    cache_file = os.path.join(cache_dir, f"{cache_key}.json")
    
    if not os.path.exists(cache_file):
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Verifica se o cache expirou
        if datetime.now().timestamp() > cache_data.get('expires_at', 0):
            logger.info(f"🕒 Cache expirado para {cache_key}")
            return None
        
        logger.info(f"✅ Dados carregados do cache para {cache_key}")
        return cache_data.get('data')
    except Exception as e:
        logger.error(f"❌ Erro ao carregar cache: {str(e)}")
        return None

def clear_cache(cache_key=None):
    """Limpa um item específico do cache ou todo o cache"""
    cache_dir = os.path.join(os.getcwd(), '.cache')
    
    if not os.path.exists(cache_dir):
        return True
    
    try:
        if cache_key:
            cache_file = os.path.join(cache_dir, f"{cache_key}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
                logger.info(f"🧹 Cache limpo para {cache_key}")
        else:
            # Limpar todo o cache
            for file in os.listdir(cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(cache_dir, file))
            logger.info("🧹 Cache completamente limpo")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao limpar cache: {str(e)}")
        return False

if __name__ == "__main__":
    # Ação ao executar diretamente: verifica se o token está disponível
    carregar_env()
    if "GITHUB_TOKEN" in os.environ:
        print("✅ Token do GitHub encontrado!")
    else:
        print("❌ Token do GitHub não encontrado!")
        print("Configure o token em um arquivo .env ou defina a variável de ambiente GITHUB_TOKEN")
        sys.exit(1) 