"""
Git3D Premium - Arquivo de Configuração Central
Contém todas as configurações globais para personalização do projeto
"""

import os
import logging
import json
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', f'git3d_{datetime.now().strftime("%Y%m%d")}.log'), mode='a')
    ]
)

# Certifique-se de que o diretório de logs existe
os.makedirs('logs', exist_ok=True)

logger = logging.getLogger('git3d_config')

# Configurações do Usuário
USERNAME = "ericvasr"  # Nome de usuário do GitHub
COMPANY_NAME = "BeOnSafe"  # Nome da empresa/organização

# Configurações de Segurança
SANITIZE_DATA = True  # Sanitiza dados para prevenir XSS e injeções
VERIFY_SSL = True  # Verificar certificados SSL em requisições

# Configurações de Cache
CACHE_ENABLED = True  # Habilita o sistema de cache
CACHE_DURATION = 86400  # Duração do cache em segundos (24 horas)
CACHE_DIR = '.cache'  # Diretório de cache

# Configurações de Visualização
VISUALIZATION_SETTINGS = {
    "width": 1200,          # Largura em pixels
    "height": 800,          # Altura em pixels
    "animation_frames": 120, # Número de frames para animação
    "animation_duration": 15, # Duração da animação em segundos
    "quality": "high",      # Qualidade da renderização (low, medium, high)
    "show_labels": True,    # Mostrar labels no gráfico
    "show_grid": True,      # Mostrar grade no gráfico
    "auto_rotate": True,    # Rotação automática no modo interativo
    "export_formats": ["html", "png", "gif"] # Formatos para exportação
}

# Temas Visuais - selecione o tema ativo alterando a variável ACTIVE_THEME
THEMES = {
    "tech_noir": {
        "name": "Tech Noir",
        "description": "Tema escuro com cores neon em estilo cyberpunk",
        "colors": {
            'background': '#0A0E17',      # Fundo muito escuro (quase preto com tom azulado)
            'surface': '#121822',         # Superfície um pouco mais clara que o fundo
            'primary': '#0C4A6E',         # Azul escuro tecnológico
            'secondary': '#065A82',       # Azul médio tecnológico
            'accent': '#00CFFD',          # Azul neon brilhante (cyan)
            'accent2': '#7B61FF',         # Roxo/violeta neon
            'highlight': '#00FFC6',       # Verde-água neon
            'warning': '#FFB200',         # Laranja/amarelo
            'error': '#FF4365',           # Vermelho/rosa neon
            'text_primary': '#E2E8F0',    # Texto principal (quase branco com tom azulado)
            'text_secondary': '#94A3B8',  # Texto secundário (cinza claro)
            'grid': '#1E293B',            # Linhas de grade (azul muito escuro)
            'low_activity': '#0F172A',    # Atividade baixa (quase preto)
            'medium_activity': '#065A82', # Atividade média (azul escuro)
            'high_activity': '#00CFFD'    # Atividade alta (azul neon)
        }
    },
    "corporate": {
        "name": "Corporate",
        "description": "Tema profissional em tons azuis para ambiente corporativo",
        "colors": {
            'background': '#F8FAFC',      # Fundo muito claro (quase branco)
            'surface': '#F1F5F9',         # Superfície um pouco mais escura que o fundo
            'primary': '#0F4C81',         # Azul escuro corporativo
            'secondary': '#3B82F6',       # Azul corporativo médio
            'accent': '#0EA5E9',          # Azul vibrante
            'accent2': '#7C3AED',         # Roxo/violeta 
            'highlight': '#10B981',       # Verde corporativo
            'warning': '#F59E0B',         # Laranja/amarelo
            'error': '#EF4444',           # Vermelho corporativo
            'text_primary': '#1E293B',    # Texto principal (quase preto)
            'text_secondary': '#64748B',  # Texto secundário (cinza médio)
            'grid': '#E2E8F0',            # Linhas de grade (cinza claro)
            'low_activity': '#E2E8F0',    # Atividade baixa (cinza muito claro)
            'medium_activity': '#93C5FD', # Atividade média (azul claro)
            'high_activity': '#2563EB'    # Atividade alta (azul escuro)
        }
    },
    "dark_elegant": {
        "name": "Dark Elegant",
        "description": "Tema escuro minimalista com toques de elegância",
        "colors": {
            'background': '#121212',      # Fundo escuro
            'surface': '#1E1E1E',         # Superfície um pouco mais clara que o fundo
            'primary': '#BB86FC',         # Roxo/lilás elegante
            'secondary': '#3700B3',       # Roxo escuro
            'accent': '#03DAC6',          # Verde-água vibrante
            'accent2': '#CF6679',         # Rosa/coral
            'highlight': '#FFAB00',       # Amarelo âmbar
            'warning': '#FFAB00',         # Amarelo âmbar (mesmo que highlight)
            'error': '#CF6679',           # Rosa/coral (mesmo que accent2)
            'text_primary': '#F5F5F5',    # Texto principal (quase branco)
            'text_secondary': '#B0B0B0',  # Texto secundário (cinza claro)
            'grid': '#2D2D2D',            # Linhas de grade (cinza escuro)
            'low_activity': '#1E1E1E',    # Atividade baixa (quase preto)
            'medium_activity': '#5C5C5C', # Atividade média (cinza médio)
            'high_activity': '#BB86FC'    # Atividade alta (roxo/lilás)
        }
    }
}

