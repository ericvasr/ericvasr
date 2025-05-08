import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import imageio

# Criar diretório para imagens
os.makedirs("images", exist_ok=True)

# Gerar dados de contribuição fictícios
hoje = datetime.now()
datas = [(hoje - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(365)]
datas.reverse()  # Do mais antigo para o mais recente

# Gerar valores de contribuição aleatórios com mais atividade nos dias de semana
weekdays = [(hoje - timedelta(days=i)).weekday() for i in range(365)]
weekdays.reverse()

contribuicoes = []
for dia in weekdays:
    # Mais contribuições durante a semana, menos nos fins de semana
    if dia < 5:  # Segunda a sexta
        contrib = np.random.randint(0, 10)
    else:  # Fins de semana
        contrib = np.random.randint(0, 3)
    contribuicoes.append(contrib)

# Criar DataFrame
df = pd.DataFrame({
    'date': datas,
    'contributionCount': contribuicoes,
    'weekday': [datetime.strptime(d, "%Y-%m-%d").weekday() for d in datas]
})

df['date'] = pd.to_datetime(df['date'])

# Criar uma matriz para visualização
# Determina o número de semanas
earliest_date = df['date'].min()
latest_date = df['date'].max()

# Determina o número de semanas
total_days = (latest_date - earliest_date).days + 1
total_weeks = (total_days // 7) + 1

# Inicializa matriz (semana, dia da semana, contribuições)
contribution_matrix = np.zeros((total_weeks, 7))

# Preenche a matriz
for _, row in df.iterrows():
    day_of_week = row['weekday']
    week_num = (row['date'] - earliest_date).days // 7
    contribution_matrix[week_num, day_of_week] = row['contributionCount']

# Criar visualização com matplotlib
print("Gerando visualização simples...")

# Criar GIF
frames = []
for angle in range(0, 360, 10):
    # Criar gráfico 3D
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Preparar dados para o gráfico
    weeks = np.arange(total_weeks)
    days = np.arange(7)
    week_grid, day_grid = np.meshgrid(weeks, days, indexing='ij')
    
    # Criar superfície 3D
    surf = ax.plot_surface(
        week_grid, day_grid, contribution_matrix,
        cmap='viridis',
        linewidth=0,
        antialiased=False
    )
    
    # Configurar labels e título
    ax.set_xlabel('Semanas')
    ax.set_ylabel('Dias da Semana')
    ax.set_zlabel('Contribuições')
    dias_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
    ax.set_yticks(range(7))
    ax.set_yticklabels(dias_semana)
    
    # Ajustar ângulo de visualização
    ax.view_init(elev=30, azim=angle)
    
    # Adicionar título e marca d'água
    ax.set_title('Contribuições do GitHub - BeOnSafe', fontsize=16)
    fig.text(0.82, 0.05, 'Powered by BeOnSafe', fontsize=12, color='gray')
    
    # Salvar frame
    filename = f'images/frame_{angle:03d}.png'
    plt.savefig(filename, dpi=80)
    frames.append(imageio.imread(filename))
    plt.close()

# Criar GIF
print("Gerando GIF animado...")
imageio.mimsave('images/github_3d_beonsafe.gif', frames, fps=10)

# Criar HTML simples
html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualização 3D de Contribuições - BeOnSafe</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f8fa;
            color: #333;
        }}
        h1, h2 {{
            color: #0066CC;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .animation {{
            text-align: center;
            margin: 20px 0;
        }}
        .stats {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin: 20px 0;
        }}
        .stat-box {{
            background-color: #E6F2FF;
            border: 1px solid #0066CC;
            border-radius: 8px;
            padding: 15px;
            width: 20%;
            margin-bottom: 10px;
            text-align: center;
        }}
        .stat-box h3 {{
            color: #0066CC;
            margin-top: 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Visualização 3D de Contribuições GitHub</h1>
        <p>Visualize sua atividade no GitHub com uma representação 3D interativa e moderna.</p>
        
        <div class="animation">
            <img src="github_3d_beonsafe.gif" alt="Visualização 3D de Contribuições" width="800">
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>Total</h3>
                <p>{sum(contribuicoes)}</p>
            </div>
            <div class="stat-box">
                <h3>Média Diária</h3>
                <p>{sum(contribuicoes)/len(contribuicoes):.1f}</p>
            </div>
            <div class="stat-box">
                <h3>Dias Ativos</h3>
                <p>{sum(1 for c in contribuicoes if c > 0)}</p>
            </div>
            <div class="stat-box">
                <h3>Melhor Dia</h3>
                <p>{max(contribuicoes)} contribuições</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Atualizado em {datetime.now().strftime('%d/%m/%Y')} | Powered by BeOnSafe</p>
        <p>📬 <a href="mailto:eric@beonsafe.com.br">eric@beonsafe.com.br</a></p>
    </div>
</body>
</html>
"""

with open("images/github_3d_beonsafe.html", "w") as f:
    f.write(html_content)

# Limpar frames temporários
for angle in range(0, 360, 10):
    os.remove(f'images/frame_{angle:03d}.png')

print("✅ Visualizações simples criadas com sucesso:")
print("  - images/github_3d_beonsafe.gif (GIF animado)")
print("  - images/github_3d_beonsafe.html (Versão HTML)")
print("\nAgora você pode fazer commit desses arquivos para seu repositório GitHub.") 