"""
Utilitário para carregar variáveis de ambiente de forma segura.
"""
import os
import sys

def carregar_env():
    """Carrega variáveis de ambiente do arquivo .env"""
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    if not os.path.exists(env_file):
        return False
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Processa linhas no formato export KEY=VALUE ou KEY=VALUE
            if line.startswith('export '):
                line = line[7:]  # Remove 'export '
                
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                # Remove aspas simples ou duplas do valor
                value = value.strip()
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                    
                os.environ[key] = value
    
    return True

if __name__ == "__main__":
    # Ação ao executar diretamente: verifica se o token está disponível
    carregar_env()
    if "GITHUB_TOKEN" in os.environ:
        print("✅ Token do GitHub encontrado!")
    else:
        print("❌ Token do GitHub não encontrado!")
        print("Configure o token em um arquivo .env ou defina a variável de ambiente GITHUB_TOKEN")
        sys.exit(1) 