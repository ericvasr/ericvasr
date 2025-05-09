#!/usr/bin/env python3
"""
Git3D Premium - Script de Testes
Ferramenta para testar as funcionalidades do sistema
"""

import os
import sys
import unittest
import logging
import json
import tempfile
import shutil
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('git3d_tests')

# Tentar importar módulos necessários
try:
    from load_env import carregar_env, save_to_cache, load_from_cache, clear_cache
    from config import get_active_theme, THEMES
    cache_available = True
except ImportError as e:
    logger.warning(f"⚠️ Módulo não encontrado: {str(e)}")
    cache_available = False

class Git3dPremiumTests(unittest.TestCase):
    """Classe para testes unitários do Git3D Premium"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar diretório temporário para testes
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        
        # Copiar arquivos necessários para teste
        needed_files = ['load_env.py', 'config.py', 'fetch_contributions.py', 
                       'generate_advanced_3d.py', 'update_readme.py']
        
        for file in needed_files:
            if os.path.exists(file):
                dest_file = os.path.join(self.test_dir, file)
                shutil.copy2(file, dest_file)
        
        # Mover para o diretório de testes
        os.chdir(self.test_dir)
        
        # Criar arquivo .env de teste
        with open('.env', 'w') as f:
            f.write('GITHUB_TOKEN=ghp_test_token_not_real\n')
            f.write('GIT3D_CACHE_ENABLED=true\n')
            f.write('GIT3D_CACHE_DURATION=3600\n')
    
    def tearDown(self):
        """Limpeza após os testes"""
        # Voltar ao diretório original
        os.chdir(self.original_dir)
        
        # Remover diretório temporário
        shutil.rmtree(self.test_dir)
    
    def test_cache_system(self):
        """Testa o sistema de cache"""
        if not cache_available:
            self.skipTest("Sistema de cache não disponível")
        
        # Carregar ambiente
        self.assertTrue(carregar_env(), "Carregar ambiente deve retornar True")
        
        # Testar salvar em cache
        test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
        self.assertTrue(save_to_cache("test_key", test_data), "Salvar em cache deve retornar True")
        
        # Testar carregar de cache
        loaded_data = load_from_cache("test_key")
        self.assertIsNotNone(loaded_data, "Dados carregados não devem ser None")
        self.assertEqual(loaded_data["test"], "data", "Dados carregados devem corresponder aos salvos")
        
        # Testar limpar cache
        self.assertTrue(clear_cache("test_key"), "Limpar cache deve retornar True")
        
        # Verificar se cache foi realmente limpo
        self.assertIsNone(load_from_cache("test_key"), "Após limpar, carregar deve retornar None")
    
    def test_theme_system(self):
        """Testa o sistema de temas"""
        try:
            from config import get_active_theme, THEMES
            
            # Verificar se temas existem
            self.assertIsNotNone(THEMES, "THEMES não deve ser None")
            self.assertGreater(len(THEMES), 0, "Deve haver pelo menos um tema")
            
            # Verificar tema ativo
            active_theme = get_active_theme()
            self.assertIsNotNone(active_theme, "Tema ativo não deve ser None")
            self.assertIn("colors", active_theme, "Tema deve ter cores")
            self.assertIn("name", active_theme, "Tema deve ter nome")
        except ImportError:
            self.skipTest("Módulo config não disponível")
    
    def test_security_hardcoded_tokens(self):
        """Testa a detecção de tokens hardcoded"""
        # Criar um arquivo temporário com token falso
        with open('test_file.py', 'w') as f:
            f.write('# Arquivo de teste\n')
            f.write('TOKEN = "ghp_1234567890abcdef1234567890abcdef123456"\n')
            f.write('PASSWORD = "senha123"\n')
        
        try:
            from security_check import SecurityChecker
            checker = SecurityChecker()
            checker.python_files = ['test_file.py']
            checker.check_hardcoded_tokens()
            
            # Verificar se o problema foi detectado
            self.assertGreater(len(checker.issues) + len(checker.warnings), 0, 
                              "Deve encontrar problemas de segurança")
        except ImportError:
            self.skipTest("Módulo security_check não disponível")
    
    def test_mock_github_api(self):
        """Testa o processo de obtenção de dados usando dados mockados"""
        # Criar dados mockados
        mock_data = {
            "data": {
                "user": {
                    "name": "Test User",
                    "login": "testuser",
                    "avatarUrl": "https://example.com/avatar.png",
                    "url": "https://github.com/testuser",
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "totalContributions": 500,
                            "weeks": [
                                {
                                    "contributionDays": [
                                        {
                                            "contributionCount": 5,
                                            "date": "2023-01-01",
                                            "weekday": 0,
                                            "color": "#39d353"
                                        },
                                        {
                                            "contributionCount": 3,
                                            "date": "2023-01-02",
                                            "weekday": 1,
                                            "color": "#26a641"
                                        }
                                    ]
                                }
                            ]
                        },
                        "commitContributionsByRepository": [],
                        "issueContributions": {"totalCount": 10, "nodes": []},
                        "pullRequestContributions": {"totalCount": 20, "nodes": []}
                    }
                }
            }
        }
        
        # Salvar dados mockados em um arquivo
        with open('mock_github_data.json', 'w') as f:
            json.dump(mock_data, f)
        
        # Simular processo de extração de dados
        try:
            with open('mock_github_data.json', 'r') as f:
                data_json = json.load(f)
            
            # Extrair dados básicos
            user_data = data_json['data']['user']
            contributions = user_data['contributionsCollection']
            total_contributions = contributions['contributionCalendar']['totalContributions']
            
            # Verificar dados
            self.assertEqual(total_contributions, 500, "Total de contribuições deve ser 500")
            self.assertEqual(user_data['name'], "Test User", "Nome do usuário deve ser 'Test User'")
            
            # Verificar contribuições por dia
            weeks = contributions['contributionCalendar']['weeks']
            days = weeks[0]['contributionDays']
            self.assertEqual(len(days), 2, "Deve ter 2 dias de contribuição")
            self.assertEqual(days[0]['contributionCount'], 5, "Dia 1 deve ter 5 contribuições")
            self.assertEqual(days[1]['contributionCount'], 3, "Dia 2 deve ter 3 contribuições")
        except Exception as e:
            self.fail(f"Erro ao processar dados mockados: {str(e)}")
    
    def test_data_sanitization(self):
        """Testa a função de sanitização de dados"""
        # Criar uma função de sanitização para teste
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
        
        # Dados de teste com conteúdo potencialmente perigoso
        test_data = {
            "name": "User <script>alert('xss')</script>",
            "repositories": [
                {"name": "repo1 <img src=x onerror=alert(1)>"},
                {"name": "normal-repo"}
            ],
            "bio": "Bio with <iframe src='javascript:alert(\"xss\")'></iframe>"
        }
        
        # Sanitizar dados
        sanitized = sanitize_data(test_data)
        
        # Verificar se os dados foram sanitizados corretamente
        self.assertIn("&lt;script&gt;", sanitized["name"], "Tags devem ser escapadas")
        self.assertIn("&lt;img", sanitized["repositories"][0]["name"], "Tags devem ser escapadas")
        self.assertIn("&lt;iframe", sanitized["bio"], "Tags devem ser escapadas")
        self.assertEqual(sanitized["repositories"][1]["name"], "normal-repo", 
                        "Dados normais não devem ser alterados")

def run_tests():
    """Executa os testes unitários"""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    print("\n🔷 Git3D Premium - Testes Unitários\n")
    run_tests() 