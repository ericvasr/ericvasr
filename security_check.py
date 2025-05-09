#!/usr/bin/env python3
"""
Git3D Premium - Verificador de Segurança
Ferramenta para analisar e garantir a segurança do projeto
"""

import os
import sys
import json
import re
import logging
import glob
import subprocess
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', f'security_{datetime.now().strftime("%Y%m%d")}.log'), mode='a')
    ]
)
logger = logging.getLogger('git3d_security')

# Garantir que o diretório de logs exista
os.makedirs('logs', exist_ok=True)

class SecurityChecker:
    """Classe para executar verificações de segurança no projeto"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.passed = []
        self.python_files = []
        self.github_token_regex = r'ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82}'
        self.generic_token_regex = r'[\'"][0-9a-f]{32,64}[\'"]'
        self.sensitive_vars = ['password', 'token', 'secret', 'key', 'pwd', 'passwd']
    
    def scan_for_python_files(self):
        """Encontra todos os arquivos Python no projeto"""
        self.python_files = glob.glob('**/*.py', recursive=True)
        logger.info(f"🔍 Encontrados {len(self.python_files)} arquivos Python para análise")
    
    def check_hardcoded_tokens(self):
        """Verifica tokens codificados diretamente no código"""
        logger.info("🔐 Verificando tokens e senhas hardcoded...")
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Verificar por tokens do GitHub
                    gh_tokens = re.findall(self.github_token_regex, content)
                    if gh_tokens:
                        self.issues.append({
                            'file': file_path,
                            'issue': f"Token do GitHub encontrado diretamente no código",
                            'count': len(gh_tokens),
                            'severity': 'ALTA'
                        })
                    
                    # Verificar por tokens genéricos
                    gen_tokens = re.findall(self.generic_token_regex, content)
                    if gen_tokens:
                        self.warnings.append({
                            'file': file_path,
                            'issue': f"Possível token/chave encontrado no código",
                            'count': len(gen_tokens),
                            'severity': 'MÉDIA'
                        })
                    
                    # Verificar linhas por linha por atribuições sensíveis
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        # Ignorar comentários
                        if line.strip().startswith('#'):
                            continue
                        
                        # Verificar atribuições de variáveis sensíveis
                        for var in self.sensitive_vars:
                            pattern = rf'\b{var}\s*=\s*[\'"][^\'"]+[\'"]'
                            if re.search(pattern, line, re.IGNORECASE):
                                # Verificar se é uma variável de ambiente
                                if not re.search(r'os\.getenv|os\.environ', line):
                                    self.warnings.append({
                                        'file': file_path,
                                        'line': i + 1,
                                        'code': line.strip(),
                                        'issue': f"Variável sensível '{var}' pode conter valor hardcoded",
                                        'severity': 'MÉDIA'
                                    })
            except Exception as e:
                logger.error(f"Erro ao analisar {file_path}: {str(e)}")
        
        if not self.issues and not self.warnings:
            self.passed.append("✅ Nenhum token ou senha hardcoded encontrado")
    
    def check_env_file(self):
        """Verifica se há arquivo .env versionado e exposto"""
        logger.info("🔐 Verificando arquivo .env...")
        
        if os.path.exists('.env'):
            # Verificar se .env está no .gitignore
            gitignore_found = False
            env_ignored = False
            
            if os.path.exists('.gitignore'):
                with open('.gitignore', 'r') as f:
                    content = f.read()
                    gitignore_found = True
                    if '.env' in content.split('\n'):
                        env_ignored = True
            
            if not gitignore_found:
                self.warnings.append({
                    'issue': "Arquivo .gitignore não encontrado",
                    'severity': 'BAIXA'
                })
            
            if not env_ignored:
                self.issues.append({
                    'issue': "Arquivo .env não está listado no .gitignore",
                    'severity': 'ALTA',
                    'recommendation': "Adicione '.env' ao arquivo .gitignore"
                })
            
            # Verificar conteúdo do .env por tokens e senhas
            try:
                with open('.env', 'r') as f:
                    env_content = f.read()
                    gh_tokens = re.findall(self.github_token_regex, env_content)
                    if gh_tokens and not env_ignored:
                        self.issues.append({
                            'issue': f"Token do GitHub encontrado no arquivo .env não-ignorado",
                            'count': len(gh_tokens),
                            'severity': 'ALTA',
                            'recommendation': "Adicione .env ao .gitignore e remova o arquivo do repositório"
                        })
            except Exception as e:
                logger.error(f"Erro ao analisar arquivo .env: {str(e)}")
        else:
            logger.info("ℹ️ Arquivo .env não encontrado")
    
    def check_github_workflow(self):
        """Verifica configurações de segurança no workflow do GitHub"""
        logger.info("🔐 Verificando workflows do GitHub...")
        
        workflow_dir = '.github/workflows'
        if not os.path.exists(workflow_dir):
            logger.info("ℹ️ Diretório de workflows não encontrado")
            return
        
        workflow_files = glob.glob(f'{workflow_dir}/*.yml') + glob.glob(f'{workflow_dir}/*.yaml')
        for wf_path in workflow_files:
            try:
                with open(wf_path, 'r') as f:
                    content = f.read()
                    
                    # Verificar se há secrets expostos
                    gh_tokens = re.findall(self.github_token_regex, content)
                    if gh_tokens:
                        self.issues.append({
                            'file': wf_path,
                            'issue': f"Token do GitHub encontrado diretamente no workflow",
                            'count': len(gh_tokens),
                            'severity': 'ALTA'
                        })
                    
                    # Verificar uso seguro de tokens
                    if 'GITHUB_TOKEN: ${{ github.token }}' in content:
                        self.warnings.append({
                            'file': wf_path,
                            'issue': "Uso de github.token em vez de secrets.GITHUB_TOKEN",
                            'severity': 'MÉDIA',
                            'recommendation': "Use ${{ secrets.GITHUB_TOKEN }} para maior segurança"
                        })
                    
                    # Verificar permissões no workflow
                    if not re.search(r'permissions:', content):
                        self.warnings.append({
                            'file': wf_path,
                            'issue': "Permissões não especificadas no workflow",
                            'severity': 'MÉDIA',
                            'recommendation': "Especifique permissões mínimas necessárias para o workflow"
                        })
            except Exception as e:
                logger.error(f"Erro ao analisar {wf_path}: {str(e)}")
    
    def check_input_validation(self):
        """Verifica validação de entrada e vulnerabilidades de injeção"""
        logger.info("🔐 Verificando validação de entrada em endpoints...")
        
        input_sources = [
            'request.args.get', 'request.form.get', 'request.json.get', 
            'input(', 'sys.argv', 'parse_args'
        ]
        
        risky_functions = [
            'exec(', 'eval(', 'subprocess.', 'os.system', 'os.popen', 
            'shell=True', 'open('
        ]
        
        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    input_lines = []
                    
                    # Identificar linhas com entrada de usuário
                    for i, line in enumerate(lines):
                        for source in input_sources:
                            if source in line and not line.strip().startswith('#'):
                                input_lines.append((i, line.strip()))
                    
                    # Analisar uso de funções arriscadas com entrada de usuário
                    for i, line in enumerate(lines):
                        for func in risky_functions:
                            if func in line and not line.strip().startswith('#'):
                                # Verificar se há validação na proximidade
                                has_validation = False
                                context_start = max(0, i - 5)
                                context_end = min(len(lines), i + 5)
                                
                                for j in range(context_start, context_end):
                                    if any(val in lines[j] for val in ['validate', 'sanitize', 'escape', 'strip', 'filter']):
                                        has_validation = True
                                        break
                                
                                if not has_validation:
                                    self.warnings.append({
                                        'file': file_path,
                                        'line': i + 1,
                                        'code': line.strip(),
                                        'issue': f"Função potencialmente arriscada '{func.strip()}' sem validação aparente",
                                        'severity': 'MÉDIA',
                                        'recommendation': "Adicione validação/sanitização antes de usar entrada externa"
                                    })
            except Exception as e:
                logger.error(f"Erro ao analisar {file_path}: {str(e)}")
    
    def check_dependencies(self):
        """Verifica dependências por vulnerabilidades conhecidas"""
        logger.info("🔐 Verificando dependências...")
        
        if not os.path.exists('requirements.txt'):
            logger.info("ℹ️ Arquivo requirements.txt não encontrado")
            return
        
        try:
            # Verificar se pip-audit está instalado
            subprocess.run(['pip', 'show', 'pip-audit'], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            
            # Executar pip-audit
            logger.info("🔍 Executando pip-audit para verificar vulnerabilidades...")
            result = subprocess.run(['pip-audit', '-r', 'requirements.txt', '--format', 'json'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                # Processar resultado
                audit_result = json.loads(result.stdout.decode())
                vulnerabilities = audit_result.get('vulnerabilities', [])
                
                if vulnerabilities:
                    for vuln in vulnerabilities:
                        self.warnings.append({
                            'dependency': vuln.get('name'),
                            'version': vuln.get('version'),
                            'issue': f"Vulnerabilidade encontrada: {vuln.get('description')}",
                            'severity': 'ALTA',
                            'recommendation': f"Atualize para uma versão segura (>= {vuln.get('fix_version')})"
                        })
                else:
                    self.passed.append("✅ Nenhuma vulnerabilidade encontrada nas dependências")
            else:
                logger.warning(f"⚠️ pip-audit retornou código {result.returncode}: {result.stderr.decode()}")
                # Abordagem alternativa sem pip-audit
                self._check_dependencies_basic()
        except Exception as e:
            logger.warning(f"⚠️ pip-audit não está disponível: {str(e)}")
            self._check_dependencies_basic()
    
    def _check_dependencies_basic(self):
        """Verificação básica de dependências sem ferramentas externas"""
        with open('requirements.txt', 'r') as f:
            dependencies = f.readlines()
        
        # Lista de dependências com versões potencialmente vulneráveis
        known_issues = {
            'flask': ('< 2.0.0', "Versões antigas do Flask podem ter vulnerabilidades"),
            'django': ('< 3.2.0', "Versões antigas do Django podem ter vulnerabilidades"),
            'requests': ('< 2.25.0', "Versões antigas do Requests podem ter vulnerabilidades"),
            'pillow': ('< 8.2.0', "Versões antigas do Pillow podem ter vulnerabilidades"),
            'matplotlib': ('< 3.4.0', "Versões antigas do Matplotlib podem ter problemas de segurança"),
            'numpy': ('< 1.20.0', "Versões antigas do NumPy podem ter problemas de segurança"),
            'pandas': ('< 1.3.0', "Versões antigas do Pandas podem ter problemas de segurança"),
        }
        
        for dep in dependencies:
            if dep.strip() and not dep.strip().startswith('#'):
                parts = dep.strip().split('==')
                if len(parts) == 2:
                    name, version = parts
                    if name in known_issues:
                        issue_version, issue_desc = known_issues[name]
                        if self._version_compare(version, issue_version):
                            self.warnings.append({
                                'dependency': name,
                                'version': version,
                                'issue': issue_desc,
                                'severity': 'MÉDIA',
                                'recommendation': f"Considere atualizar para uma versão mais recente"
                            })
    
    def _version_compare(self, version, constraint):
        """Compara versões com base na restrição (< x.y.z)"""
        try:
            if constraint.startswith('< '):
                limit = constraint[2:]
                v1 = [int(x) for x in version.split('.')]
                v2 = [int(x) for x in limit.split('.')]
                
                # Preencher com zeros para garantir mesmo comprimento
                while len(v1) < len(v2):
                    v1.append(0)
                while len(v2) < len(v1):
                    v2.append(0)
                
                # Comparar componentes de versão
                for i in range(len(v1)):
                    if v1[i] < v2[i]:
                        return True
                    elif v1[i] > v2[i]:
                        return False
                
                # Versões iguais
                return False
            
            return False
        except Exception:
            # Em caso de erro, sendo conservador
            return True
    
    def run_all_checks(self):
        """Executa todas as verificações de segurança"""
        logger.info("🔐 Iniciando verificação de segurança do Git3D Premium...")
        
        # Encontrar arquivos Python
        self.scan_for_python_files()
        
        # Executar verificações
        self.check_hardcoded_tokens()
        self.check_env_file()
        self.check_github_workflow()
        self.check_input_validation()
        self.check_dependencies()
        
        # Relatar resultados
        self.report_results()
    
    def report_results(self):
        """Gera relatório dos resultados de segurança"""
        print("\n" + "=" * 80)
        print("🔒 RELATÓRIO DE SEGURANÇA - GIT3D PREMIUM 🔒".center(80))
        print("=" * 80)
        
        # Problemas críticos
        if self.issues:
            print("\n❌ PROBLEMAS CRÍTICOS ENCONTRADOS:".ljust(80))
            print("-" * 80)
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue.get('issue')} ({issue.get('severity')})")
                if 'file' in issue:
                    print(f"   Arquivo: {issue.get('file')}")
                if 'line' in issue:
                    print(f"   Linha {issue.get('line')}: {issue.get('code')}")
                if 'recommendation' in issue:
                    print(f"   ✅ Recomendação: {issue.get('recommendation')}")
                print()
        
        # Avisos
        if self.warnings:
            print("\n⚠️ AVISOS:".ljust(80))
            print("-" * 80)
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning.get('issue')} ({warning.get('severity')})")
                if 'file' in warning:
                    print(f"   Arquivo: {warning.get('file')}")
                if 'line' in warning:
                    print(f"   Linha {warning.get('line')}: {warning.get('code')}")
                if 'dependency' in warning:
                    print(f"   Dependência: {warning.get('dependency')} {warning.get('version')}")
                if 'recommendation' in warning:
                    print(f"   ✅ Recomendação: {warning.get('recommendation')}")
                print()
        
        # Verificações aprovadas
        if self.passed:
            print("\n✅ VERIFICAÇÕES APROVADAS:".ljust(80))
            print("-" * 80)
            for i, passed in enumerate(self.passed, 1):
                print(f"{i}. {passed}")
            print()
        
        # Resumo
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        total_passed = len(self.passed)
        
        print("\n📊 RESUMO:".ljust(80))
        print("-" * 80)
        print(f"Problemas críticos: {total_issues}")
        print(f"Avisos: {total_warnings}")
        print(f"Verificações aprovadas: {total_passed}")
        
        # Status geral
        if total_issues > 0:
            status = "❌ FALHOU"
        elif total_warnings > 0:
            status = "⚠️ PASSOU COM AVISOS"
        else:
            status = "✅ PASSOU"
        
        print(f"\nStatus da verificação de segurança: {status}")
        print("=" * 80)
        
        # Salvar relatório em arquivo
        report_file = os.path.join('logs', f'security_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        try:
            with open(report_file, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("RELATÓRIO DE SEGURANÇA - GIT3D PREMIUM".center(80) + "\n")
                f.write("=" * 80 + "\n")
                f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Status: {status}\n")
                f.write(f"Problemas críticos: {total_issues}\n")
                f.write(f"Avisos: {total_warnings}\n")
                f.write(f"Verificações aprovadas: {total_passed}\n")
                f.write("=" * 80 + "\n")
            
            logger.info(f"✅ Relatório salvo em {report_file}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {str(e)}")

def main():
    checker = SecurityChecker()
    checker.run_all_checks()

if __name__ == "__main__":
    main() 