#!/usr/bin/env python3
"""
Git3D Premium - Gerenciador de Cache
Ferramenta para visualizar, limpar e gerenciar o cache do sistema
"""

import os
import sys
import json
from datetime import datetime
import argparse
import logging
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('git3d_cache_manager')

# Tentar importar funções do módulo load_env
try:
    from load_env import clear_cache
    custom_clear_available = True
except ImportError:
    custom_clear_available = False

# Tentar importar configurações
try:
    from config import CACHE_DIR, CACHE_ENABLED, CACHE_DURATION
except ImportError:
    # Valores padrão caso o módulo config não esteja disponível
    CACHE_DIR = '.cache'
    CACHE_ENABLED = True
    CACHE_DURATION = 86400

def format_size(size_bytes):
    """Formata tamanho em bytes para formato legível"""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name)-1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:.2f}{size_name[i]}"

def format_timestamp(timestamp):
    """Converte timestamp para formato legível"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "N/A"

def get_cache_items():
    """Retorna todos os itens no cache com suas informações"""
    cache_items = []
    
    if not os.path.exists(CACHE_DIR):
        return cache_items
    
    for filename in os.listdir(CACHE_DIR):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(CACHE_DIR, filename)
        try:
            # Estatísticas do arquivo
            stats = os.stat(filepath)
            file_size = stats.st_size
            creation_time = stats.st_ctime
            modify_time = stats.st_mtime
            
            # Extrair data de expiração do arquivo
            expired = False
            expires_at = None
            
            try:
                with open(filepath, 'r') as f:
                    cache_data = json.load(f)
                    expires_at = cache_data.get('expires_at')
                    expired = expires_at and datetime.now().timestamp() > expires_at
            except (json.JSONDecodeError, IOError):
                expired = True  # Se não conseguir ler, considera expirado
            
            cache_key = filename.replace('.json', '')
            
            cache_items.append({
                'key': cache_key,
                'size': file_size,
                'size_formatted': format_size(file_size),
                'created_at': creation_time,
                'created_at_formatted': format_timestamp(creation_time),
                'expires_at': expires_at,
                'expires_at_formatted': format_timestamp(expires_at) if expires_at else "N/A",
                'expired': expired,
                'path': filepath
            })
        except Exception as e:
            logger.error(f"Erro ao processar item de cache {filename}: {str(e)}")
    
    # Ordenar por data de criação (mais recente primeiro)
    cache_items.sort(key=lambda x: x['created_at'], reverse=True)
    return cache_items

def list_cache():
    """Lista todos os itens no cache com suas informações"""
    items = get_cache_items()
    
    if not items:
        print("📭 O cache está vazio")
        return
    
    # Calcular tamanho total
    total_size = sum(item['size'] for item in items)
    
    print(f"\n🔷 Git3D Premium - Itens em Cache ({len(items)} itens, {format_size(total_size)} total)\n")
    print(f"{'Chave':<30} {'Tamanho':<10} {'Criado em':<20} {'Expira em':<20} {'Status'}")
    print("-" * 90)
    
    for item in items:
        status = "🔴 Expirado" if item['expired'] else "🟢 Válido"
        print(f"{item['key']:<30} {item['size_formatted']:<10} {item['created_at_formatted']:<20} {item['expires_at_formatted']:<20} {status}")
    
    print("-" * 90)
    print(f"📊 Tamanho total: {format_size(total_size)}")
    print(f"📂 Diretório: {os.path.abspath(CACHE_DIR)}")
    print(f"⚙️ Cache {'habilitado' if CACHE_ENABLED else 'desabilitado'} | Duração padrão: {CACHE_DURATION // 3600} horas")

def clear_all_cache():
    """Limpa todo o cache"""
    if not os.path.exists(CACHE_DIR):
        print("📭 O cache já está vazio")
        return
    
    if custom_clear_available:
        # Usar a função do módulo load_env se disponível
        if clear_cache():
            print("✅ Cache limpo com sucesso!")
        else:
            print("❌ Erro ao limpar cache")
        return
    
    try:
        # Remover e recriar o diretório
        shutil.rmtree(CACHE_DIR)
        os.makedirs(CACHE_DIR, exist_ok=True)
        print("✅ Cache limpo com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao limpar cache: {str(e)}")

def clear_expired_cache():
    """Limpa apenas itens expirados do cache"""
    items = get_cache_items()
    expired_count = 0
    
    if not items:
        print("📭 O cache está vazio")
        return
    
    for item in items:
        if item['expired']:
            try:
                os.remove(item['path'])
                expired_count += 1
            except Exception as e:
                logger.error(f"Erro ao remover item expirado {item['key']}: {str(e)}")
    
    print(f"✅ {expired_count} itens expirados removidos do cache")

def clear_item(cache_key):
    """Limpa um item específico do cache"""
    if not os.path.exists(CACHE_DIR):
        print("📭 O cache está vazio")
        return
    
    if custom_clear_available:
        # Usar a função do módulo load_env se disponível
        if clear_cache(cache_key):
            print(f"✅ Item '{cache_key}' removido do cache com sucesso!")
        else:
            print(f"❌ Erro ao remover item '{cache_key}' do cache")
        return
    
    filepath = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if not os.path.exists(filepath):
        print(f"❌ Item '{cache_key}' não encontrado no cache")
        return
    
    try:
        os.remove(filepath)
        print(f"✅ Item '{cache_key}' removido do cache com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao remover item '{cache_key}' do cache: {str(e)}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Git3D Premium - Gerenciador de Cache')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar todos os itens no cache')
    
    # Comando clear
    clear_parser = subparsers.add_parser('clear', help='Limpar cache')
    clear_parser.add_argument('--all', action='store_true', help='Limpar todo o cache')
    clear_parser.add_argument('--expired', action='store_true', help='Limpar apenas itens expirados')
    clear_parser.add_argument('--item', type=str, help='Limpar um item específico do cache')
    
    # Analisar argumentos
    args = parser.parse_args()
    
    # Verificar comando
    if args.command == 'list' or not args.command:
        list_cache()
    elif args.command == 'clear':
        if args.all:
            clear_all_cache()
        elif args.expired:
            clear_expired_cache()
        elif args.item:
            clear_item(args.item)
        else:
            print("❌ Especifique uma opção de limpeza: --all, --expired ou --item")
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 