# Tema ativo para visualização
ACTIVE_THEME = "tech_noir"

# Diretórios de saída
OUTPUT_DIRS = {
    "images": "images",
    "data": "data",
    "logs": "logs",
    "cache": CACHE_DIR
}

# Certificar-se de que todos os diretórios existam
for directory in OUTPUT_DIRS.values():
    os.makedirs(directory, exist_ok=True)

# Função para salvar as configurações atuais em um arquivo
def save_config():
    """Salva as configurações atuais em um arquivo JSON"""
    config = {
        "username": USERNAME,
        "company_name": COMPANY_NAME,
        "visualization": VISUALIZATION_SETTINGS,
        "active_theme": ACTIVE_THEME,
        "cache_enabled": CACHE_ENABLED,
        "cache_duration": CACHE_DURATION,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        with open('git3d_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("✅ Configurações salvas com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao salvar configurações: {str(e)}")
        return False

# Função para carregar configurações de um arquivo
def load_config():
    """Carrega configurações de um arquivo JSON"""
    global USERNAME, COMPANY_NAME, VISUALIZATION_SETTINGS, ACTIVE_THEME, CACHE_ENABLED, CACHE_DURATION
    
    if not os.path.exists('git3d_config.json'):
        logger.info("⚠️ Arquivo de configuração não encontrado, usando valores padrão")
        return False
    
    try:
        with open('git3d_config.json', 'r') as f:
            config = json.load(f)
        
        # Atualizar variáveis globais
        USERNAME = config.get('username', USERNAME)
        COMPANY_NAME = config.get('company_name', COMPANY_NAME)
        VISUALIZATION_SETTINGS.update(config.get('visualization', {}))
        ACTIVE_THEME = config.get('active_theme', ACTIVE_THEME)
        CACHE_ENABLED = config.get('cache_enabled', CACHE_ENABLED)
        CACHE_DURATION = config.get('cache_duration', CACHE_DURATION)
        
        logger.info("✅ Configurações carregadas com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao carregar configurações: {str(e)}")
        return False

# Função para obter o tema ativo
def get_active_theme():
    """Retorna o dicionário de cores do tema ativo"""
    return THEMES.get(ACTIVE_THEME, THEMES['tech_noir'])

# Carregar configurações no início
try:
    load_config()
except Exception as e:
    logger.error(f"❌ Erro ao inicializar configurações: {str(e)}")

# Inicialização
logger.info(f"🔷 Git3D Premium inicializado - Usuário: {USERNAME} - Tema: {get_active_theme()['name']}")

if __name__ == "__main__":
    # Ao executar diretamente, exibe as configurações atuais
    print(f"\n🔷 Git3D Premium - Configurações Atuais\n")
    print(f"👤 Usuário: {USERNAME}")
    print(f"🏢 Empresa: {COMPANY_NAME}")
    print(f"🎨 Tema Ativo: {get_active_theme()['name']} - {get_active_theme()['description']}")
    print(f"🔒 Cache Habilitado: {'Sim' if CACHE_ENABLED else 'Não'}")
    print(f"⏱️ Duração do Cache: {CACHE_DURATION // 3600} horas")
    print(f"\n📊 Configurações de Visualização:")
    for key, value in VISUALIZATION_SETTINGS.items():
        print(f"  - {key}: {value}")
    
    # Pergunta se o usuário quer salvar as configurações atuais
    response = input("\n💾 Deseja salvar estas configurações? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        save_config()
        print("✅ Configurações salvas com sucesso!")
    else:
        print("⏹️ Operação cancelada.") 