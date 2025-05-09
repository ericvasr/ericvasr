import os
import sys
import subprocess

# Verificar se o token está disponível
if not os.getenv("GITHUB_TOKEN"):
    # Em ambiente local, permitir entrada manual
    token = input("Digite seu token do GitHub: ").strip()
    if token:
        os.environ["GITHUB_TOKEN"] = token
    else:
        print("❌ Erro: Token do GitHub não fornecido")
        sys.exit(1)
    
# Verificar se o usuário foi fornecido como argumento
if len(sys.argv) != 2:
    username = input("Digite seu nome de usuário do GitHub: ").strip()
    if not username:
        print("❌ Erro: Nome de usuário não fornecido")
        sys.exit(1)
else:
    username = sys.argv[1]
    
# Modificar os scripts para usar o nome de usuário
for script in ["fetch_contributions.py", "visualize_3d.py", "generate_advanced_3d.py"]:
    with open(script, "r") as f:
        content = f.read()
    
    content = content.replace('USERNAME = "ericvasr"', f'USERNAME = "{username}"')
    
    with open(script, "w") as f:
        f.write(content)

# Criar diretório de imagens se não existir
os.makedirs("images", exist_ok=True)

# Executar cada script diretamente em sequência
print("📊 Buscando dados de contribuições...")
try:
    subprocess.run([sys.executable, "fetch_contributions.py"], check=True)
    
    print("🎨 Gerando visualizações 3D...")
    subprocess.run([sys.executable, "generate_advanced_3d.py"], check=True)
    
    print("📝 Atualizando README...")
    subprocess.run([sys.executable, "update_readme.py"], check=True)
    
    print("✅ Processo concluído com sucesso!")
    print("Arquivos gerados:")
    
    if os.path.exists("images"):
        files = os.listdir("images")
        for file in sorted(files):
            print(f"  - images/{file}")
    else:
        print("Diretório images/ não existe.")
        
except subprocess.CalledProcessError as e:
    print(f"❌ Erro ao executar script: {e}")
    sys.exit(1) 