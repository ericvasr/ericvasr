import os
import re
import json
from datetime import datetime
import logging
import sys

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('git3d_readme')

def carregar_estatisticas():
    """
    Carrega estatísticas de contribuições de diversos arquivos
    """
    estatisticas = {
        "usuario": None,
        "total_contribuicoes": 0,
        "media_diaria": 0,
        "sequencia_atual": 0,
        "sequencia_maxima": 0,
        "dias_ativos": 0,
        "taxa_atividade": 0,
        "melhor_dia": None,
        "repositorios": [],
        "issues": 0,
        "pull_requests": 0
    }
    
    # Carregar dados do usuário
    if os.path.exists("github_user_data.json"):
        try:
            with open("github_user_data.json", "r") as f:
                user_data = json.load(f)
                estatisticas["usuario"] = user_data.get("username", "")
                estatisticas["nome"] = user_data.get("name", "")
                estatisticas["avatar_url"] = user_data.get("avatar_url", "")
                estatisticas["profile_url"] = user_data.get("profile_url", "")
                estatisticas["total_contribuicoes"] = user_data.get("total_contributions", 0)
                estatisticas["issues"] = user_data.get("issue_count", 0)
                estatisticas["pull_requests"] = user_data.get("pr_count", 0)
                estatisticas["repositorios"] = user_data.get("top_repositories", [])
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar dados do usuário: {str(e)}")
    
    # Carregar estatísticas de contribuições
    if os.path.exists("contrib_stats.json"):
        try:
            with open("contrib_stats.json", "r") as f:
                stats = json.load(f)
                estatisticas["media_diaria"] = stats.get("daily_average", 0)
                estatisticas["sequencia_atual"] = stats.get("streak_info", {}).get("current_streak", 0)
                estatisticas["sequencia_maxima"] = stats.get("streak_info", {}).get("max_streak", 0)
                
                # Encontrar o melhor dia da semana
                weekday_totals = stats.get("weekday_totals", {})
                if weekday_totals:
                    estatisticas["melhor_dia"] = max(weekday_totals.items(), key=lambda x: x[1])[0]
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar estatísticas: {str(e)}")
            
    # Carregar dados avançados da visualização 3D
    if os.path.exists("images/github_stats.json"):
        try:
            with open("images/github_stats.json", "r") as f:
                viz_stats = json.load(f)
                estatisticas["dias_ativos"] = viz_stats.get("active_days", 0)
                estatisticas["taxa_atividade"] = viz_stats.get("activity_rate", 0)
                estatisticas["score_intensidade"] = viz_stats.get("intensity_score", 0)
                
                # Usar estes dados se ainda não estiverem definidos
                if not estatisticas["melhor_dia"]:
                    estatisticas["melhor_dia"] = viz_stats.get("best_day", "")
                if not estatisticas["sequencia_maxima"]:
                    estatisticas["sequencia_maxima"] = viz_stats.get("max_streak", 0)
                if not estatisticas["sequencia_atual"]:
                    estatisticas["sequencia_atual"] = viz_stats.get("current_streak", 0)
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar estatísticas avançadas: {str(e)}")
    
    return estatisticas

def criar_badges(estatisticas):
    """
    Gera badges para as estatísticas
    """
    # URLs base para criar badges
    shields_url = "https://img.shields.io"
    
    # Cores tecnológicas
    cores = {
        "azul_tech": "00CFFD",
        "verde_tech": "00FFC6", 
        "roxo_tech": "7B61FF",
        "laranja_tech": "FFB200",
        "background": "0A0E17"
    }
    
    badges = {
        "contribuicoes": f"{shields_url}/badge/Contribuições-{estatisticas['total_contribuicoes']}-{cores['azul_tech']}?style=for-the-badge&logo=github&logoColor=white&labelColor=0C4A6E",
        "sequencia": f"{shields_url}/badge/Sequência-{estatisticas['sequencia_atual']}%20dias-{cores['verde_tech']}?style=for-the-badge&logo=firebase&logoColor=white&labelColor=065A82",
        "pull_requests": f"{shields_url}/badge/Pull%20Requests-{estatisticas['pull_requests']}-{cores['roxo_tech']}?style=for-the-badge&logo=git&logoColor=white&labelColor=333333",
        "issues": f"{shields_url}/badge/Issues-{estatisticas['issues']}-{cores['laranja_tech']}?style=for-the-badge&logo=jira&logoColor=white&labelColor=333333",
    }
    
    return badges

