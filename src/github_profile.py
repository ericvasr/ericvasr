#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilitário para gerenciar perfil do GitHub
BeOnSafe - Eric Ribeiro
"""

import os
import requests
import json
import logging
from dotenv import load_dotenv

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/github.log")
    ]
)

logger = logging.getLogger("github_profile")

# Carrega variáveis de ambiente
load_dotenv()

class GitHubProfile:
    """Classe para gerenciar perfil do GitHub"""
    
    def __init__(self):
        self.username = os.getenv("GITHUB_USERNAME", "ericvasr")
        # Tenta obter o token da variável GH_TOKEN (formato preferido dos GitHub Actions)
        self.token = os.getenv("GH_TOKEN")
        if not self.token:
            # Fallback para outras variáveis possíveis
            self.token = os.getenv("GITHUB_TOKEN")
        
        self.base_url = "https://api.github.com"
        
        logger.info(f"GitHubProfile inicializado para o usuário: {self.username}")
        if self.token:
            logger.info("Token do GitHub encontrado.")
        else:
            logger.warning("Token do GitHub não encontrado. Algumas funcionalidades podem ser limitadas.")
        
    def get_user_info(self):
        """Obtém informações do usuário do GitHub"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
            
        response = requests.get(
            f"{self.base_url}/users/{self.username}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter informações: {response.status_code}")
            return None
            
    def get_repositories(self, limit=10):
        """Obtém repositórios do usuário"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
            
        response = requests.get(
            f"{self.base_url}/users/{self.username}/repos?sort=updated&per_page={limit}",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Erro ao obter repositórios: {response.status_code}")
            return []
    
    def print_profile_summary(self):
        """Imprime resumo do perfil"""
        info = self.get_user_info()
        repos = self.get_repositories(5)
        
        if not info:
            print("Não foi possível obter informações do perfil")
            return
            
        print("\n=== Perfil do GitHub ===")
        print(f"Nome: {info.get('name', 'Eric Ribeiro')}")
        print(f"Login: {info.get('login')}")
        print(f"Bio: {info.get('bio', 'Fundador da BeOnSafe - Especialista em IA e Automação')}")
        print(f"Seguidores: {info.get('followers')}")
        print(f"Seguindo: {info.get('following')}")
        print(f"Repositórios públicos: {info.get('public_repos')}")
        
        if repos:
            print("\n=== Repositórios Recentes ===")
            for repo in repos:
                print(f"- {repo['name']}: {repo['description'] or 'Sem descrição'}")
        
        print("\n=== BeOnSafe ===")
        print("Desenvolvendo agentes de IA e soluções para imobiliárias e concessionárias.")
        print("https://github.com/ericvasr")

def main():
    """Função principal"""
    # Cria pasta de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Inicializa perfil
    profile = GitHubProfile()
    profile.print_profile_summary()

if __name__ == "__main__":
    main() 