import os
import re
from datetime import datetime

def atualizar_readme(caminho_readme, caminho_gif=None, caminho_html=None):
    """
    Atualiza o README.md com a visualização 3D do GitHub
    
    Args:
        caminho_readme: Caminho para o arquivo README.md
        caminho_gif: Caminho para o arquivo GIF
        caminho_html: Caminho para o arquivo HTML
    """
    # Verificar se o README existe
    if not os.path.exists(caminho_readme):
        print(f"⚠️ README não encontrado em {caminho_readme}")
        return False
    
    # Ler o conteúdo atual
    with open(caminho_readme, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Definir o padrão para substituição ou inserção
    padrao_viz_3d = r"## 🔷 Painel 3D de Contribuições.*?---"
    
    # Data atual
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Preparar a nova seção
    nova_secao = f"""## 🔷 Painel 3D de Contribuições – Powered by BeOnSafe

> Visualize minha dedicação e ritmo de contribuição de forma interativa e moderna.

"""
    
    # Adicionar GIF se disponível
    if caminho_gif and os.path.exists(caminho_gif):
        nova_secao += f"![Painel 3D]({caminho_gif})\n\n"
    
    # Adicionar link para HTML interativo se disponível
    if caminho_html and os.path.exists(caminho_html):
        rel_path_html = os.path.relpath(caminho_html, os.path.dirname(caminho_readme))
        nova_secao += f"[📊 Versão Interativa]({rel_path_html}) _(Atualizado em {data_atual})_\n\n"
    
    nova_secao += "---"
    
    # Verificar se existe a seção para substituir
    if re.search(padrao_viz_3d, conteudo, re.DOTALL):
        # Substituir a seção existente
        novo_conteudo = re.sub(padrao_viz_3d, nova_secao, conteudo, flags=re.DOTALL)
    else:
        # Procurar um lugar adequado para inserir
        if "# " in conteudo:
            # Após a primeira seção principal
            partes = conteudo.split("# ", 1)
            if len(partes) > 1:
                match = re.search(r"^.*?\n", "# " + partes[1])
                if match:
                    pos = len(partes[0]) + match.end()
                    novo_conteudo = conteudo[:pos] + "\n" + nova_secao + "\n\n" + conteudo[pos:]
                else:
                    novo_conteudo = conteudo + "\n\n" + nova_secao + "\n"
            else:
                novo_conteudo = conteudo + "\n\n" + nova_secao + "\n"
        else:
            # Adicionar ao final
            novo_conteudo = conteudo + "\n\n" + nova_secao + "\n"
    
    # Escrever o novo conteúdo
    with open(caminho_readme, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    
    print(f"✅ README atualizado com sucesso em {caminho_readme}")
    return True

if __name__ == "__main__":
    # Caminhos para os arquivos
    caminho_readme = "./README.md"  # README na pasta raiz do projeto
    caminho_gif = "images/github_3d_beonsafe.gif"
    caminho_html = "images/github_3d_beonsafe.html"
    
    atualizar_readme(caminho_readme, caminho_gif, caminho_html) 