#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git3D Premium - Script de Execução Unificado
Visualização 3D Avançada de Contribuições do GitHub - BeOnSafe

Este script unifica todo o processo de geração de visualizações 3D premium,
executando os módulos de coleta de dados, visualização 3D e atualização do README.
"""

import os
import sys
import argparse
import logging
import time
import subprocess
from datetime import datetime
import colorama
from colorama import Fore, Style

# Inicializa colorama para mensagens coloridas
colorama.init(autoreset=True)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"git3d_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('git3d_runner')

def print_banner():
    """Exibe o banner do Git3D Premium"""
    banner = f"""
{Fore.BLUE}╔═══════════════════════════════════════════════════════════════╗
{Fore.BLUE}║{Fore.YELLOW} 🔷 Git3D Premium {Fore.WHITE}- Visualização 3D Premium de Contribuições{Fore.BLUE} ║
{Fore.BLUE}║{Fore.CYAN}    Powered by BeOnSafe - Visualizações de Alta Qualidade     {Fore.BLUE}║
{Fore.BLUE}╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def check_dependencies():
    """Verifica se todas as dependências necessárias estão instaladas"""
    try:
        import pandas
        import numpy
        import plotly
        import requests
        import tqdm
        
        # Verifica dependências opcionais
        kaleido_installed = False
        imageio_installed = False
        try:
            import kaleido
            kaleido_installed = True
        except ImportError:
            logger.warning(f"{Fore.YELLOW}⚠️ Kaleido não encontrado. Exportação de imagens pode ser limitada.")
        
        try:
            import imageio
            imageio_installed = True
        except ImportError:
            logger.warning(f"{Fore.YELLOW}⚠️ ImageIO não encontrado. Geração de GIFs não estará disponível.")
        
        return True, kaleido_installed, imageio_installed
    except ImportError as e:
        logger.error(f"{Fore.RED}❌ Dependência não encontrada: {str(e)}")
        logger.error(f"{Fore.RED}❌ Instale todas as dependências com: pip install -r requirements.txt")
        return False, False, False

