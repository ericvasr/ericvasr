#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BeOnSafe - Sistema de Automação e Agentes Inteligentes
Desenvolvido por Eric Ribeiro para automação de processos e IA.
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Importa os módulos da BeOnSafe
from agent_core import (
    AgentImobiliario,
    AgentConcessionaria,
    AgentManager
)
from api_gateway import APIGateway
from github_profile import GithubProfile
from image_generator import ImagemAleatoria

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/beonsafe.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("beonsafe")

# Verifica se o diretório de logs existe
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("data/images", exist_ok=True)

def configurar_argumentos():
    """Configura os argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description="BeOnSafe - Sistema de Automação e Agentes Inteligentes"
    )
    
    # Adiciona os subcomandos
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")
    
    # Subcomando para executar os agentes
    parser_agente = subparsers.add_parser("agente", help="Gerenciar agentes")
    parser_agente.add_argument("tipo", choices=["imobiliaria", "concessionaria", "todos"], 
                               help="Tipo de agente a ser executado")
    parser_agente.add_argument("--async", action="store_true", dest="modo_async",
                               help="Executar agentes de forma assíncrona")
    
    # Subcomando para perfil GitHub
    parser_github = subparsers.add_parser("github", help="Gerenciar integração com GitHub")
    parser_github.add_argument("acao", choices=["perfil", "repos", "contrib"],
                               help="Ação a ser executada com GitHub")
    
    # Subcomando para geração de imagens
    parser_imagem = subparsers.add_parser("imagem", help="Gerador de imagens")
    parser_imagem.add_argument("tipo", choices=["avatar", "imovel", "veiculo", "todos"], 
                               help="Tipo de imagem a ser gerada")
    parser_imagem.add_argument("--qtd", type=int, default=1, 
                               help="Quantidade de imagens a serem geradas")
    parser_imagem.add_argument("--dir", type=str, default="data/images", 
                               help="Diretório para salvar as imagens")
    
    return parser.parse_args()

def executar_agentes(tipo, modo_async=False):
    """Executa os agentes de acordo com o tipo especificado"""
    logger.info(f"Iniciando agentes do tipo: {tipo} (modo assíncrono: {modo_async})")
    
    # Inicializa o gerenciador de API
    api = APIGateway()
    
    # Inicializa o gerenciador de agentes
    gerenciador = AgentManager(api_gateway=api)
    
    if tipo == "imobiliaria" or tipo == "todos":
        # Inicializa e registra os agentes imobiliários
        agente_imovel = AgentImobiliario(nome="Imobiliária BeOnSafe", api_gateway=api)
        gerenciador.registrar_agente(agente_imovel)
        logger.info(f"Agente imobiliário registrado: {agente_imovel.obter_nome()}")
    
    if tipo == "concessionaria" or tipo == "todos":
        # Inicializa e registra os agentes de concessionária
        agente_carro = AgentConcessionaria(nome="Concessionária BeOnSafe", api_gateway=api)
        gerenciador.registrar_agente(agente_carro)
        logger.info(f"Agente de concessionária registrado: {agente_carro.obter_nome()}")
    
    # Executa todos os agentes registrados
    if modo_async:
        gerenciador.executar_todos_async()
    else:
        gerenciador.executar_todos()
    
    return gerenciador.obter_resultados()

def executar_github(acao):
    """Executa operações relacionadas ao GitHub"""
    logger.info(f"Executando ação GitHub: {acao}")
    
    # Inicializa o gerenciador de perfil GitHub
    github = GithubProfile()
    
    if acao == "perfil":
        # Obtém e exibe informações do perfil
        perfil = github.obter_perfil()
        print("\n=== Perfil do GitHub ===")
        print(f"Nome: {perfil.get('name')}")
        print(f"Login: {perfil.get('login')}")
        print(f"Seguidores: {perfil.get('followers')}")
        print(f"Repositórios públicos: {perfil.get('public_repos')}")
        print(f"Bio: {perfil.get('bio')}")
        
    elif acao == "repos":
        # Lista os repositórios
        repos = github.listar_repositorios()
        print("\n=== Repositórios ===")
        for i, repo in enumerate(repos, 1):
            print(f"{i}. {repo.get('name')} - {repo.get('description')}")
            print(f"   ⭐ {repo.get('stargazers_count')} | 🍴 {repo.get('forks_count')}")
            print(f"   URL: {repo.get('html_url')}")
            print()
            
    elif acao == "contrib":
        # Exibe contribuições
        contrib = github.obter_contribuicoes()
        print("\n=== Contribuições ===")
        print(f"Total de contribuições no último ano: {contrib.get('total', 0)}")
        print(f"Média diária: {contrib.get('average_daily', 0):.2f}")
        print(f"Sequência atual: {contrib.get('current_streak', 0)} dias")
        print(f"Melhor sequência: {contrib.get('longest_streak', 0)} dias")
    
    return True

def executar_gerador_imagens(tipo, quantidade, diretorio):
    """Executa o gerador de imagens"""
    logger.info(f"Gerando {quantidade} imagens do tipo: {tipo}")
    
    # Inicializa o gerador de imagens
    gerador = ImagemAleatoria(diretorio_saida=diretorio)
    
    if tipo == "avatar" or tipo == "todos":
        # Gera avatares
        avatares = gerador.gerar_lote_avatares(quantidade=quantidade, prefixo_texto="Agente BeOnSafe")
        print(f"\n=== Avatares gerados: {len(avatares)} ===")
        for caminho in avatares:
            print(f"- {caminho}")
    
    if tipo == "imovel" or tipo == "todos":
        # Gera imagens de imóveis
        imoveis = gerador.gerar_lote_imoveis(quantidade=quantidade)
        print(f"\n=== Imagens de imóveis geradas: {len(imoveis)} ===")
        for caminho in imoveis:
            print(f"- {caminho}")
    
    if tipo == "veiculo" or tipo == "todos":
        # Gera imagens de veículos
        veiculos = gerador.gerar_lote_veiculos(quantidade=quantidade)
        print(f"\n=== Imagens de veículos geradas: {len(veiculos)} ===")
        for caminho in veiculos:
            print(f"- {caminho}")
    
    print(f"\nTodas as imagens foram salvas em: {diretorio}")
    return True

def main():
    """Função principal"""
    # Banner da aplicação
    print("\n" + "="*50)
    print("BeOnSafe - Sistema de Automação e Agentes Inteligentes")
    print("Desenvolvido por Eric Ribeiro")
    print("="*50 + "\n")
    
    # Configuração de argumentos de linha de comando
    args = configurar_argumentos()
    
    # Inicia o cronômetro
    inicio = datetime.now()
    
    # Executa a ação correspondente ao comando
    if args.comando == "agente":
        executar_agentes(args.tipo, args.modo_async)
    elif args.comando == "github":
        executar_github(args.acao)
    elif args.comando == "imagem":
        executar_gerador_imagens(args.tipo, args.qtd, args.dir)
    else:
        # Se nenhum comando for fornecido, mostra uma mensagem de ajuda
        print("Nenhum comando válido fornecido. Use -h para ajuda.")
        print("Exemplo de uso:")
        print("  python main.py agente imobiliaria")
        print("  python main.py github perfil")
        print("  python main.py imagem avatar --qtd 5")
    
    # Registra o tempo de execução
    tempo_execucao = (datetime.now() - inicio).total_seconds()
    logger.info(f"Execução concluída em {tempo_execucao:.2f} segundos")
    print(f"\nExecução concluída em {tempo_execucao:.2f} segundos")

if __name__ == "__main__":
    main() 