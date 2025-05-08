import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import os
from plotly.subplots import make_subplots
import plotly.express as px
import math
import plotly.io as pio

# Configurações para vídeos e animações
pio.renderers.default = "browser"

# Carrega os dados de contribuições
df = pd.read_csv('contrib_data.csv')
df['date'] = pd.to_datetime(df['date'])

# Extrai o nome de usuário
USERNAME = "ericvasr"

# Cores da identidade visual BeOnSafe
BEONSAFE_COLORS = {
    'primary': '#0066CC',    # Azul principal
    'secondary': '#00AAFF',  # Azul secundário
    'accent': '#FF6600',     # Laranja como acento
    'dark': '#003366',       # Azul escuro
    'light': '#E6F2FF',      # Azul claro
    'text': '#333333',       # Texto escuro
    'background': '#FFFFFF'  # Fundo branco
}

# Personalização da colorscale do plotly para BeOnSafe
beonsafe_colorscale = [
    [0.0, BEONSAFE_COLORS['light']],
    [0.2, '#CCE6FF'],
    [0.4, BEONSAFE_COLORS['secondary']],
    [0.6, '#0088CC'],
    [0.8, BEONSAFE_COLORS['primary']],
    [1.0, BEONSAFE_COLORS['dark']]
]

# Processamento para visualização 3D
earliest_date = df['date'].min()
latest_date = df['date'].max()

# Determina o número de semanas
total_days = (latest_date - earliest_date).days + 1
total_weeks = (total_days // 7) + 1

# Inicializa matriz 3D (semana, dia da semana, contribuições)
contribution_matrix = np.zeros((total_weeks, 7))

# Preenche a matriz e computa estatísticas
total_contributions = 0
max_contributions_day = 0
day_with_most = None

for _, row in df.iterrows():
    day_of_week = row['weekday']
    week_num = (row['date'] - earliest_date).days // 7
    contribution_matrix[week_num, day_of_week] = row['contributionCount']
    total_contributions += row['contributionCount']
    
    if row['contributionCount'] > max_contributions_day:
        max_contributions_day = row['contributionCount']
        day_with_most = row['date']

# Informações para o dashboard
avg_daily = total_contributions / len(df)
active_days = (df['contributionCount'] > 0).sum()
streak = 0
current_streak = 0

# Calcula sequência de contribuições
sorted_df = df.sort_values('date')
for _, row in sorted_df.iterrows():
    if row['contributionCount'] > 0:
        current_streak += 1
    else:
        current_streak = 0
    
    streak = max(streak, current_streak)

# Cria coordenadas para o gráfico 3D
weeks = np.arange(total_weeks)
days = np.arange(7)
week_grid, day_grid = np.meshgrid(weeks, days, indexing='ij')

# Prepara dados para o gráfico 3D
z_values = contribution_matrix
max_contribution = z_values.max()

# ============= CRIA DASHBOARD COM MÚLTIPLOS GRÁFICOS =============
# Cria subplot com 1 linha e 1 coluna para o gráfico 3D principal
fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'surface'}]])

# Adiciona o gráfico de superfície 3D
surface = go.Surface(
    z=z_values,
    x=week_grid,
    y=day_grid,
    colorscale=beonsafe_colorscale,
    colorbar=dict(
        title=dict(
            text="Contribuições",
            font=dict(size=14, family="Arial", color=BEONSAFE_COLORS['text'])
        ),
        tickfont=dict(size=12, family="Arial", color=BEONSAFE_COLORS['text'])
    ),
    lighting=dict(
        ambient=0.6,
        diffuse=0.9,
        roughness=0.3,
        specular=0.8,
        fresnel=0.2
    ),
    contours=dict(
        z=dict(
            show=True,
            width=1.5,
            color="white",
            highlightcolor="white"
        )
    ),
    hoverinfo='all',
    hovertemplate=
    '<b>Semana</b>: %{x}<br>' +
    '<b>Dia</b>: %{y}<br>' +
    '<b>Contribuições</b>: %{z}<br>' +
    '<extra></extra>'
)

fig.add_trace(surface)

# Configura o layout 
dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

fig.update_layout(
    title=dict(
        text=f"Visualização 3D do GitHub - {USERNAME}",
        font=dict(
            family="Arial Black",
            size=24,
            color=BEONSAFE_COLORS['primary']
        ),
        x=0.5,
        y=0.95
    ),
    autosize=True,
    width=1400,
    height=900,
    paper_bgcolor=BEONSAFE_COLORS['background'],
    plot_bgcolor=BEONSAFE_COLORS['background'],
    scene=dict(
        xaxis=dict(
            title=dict(
                text="Semanas",
                font=dict(family="Arial", size=14, color=BEONSAFE_COLORS['text'])
            ),
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor=BEONSAFE_COLORS['light'],
            zerolinecolor=BEONSAFE_COLORS['primary']
        ),
        yaxis=dict(
            title=dict(
                text="Dias da Semana",
                font=dict(family="Arial", size=14, color=BEONSAFE_COLORS['text'])
            ),
            ticktext=dias_semana,
            tickvals=list(range(7)),
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor=BEONSAFE_COLORS['light'],
            zerolinecolor=BEONSAFE_COLORS['primary']
        ),
        zaxis=dict(
            title=dict(
                text="Contribuições",
                font=dict(family="Arial", size=14, color=BEONSAFE_COLORS['text'])
            ),
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor=BEONSAFE_COLORS['light'],
            zerolinecolor=BEONSAFE_COLORS['primary']
        ),
        camera=dict(
            eye=dict(x=1.5, y=-1.5, z=0.8)
        ),
        aspectmode='manual',
        aspectratio=dict(x=2, y=1, z=0.7)
    ),
    margin=dict(l=30, r=30, b=50, t=100)
)