def check_github_token():
    """Verifica se o token do GitHub está disponível"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.warning(f"{Fore.YELLOW}⚠️ Token do GitHub não encontrado nas variáveis de ambiente.")
        
        # Verificar no arquivo .env
        if os.path.exists(".env"):
            try:
                from dotenv import load_dotenv
                load_dotenv()
                token = os.getenv("GITHUB_TOKEN")
                if token:
                    logger.info(f"{Fore.GREEN}✅ Token carregado do arquivo .env")
                    return True
            except ImportError:
                logger.warning(f"{Fore.YELLOW}⚠️ python-dotenv não instalado. Não foi possível carregar .env")
        
        # Solicitar token interativamente
        if sys.stdin.isatty():  # Verificar se é ambiente interativo
            logger.info(f"{Fore.CYAN}🔑 Por favor, forneça seu token do GitHub:")
            token_input = input("> ").strip()
            if token_input:
                os.environ["GITHUB_TOKEN"] = token_input
                logger.info(f"{Fore.GREEN}✅ Token configurado temporariamente")
                
                # Perguntar se deseja salvar
                save_token = input(f"{Fore.CYAN}💾 Deseja salvar o token para uso futuro? (s/N): ").strip().lower()
                if save_token == 's':
                    try:
                        with open(".env", "a") as f:
                            f.write(f"\nGITHUB_TOKEN={token_input}\n")
                        logger.info(f"{Fore.GREEN}✅ Token salvo no arquivo .env")
                    except Exception as e:
                        logger.error(f"{Fore.RED}❌ Erro ao salvar token: {str(e)}")
                
                return True
            else:
                logger.error(f"{Fore.RED}❌ Token não fornecido")
                return False
        else:
            logger.error(f"{Fore.RED}❌ Token do GitHub não encontrado e ambiente não-interativo")
            return False
    
    return True

def run_module(script_name, description, timeout=300):
    """Executa um módulo do Git3D Premium com monitoramento de progresso"""
    logger.info(f"{Fore.CYAN}⏳ {description}...")
    
    # Verificar se o script existe
    if not os.path.exists(script_name):
        logger.error(f"{Fore.RED}❌ Script não encontrado: {script_name}")
        return False
    
    # Executar o script
    start_time = time.time()
    try:
        process = subprocess.Popen(
            [sys.executable, script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitorar saída em tempo real
        output = []
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if line:
                print(f"  {line}")
                output.append(line)
        
        # Aguardar conclusão com timeout
        process.wait(timeout=timeout)
        
        # Verificar código de saída
        if process.returncode != 0:
            logger.error(f"{Fore.RED}❌ Falha ao executar {script_name} (código {process.returncode})")
            return False
        
        # Sucesso
        elapsed_time = time.time() - start_time
        logger.info(f"{Fore.GREEN}✅ {description} concluído em {elapsed_time:.2f}s")
        return True
    
    except subprocess.TimeoutExpired:
        process.kill()
        logger.error(f"{Fore.RED}❌ Timeout ao executar {script_name} (> {timeout}s)")
        return False
    except Exception as e:
        logger.error(f"{Fore.RED}❌ Erro ao executar {script_name}: {str(e)}")
        return False

def main():
    """Função principal"""
    # Análise de argumentos
    parser = argparse.ArgumentParser(description="Git3D Premium - Visualização 3D Avançada de Contribuições")
    parser.add_argument("-u", "--usuario", help="Nome de usuário do GitHub", default="ericvasr")
    parser.add_argument("--sem-readme", action="store_true", help="Não atualizar o README")
    parser.add_argument("--apenas-dados", action="store_true", help="Apenas coletar dados, sem gerar visualizações")
    parser.add_argument("--verbose", action="store_true", help="Exibir mensagens detalhadas")
    
    args = parser.parse_args()
    
    # Configurar nível de logging
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Exibir banner
    print_banner()
    
    # Verificar dependências
    logger.info(f"{Fore.CYAN}🔍 Verificando ambiente e dependências...")
    deps_ok, kaleido_ok, imageio_ok = check_dependencies()
    if not deps_ok:
        return 1
    
    # Verificar token
    if not check_github_token():
        return 1
    
    # Atualizar USERNAME nos scripts se fornecido
    if args.usuario and args.usuario != "ericvasr":
        logger.info(f"{Fore.CYAN}👤 Configurando para usuário: {args.usuario}")
        try:
            files_to_update = ["fetch_contributions.py", "generate_advanced_3d.py"]
            for file in files_to_update:
                if os.path.exists(file):
                    with open(file, "r") as f:
                        content = f.read()
                    
                    content = content.replace('USERNAME = "ericvasr"', f'USERNAME = "{args.usuario}"')
                    
                    with open(file, "w") as f:
                        f.write(content)
            logger.info(f"{Fore.GREEN}✅ Scripts configurados para o usuário: {args.usuario}")
        except Exception as e:
            logger.error(f"{Fore.RED}❌ Erro ao configurar scripts para usuário: {str(e)}")
            return 1
    
    # Etapa 1: Coleta de dados
    if not run_module("fetch_contributions.py", "Coletando dados de contribuições"):
        return 1
    
    # Verificar se deseja apenas coletar dados
    if args.apenas_dados:
        logger.info(f"{Fore.GREEN}✅ Coleta de dados concluída. Encerrando conforme solicitado.")
        return 0
    
    # Etapa 2: Gerar visualização 3D
    if not run_module("generate_advanced_3d.py", "Gerando visualização 3D premium"):
        return 1
    
    # Etapa 3: Atualizar README
    if not args.sem_readme:
        if not run_module("update_readme.py", "Atualizando README com visualização premium"):
            return 1
    
    # Conclusão
    logger.info(f"{Fore.GREEN}🎉 Processo concluído com sucesso!")
    logger.info(f"{Fore.CYAN}📊 Arquivos gerados:")
    
    output_files = [
        "images/github_3d_beonsafe.html",
        "images/github_3d_beonsafe.png",
        "images/github_3d_beonsafe.gif",
        "images/github_3d_beonsafe_animated.html",
        "README.md"
    ]
    
    for file in output_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            if size > 1024:
                logger.info(f"{Fore.GREEN}  ✅ {file} ({size/1024:.1f} MB)")
            else:
                logger.info(f"{Fore.GREEN}  ✅ {file} ({size:.1f} KB)")
    
    logger.info(f"{Fore.YELLOW}⭐ Para personalização avançada, consulte README_GIT3D.md")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.error(f"{Fore.RED}❌ Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"{Fore.RED}❌ Erro não tratado: {str(e)}")
        sys.exit(1) 