def atualizar_readme(caminho_readme, caminho_gif=None, caminho_html=None):
    """
    Atualiza o README.md com a visualização 3D do GitHub e estatísticas avançadas
    
    Args:
        caminho_readme: Caminho para o arquivo README.md
        caminho_gif: Caminho para o arquivo GIF
        caminho_html: Caminho para o arquivo HTML
    """
    # Carregar estatísticas
    estatisticas = carregar_estatisticas()
    badges = criar_badges(estatisticas)
    
    # Verificar se o README existe
    if not os.path.exists(caminho_readme):
        logger.warning(f"⚠️ README não encontrado em {caminho_readme}")
        with open(caminho_readme, 'w', encoding='utf-8') as f:
            f.write(f"# Perfil de {estatisticas['usuario'] or 'GitHub'}\n\n")
        logger.info(f"✅ README criado em {caminho_readme}")
    
    # Ler o conteúdo atual
    with open(caminho_readme, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Definir o padrão para substituição ou inserção
    padrao_viz_3d = r"## 🔷 Painel 3D de Contribuições.*?---"
    
    # Data atual
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    # Definir caminhos relativos para imagens
    rel_path_gif = os.path.relpath(caminho_gif, os.path.dirname(caminho_readme)) if caminho_gif and os.path.exists(caminho_gif) else None
    rel_path_html = os.path.relpath(caminho_html, os.path.dirname(caminho_readme)) if caminho_html and os.path.exists(caminho_html) else None
    
    # URLs absolutas para GitHub
    github_username = estatisticas['usuario'] or "ericvasr"
    github_gif_url = f"https://raw.githubusercontent.com/{github_username}/{github_username}/main/images/github_3d_beonsafe.gif"
    github_html_url = f"https://htmlpreview.github.io/?https://github.com/{github_username}/{github_username}/blob/main/images/github_3d_beonsafe.html"
    
    # Estilo Tech com cores escuras
    tech_style = """
<style>
.tech-container {
  background-color: #0A0E17;
  color: #E2E8F0;
  border-radius: 8px;
  overflow: hidden;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  margin-bottom: 20px;
  border: 1px solid #00CFFD;
  box-shadow: 0 0 15px rgba(0, 207, 253, 0.3);
}
.tech-header {
  background-color: #121822;
  color: #00CFFD;
  padding: 10px 15px;
  font-weight: bold;
  border-bottom: 1px solid #00CFFD;
}
.tech-content {
  padding: 15px;
}
.tech-footer {
  padding: 10px 15px;
  background-color: #121822;
  font-size: 0.9em;
  border-top: 1px solid #00CFFD;
  text-align: center;
}
</style>
"""
    
    # Preparar a nova seção com design mais tecnológico
    nova_secao = f"""## ⚡ Analytics 3D Premium - Contribuições GitHub

<div align="center">

### 📊 Visualização Avançada de Atividade

[![Contribuições]({badges['contribuicoes']})](https://github.com/{estatisticas['usuario']})
[![Sequência Atual]({badges['sequencia']})](https://github.com/{estatisticas['usuario']})
[![Pull Requests]({badges['pull_requests']})](https://github.com/{estatisticas['usuario']}?tab=repositories)
[![Issues]({badges['issues']})](https://github.com/{estatisticas['usuario']}?tab=repositories)

</div>

<table>
<tr>
<td width="60%">
<img src="{github_gif_url}" alt="Visualização 3D Tech de Contribuições" width="100%" />
<p align="center"><em>🔄 Visualização 3D Avançada - Tecnologia BeOnSafe</em></p>
</td>
<td width="40%" style="background-color:#0A0E17; color:#E2E8F0;">
<h4 style="color:#00CFFD;">⚡ MÉTRICAS DE DESEMPENHO</h4>
<ul>
<li><b>Total de Contribuições:</b> {estatisticas['total_contribuicoes']}</li>
<li><b>Média Diária:</b> {estatisticas['media_diaria']:.1f}</li>
<li><b>Dias Ativos:</b> {estatisticas['dias_ativos']} ({estatisticas['taxa_atividade']:.1f}%)</li>
<li><b>Sequência Atual:</b> {estatisticas['sequencia_atual']} dias</li>
<li><b>Sequência Máxima:</b> {estatisticas['sequencia_maxima']} dias</li>
<li><b>Dia Mais Produtivo:</b> {estatisticas['melhor_dia']}</li>
<li><b>Score de Intensidade:</b> {estatisticas.get('score_intensidade', 0):.1f}%</li>
</ul>
"""
    
    # Adicionar informações de repositórios, se disponíveis
    if estatisticas["repositorios"]:
        nova_secao += f"""
<h4 style="color:#00FFC6;">🔹 PRINCIPAIS REPOSITÓRIOS</h4>
<ul>
"""
        for repo in estatisticas["repositorios"][:3]:  # Mostrar apenas os 3 principais
            nova_secao += f"<li>{repo}</li>\n"
        nova_secao += "</ul>\n"
    
    # Adicionar links
    nova_secao += f"""
<p><a href="{github_html_url}" style="color:#7B61FF;"><b>📊 VERSÃO INTERATIVA</b></a> <em>(Atualizado em {data_atual})</em></p>
<p><a href="https://github.com/{github_username}/git3d" style="color:#00FFC6;"><b>⚙️ CÓDIGO FONTE</b></a> | <a href="https://github.com/{github_username}/git3d/blob/main/README_GIT3D.md" style="color:#00FFC6;"><b>📖 DOCUMENTAÇÃO</b></a></p>
</td>
</tr>
</table>

<div align="center">
<p><b style="color:#00CFFD;">POWERED BY <a href="https://beonsafe.com.br">BEONSAFE</a></b> | Tecnologia Avançada de Visualização</p>
</div>

---"""
    
    # Verificar se existe a seção para substituir
    if re.search(padrao_viz_3d, conteudo, re.DOTALL):
        # Substituir a seção existente
        novo_conteudo = re.sub(padrao_viz_3d, nova_secao, conteudo, flags=re.DOTALL)
        logger.info("✅ Seção existente de visualização 3D substituída")
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
        logger.info("✅ Nova seção de visualização 3D premium adicionada")
    
    # Escrever o novo conteúdo
    with open(caminho_readme, 'w', encoding='utf-8') as f:
        f.write(novo_conteudo)
    
    logger.info(f"✅ README atualizado com sucesso em {caminho_readme}")
    return True

if __name__ == "__main__":
    # Caminhos para os arquivos
    caminho_readme = "./README.md"  # README na pasta raiz do projeto
    caminho_gif = "images/github_3d_beonsafe.gif"
    caminho_html = "images/github_3d_beonsafe.html"
    
    logger.info("🔄 Iniciando atualização do README com visualização 3D premium")
    sucesso = atualizar_readme(caminho_readme, caminho_gif, caminho_html)
    
    if sucesso:
        logger.info("🎉 README atualizado com sucesso!")
    else:
        logger.error("❌ Houve um problema ao atualizar o README")
        sys.exit(1) 