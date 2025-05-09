#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git3D Premium - Script de Execução Unificado
Executa todo o processo de geração de visualização 3D de contribuições do GitHub

Uso:
  python run_git3d.py --full         # Executa o processo completo com todas as etapas
  python run_git3d.py --fetch        # Apenas obtém os dados de contribuições
  python run_git3d.py --visualize    # Apenas gera a visualização 3D
  python run_git3d.py --update       # Apenas atualiza o README
  python run_git3d.py --security     # Executa verificação de segurança
  python run_git3d.py --config       # Configura preferências
  python run_git3d.py --clean-cache  # Limpa o cache

Autor: Eric Vasconcellos (BeOnSafe)
Versão: 1.2.0
"""

import os
import sys
import argparse
import logging
import time
import subprocess
from datetime import datetime, timedelta

# Configurar logging
logs_dir = 'logs'
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(logs_dir, f'git3d_run_{datetime.now().strftime("%Y%m%d")}.log'), mode='a')
    ]
)
logger = logging.getLogger('git3d_runner')

# Tentar importar configurações
try:
    from config import USERNAME, COMPANY_NAME, ACTIVE_THEME
    config_available = True
except ImportError:
    logger.warning("⚠️ Módulo de configuração não encontrado, usando valores padrão")
    USERNAME = "ericvasr"
    COMPANY_NAME = "BeOnSafe"
    ACTIVE_THEME = "tech_noir"
    config_available = False

def execute_command(cmd, description, allow_failure=False):
    """Executa um comando no shell com formatação e tratamento de erros"""
    logger.info(f"🔄 {description}")
    
    cmd_str = cmd if isinstance(cmd, str) else " ".join(cmd)
    logger.info(f"🔷 Comando: {cmd_str}")
    
    print(f"\n{'='*80}")
    print(f" 🔷 {description} ".center(80, "="))
    print(f"{'='*80}")
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, check=not allow_failure)
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            logger.info(f"✅ Comando concluído com sucesso em {elapsed:.2f}s")
            print(f"\n✅ Concluído com sucesso em {elapsed:.2f}s!")
            return True
        else:
            logger.error(f"❌ Comando falhou com código {result.returncode} em {elapsed:.2f}s")
            print(f"\n❌ Falha: código de saída {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"💥 Erro ao executar comando: {str(e)}")
        print(f"\n💥 Erro: {str(e)}")
        return False

def verify_dependencies():
    """Verifica se todas as dependências necessárias estão instaladas"""
    logger.info("🔍 Verificando dependências")
    
    try:
        import pandas, numpy, plotly, requests, tqdm, matplotlib
        logger.info("✅ Dependências básicas verificadas")
        
        try:
            import imageio, kaleido
            logger.info("✅ Dependências para geração de imagens verificadas")
        except ImportError:
            logger.warning("⚠️ Algumas dependências para geração de imagens estão faltando")
            if input("📦 Deseja instalar as dependências faltantes? (s/n): ").lower() in ['s', 'sim', 'y', 'yes']:
                execute_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              "Instalando dependências")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Dependência faltante: {str(e)}")
        print(f"\n❌ Algumas dependências estão faltando. Execute: pip install -r requirements.txt")
        
        if input("📦 Deseja instalar as dependências agora? (s/n): ").lower() in ['s', 'sim', 'y', 'yes']:
            execute_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          "Instalando dependências")
            return True
        return False

def fetch_contributions():
    """Obtém os dados de contribuições do GitHub"""
    return execute_command([sys.executable, "fetch_contributions.py"], 
                        "Obtendo dados de contribuições do GitHub")

def generate_visualization():
    """Gera a visualização 3D das contribuições"""
    return execute_command([sys.executable, "generate_advanced_3d.py"], 
                        "Gerando visualização 3D premium")

def update_readme():
    """Atualiza o README com a nova visualização"""
    return execute_command([sys.executable, "update_readme.py"], 
                        "Atualizando README com visualização 3D")

def run_security_check():
    """Executa verificação de segurança"""
    return execute_command([sys.executable, "security_check.py"], 
                        "Verificando segurança do projeto", 
                        allow_failure=True)

def configure_settings():
    """Configura preferências do sistema"""
    return execute_command([sys.executable, "config.py"], 
                        "Configurando preferências do sistema",
                        allow_failure=True)

def clean_cache():
    """Limpa o cache do sistema"""
    return execute_command([sys.executable, "manage_cache.py", "clear", "--all"], 
                        "Limpando cache do sistema",
                        allow_failure=True)

def view_cache():
    """Visualiza o estado atual do cache"""
    return execute_command([sys.executable, "manage_cache.py", "list"], 
                        "Visualizando estado atual do cache",
                        allow_failure=True)

def run_tests():
    """Executa testes unitários"""
    return execute_command([sys.executable, "test_git3d.py"], 
                        "Executando testes unitários",
                        allow_failure=True)

def run_full_process():
    """Executa o processo completo de geração e atualização"""
    logger.info("🚀 Iniciando processo completo do Git3D Premium")
    
    # Verificar dependências primeiro
    if not verify_dependencies():
        logger.error("❌ Verificação de dependências falhou. Abortando.")
        return False
    
    # Limpar cache expirado para não usar dados antigos
    execute_command([sys.executable, "manage_cache.py", "clear", "--expired"], 
                  "Limpando cache expirado",
                  allow_failure=True)
    
    # Sequência principal
    success = fetch_contributions()
    if not success:
        logger.error("❌ Falha ao obter dados de contribuições. Abortando.")
        return False
    
    success = generate_visualization()
    if not success:
        logger.error("❌ Falha ao gerar visualização 3D. Abortando.")
        return False
    
    success = update_readme()
    if not success:
        logger.warning("⚠️ Falha ao atualizar README, mas visualizações foram geradas.")
    
    # Verificação de segurança opcional
    run_security_check()
    
    logger.info("✅ Processo completo concluído com sucesso!")
    return True

def create_welcome_message():
    """Cria uma mensagem de boas-vindas para o console"""
    terminal_width = 80
    
    message = [
        "",
        "🔷" * (terminal_width // 2),
        f"{'GIT3D PREMIUM - VISUALIZAÇÃO 3D DE CONTRIBUIÇÕES GITHUB'.center(terminal_width)}",
        f"{'Powered by BeOnSafe'.center(terminal_width)}",
        f"{'Versão 1.2.0'.center(terminal_width)}",
        "🔷" * (terminal_width // 2),
        "",
        f"👤 Usuário: {USERNAME}",
        f"🏢 Empresa: {COMPANY_NAME}",
        f"🎨 Tema: {ACTIVE_THEME}",
        ""
    ]
    
    return "\n".join(message)

def parse_arguments():
    """Analisa argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description='Git3D Premium - Visualização 3D de Contribuições do GitHub',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--full', action='store_true', help='Executa o processo completo')
    group.add_argument('--fetch', action='store_true', help='Apenas obtém dados de contribuições')
    group.add_argument('--visualize', action='store_true', help='Apenas gera visualização 3D')
    group.add_argument('--update', action='store_true', help='Apenas atualiza o README')
    group.add_argument('--security', action='store_true', help='Executa verificação de segurança')
    group.add_argument('--config', action='store_true', help='Configura preferências')
    group.add_argument('--clean-cache', action='store_true', help='Limpa o cache')
    group.add_argument('--view-cache', action='store_true', help='Visualiza o estado do cache')
    group.add_argument('--test', action='store_true', help='Executa testes unitários')
    
    return parser.parse_args()

def main():
    """Função principal"""
    print(create_welcome_message())
    
    args = parse_arguments()
    
    if args.fetch:
        fetch_contributions()
    elif args.visualize:
        generate_visualization()
    elif args.update:
        update_readme()
    elif args.security:
        run_security_check()
    elif args.config:
        configure_settings()
    elif args.clean_cache:
        clean_cache()
    elif args.view_cache:
        view_cache()
    elif args.test:
        run_tests()
    else:
        # Padrão é executar o processo completo
        run_full_process()
    
    print("\n🔷 Finalizado! 🔷\n")

if __name__ == "__main__":
    main() 