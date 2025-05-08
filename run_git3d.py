#!/usr/bin/env python3
"""
🔷 Git3D - BeOnSafe
Visualização 3D de contribuições do GitHub para seu perfil.

Este script automatiza todo o processo:
1. Obtenção dos dados via API GraphQL do GitHub
2. Processamento dos dados
3. Geração de visualizações 3D avançadas
4. Atualização do README.md

Requisitos:
- Python 3.6+
- Token de acesso pessoal do GitHub com as permissões corretas
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import traceback

# Carregar variáveis de ambiente
try:
    from load_env import carregar_env
    env_carregado = carregar_env()
except ImportError:
    env_carregado = False

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import requests
        import pandas
        import numpy
        import plotly
        import re
        
        # Verifica se temos os pacotes opcionais para GIF
        try:
            import kaleido
            import imageio
            tem_gif = True
        except ImportError:
            tem_gif = False
            print("⚠️ Pacotes para geração de GIF não encontrados (kaleido, imageio)")
            print("   Para habilitar a geração de GIFs, instale: pip install kaleido imageio")
        
        return True, tem_gif
    except ImportError as e:
        print(f"❌ Dependência faltando: {str(e)}")
        print("   Instale as dependências com: pip install requests pandas numpy plotly")
        return False, False

def obter_token_github():
    """Obtém o token do GitHub"""
    # Primeiro checa se existe no ambiente
    token = os.getenv("GITHUB_TOKEN")
    
    # Se não existir, solicita
    if not token:
        print("\n🔑 Token do GitHub necessário para acessar a API")
        print("   Acesse: https://github.com/settings/tokens")
        print("   Crie um token com as permissões: repo, read:user, user:email, read:org, etc.")
        token = input("   Cole seu token aqui: ").strip()
        
        # Opção para salvar no ambiente para futuros usos
        salvar = input("   Deseja salvar este token para usos futuros? (s/n): ").strip().lower()
        if salvar == 's':
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'), "w") as f:
                f.write(f"GITHUB_TOKEN='{token}'")
            os.chmod(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'), 0o600)  # Permissões restritas
            print("   Token salvo com segurança no arquivo .env")
            print("   ⚠️ ATENÇÃO: Nunca compartilhe este arquivo ou adicione ao controle de versão")
    
    return token

def obter_usuario_github():
    """Obtém o nome de usuário do GitHub"""
    # Verifica se foi passado como argumento
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    # Caso contrário, solicita
    username = input("\n👤 Digite seu nome de usuário do GitHub: ").strip()
    return username

def executar_etapa(descricao, funcao, *args, **kwargs):
    """Executa uma etapa do processo com formatação"""
    print(f"\n{'='*80}")
    print(f"🔷 {descricao}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        resultado = funcao(*args, **kwargs)
        elapsed = time.time() - start_time
        print(f"✅ Concluído em {elapsed:.2f} segundos")
        return resultado
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        print(traceback.format_exc())
        return None

def executar_script(script_path, msg="Executando script"):
    """Executa um script Python"""
    print(f"\n▶️ {msg}...")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Erro ao executar {script_path}")
        print(result.stderr)
        return False
    
    print(result.stdout)
    return True

def salvar_token_variavel(token):
    """Salva o token em uma variável de ambiente temporária"""
    os.environ["GITHUB_TOKEN"] = token

def main():
    """Função principal"""
    # Mostrar banner
    print("""
    ╔═════════════════════════════════════════════════════╗
    ║                                                     ║
    ║  🔷 Git3D - BeOnSafe                               ║
    ║  Visualização 3D de Contribuições do GitHub         ║
    ║                                                     ║
    ╚═════════════════════════════════════════════════════╝
    """)
    
    print("📅 Iniciado em:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    # Verificar dependências
    deps_ok, tem_gif = executar_etapa("Verificando dependências", verificar_dependencias)
    if not deps_ok:
        return

    # Obter credenciais e configurações
    if not os.getenv("GITHUB_TOKEN"):
        token = executar_etapa("Obtendo token do GitHub", obter_token_github)
        if not token:
            return
        # Salvar token em variável de ambiente temporária
        salvar_token_variavel(token)
    else:
        print("✅ Token do GitHub encontrado nas variáveis de ambiente")
    
    username = executar_etapa("Obtendo nome de usuário", obter_usuario_github)
    if not username:
        return
    
    # Modificar os scripts para usar o nome de usuário correto
    with open("fetch_contributions.py", "r") as f:
        conteudo = f.read()
    
    conteudo_modificado = conteudo.replace('USERNAME = "ericvasr"', f'USERNAME = "{username}"')
    
    with open("fetch_contributions.py", "w") as f:
        f.write(conteudo_modificado)
    
    # Executar as etapas em sequência
    executar_script("fetch_contributions.py", "Buscando dados de contribuições")
    
    # Se não encontrou os dados, encerra
    if not os.path.exists("contrib_data.csv"):
        print("❌ Erro: Dados de contribuições não foram gerados")
        return
    
    # Modificar scripts de visualização para usar o nome de usuário correto
    for script in ["visualize_3d.py", "generate_advanced_3d.py"]:
        with open(script, "r") as f:
            conteudo = f.read()
        
        conteudo_modificado = conteudo.replace('USERNAME = "ericvasr"', f'USERNAME = "{username}"')
        
        with open(script, "w") as f:
            f.write(conteudo_modificado)
    
    # Gerar visualizações
    if tem_gif:
        executar_script("generate_advanced_3d.py", "Gerando visualização 3D avançada com GIF")
    else:
        executar_script("visualize_3d.py", "Gerando visualização 3D básica")
    
    # Atualizar o README
    executar_script("update_readme.py", "Atualizando README.md")
    
    print("\n🎉 Processo concluído com sucesso!")
    print("📊 Arquivos gerados:")
    
    # Listar arquivos gerados
    if os.path.exists("images"):
        for arquivo in os.listdir("images"):
            if arquivo.endswith((".html", ".png", ".gif")):
                print(f"   - images/{arquivo}")
    
    print("\n🔷 Obrigado por usar Git3D - BeOnSafe")
    print("📬 Contato: eric@beonsafe.com.br")

if __name__ == "__main__":
    main() 