# Adicionar logo e informações
data_atual = datetime.now().strftime("%d/%m/%Y")

# Adicionar estatísticas na parte inferior
stats_text = (
    f"<b>Total de Contribuições:</b> {total_contributions} | "
    f"<b>Média Diária:</b> {avg_daily:.1f} | "
    f"<b>Dias Ativos:</b> {active_days} | "
    f"<b>Sequência Máxima:</b> {streak} dias"
)

fig.add_annotation(
    text=stats_text,
    x=0.5,
    y=0.02,
    xref="paper",
    yref="paper",
    showarrow=False,
    font=dict(
        family="Arial",
        size=14,
        color=BEONSAFE_COLORS['primary']
    ),
    align="center",
    bgcolor=BEONSAFE_COLORS['light'],
    bordercolor=BEONSAFE_COLORS['primary'],
    borderwidth=1,
    borderpad=6
)

# Adicionar assinatura BeOnSafe
fig.add_annotation(
    text="Powered by <b>BeOnSafe</b>",
    x=0.98,
    y=0.04,
    xref="paper",
    yref="paper",
    showarrow=False,
    font=dict(
        family="Arial",
        size=14,
        color=BEONSAFE_COLORS['accent']
    ),
    align="right"
)

# Adicionar data de geração
fig.add_annotation(
    text=f"Gerado em {data_atual}",
    x=0.02,
    y=0.04,
    xref="paper",
    yref="paper",
    showarrow=False,
    font=dict(
        family="Arial",
        size=12,
        color=BEONSAFE_COLORS['text']
    ),
    align="left"
)

# Criar diretório para as imagens se não existir
if not os.path.exists('images'):
    os.makedirs('images')

# Salvar versão HTML interativa
fig.write_html("images/github_3d_beonsafe.html")

# Salvar imagem estática em alta resolução
fig.write_image("images/github_3d_beonsafe.png", scale=2)

# Criar versão animada com rotação
frames = []
for i in range(0, 360, 5):
    camera = dict(
        eye=dict(
            x=1.5 * np.cos(np.radians(i)),
            y=1.5 * np.sin(np.radians(i)),
            z=0.8
        )
    )
    frames.append(go.Frame(layout=dict(scene_camera=camera)))

animated_fig = go.Figure(
    data=fig.data,
    layout=fig.layout,
    frames=frames
)

animated_fig.update_layout(
    updatemenus=[{
        "type": "buttons",
        "buttons": [{
            "label": "Animar",
            "method": "animate",
            "args": [None, {"frame": {"duration": 30, "redraw": True}, "fromcurrent": True}]
        }],
        "direction": "left",
        "showactive": False,
        "x": 0.1,
        "y": 0,
        "xanchor": "right"
    }]
)

animated_fig.write_html("images/github_3d_beonsafe_animated.html")

# Criar GIF para o README
try:
    import kaleido
    import imageio
    
    print("Gerando sequência de imagens para GIF...")
    frames_gif = []
    
    for i in range(0, 360, 10):
        camera = dict(
            eye=dict(
                x=1.5 * np.cos(np.radians(i)),
                y=1.5 * np.sin(np.radians(i)),
                z=0.8
            )
        )
        temp_fig = go.Figure(data=fig.data, layout=fig.layout)
        temp_fig.update_layout(scene_camera=camera)
        
        # Cria diretório temporário para os frames
        if not os.path.exists('temp_frames'):
            os.makedirs('temp_frames')
            
        temp_file = f"temp_frames/frame_{i:03d}.png"
        temp_fig.write_image(temp_file, scale=1)
        frames_gif.append(temp_file)
    
    # Cria o GIF
    print("Criando GIF animado...")
    images = [imageio.imread(frame) for frame in frames_gif]
    imageio.mimsave("images/github_3d_beonsafe.gif", images, fps=10)
    
    # Limpa arquivos temporários
    for frame in frames_gif:
        os.remove(frame)
    os.rmdir("temp_frames")
    
    print("✅ GIF animado criado em images/github_3d_beonsafe.gif")
except ImportError:
    print("⚠️ Pacotes kaleido ou imageio não encontrados. GIF não foi gerado.")
    print("   Para gerar GIFs, instale: pip install kaleido imageio")
except Exception as e:
    print(f"⚠️ Erro ao gerar GIF: {str(e)}")
    print("   O GIF não foi gerado, mas as outras visualizações estão disponíveis")

print("\n✅ Visualizações 3D do BeOnSafe criadas em:")
print("  - images/github_3d_beonsafe.html (versão interativa)")
print("  - images/github_3d_beonsafe.png (imagem estática)")
print("  - images/github_3d_beonsafe_animated.html (versão animada)")

print("\n🔍 Estatísticas do usuário:")
print(f"  - Total de Contribuições: {total_contributions}")
print(f"  - Média Diária: {avg_daily:.1f}")
print(f"  - Dias Ativos: {active_days}")
print(f"  - Sequência Máxima: {streak} dias")
print(f"  - Dia com mais contribuições: {day_with_most.strftime('%d/%m/%Y')} ({max_contributions_day})") 