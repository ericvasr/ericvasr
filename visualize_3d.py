import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os

# Carrega os dados de contribuições
df = pd.read_csv('contrib_data.csv')
df['date'] = pd.to_datetime(df['date'])

# Pega o nome de usuário do arquivo de contribuições
USERNAME = "ericvasr"  # Substitua pelo seu usuário se necessário

# Cria uma matriz para visualização 3D
# Converte datas para uma matriz de semanas x dias da semana
earliest_date = df['date'].min()
latest_date = df['date'].max()

# Determina o número de semanas
total_days = (latest_date - earliest_date).days + 1
total_weeks = (total_days // 7) + 1

# Inicializa matriz 3D (semana, dia da semana, contribuições)
contribution_matrix = np.zeros((total_weeks, 7))

# Preenche a matriz
for _, row in df.iterrows():
    day_of_week = row['weekday']
    week_num = (row['date'] - earliest_date).days // 7
    contribution_matrix[week_num, day_of_week] = row['contributionCount']

# Cria coordenadas para o gráfico 3D
weeks = np.arange(total_weeks)
days = np.arange(7)
week_grid, day_grid = np.meshgrid(weeks, days, indexing='ij')

# Prepara dados para o gráfico 3D
z_values = contribution_matrix
max_contribution = z_values.max()

# Criar visualização 3D com Plotly
fig = go.Figure(data=[
    go.Surface(
        z=z_values,
        x=week_grid,
        y=day_grid,
        colorscale='Viridis',
        colorbar=dict(
            title=dict(
                text="Contribuições"
            )
        ),
        lighting=dict(
            ambient=0.7,
            diffuse=0.8,
            roughness=0.5,
            specular=0.7,
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
])

# Configura o layout
dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

fig.update_layout(
    title=f"Visualização 3D das Contribuições do GitHub - {USERNAME}",
    autosize=True,
    width=1200,
    height=800,
    scene=dict(
        xaxis=dict(
            title="Semanas",
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor="white",
        ),
        yaxis=dict(
            title="Dias da Semana",
            ticktext=dias_semana,
            tickvals=list(range(7)),
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor="white"
        ),
        zaxis=dict(
            title="Contribuições",
            gridcolor="lightgray",
            showbackground=True,
            backgroundcolor="white"
        ),
        camera=dict(
            eye=dict(x=1.5, y=-1.5, z=0.8)
        )
    ),
    margin=dict(l=0, r=0, b=0, t=50),
    scene_aspectmode='manual',
    scene_aspectratio=dict(x=2, y=1, z=0.7)
)

# Adiciona marca d'água e informações
data_atual = datetime.now().strftime("%d/%m/%Y")
fig.add_annotation(
    text=f"BeOnSafe - Criado em {data_atual}",
    x=0.98,
    y=0.02,
    xref="paper",
    yref="paper",
    showarrow=False,
    font=dict(
        family="Arial",
        size=12,
        color="gray"
    ),
    align="right"
)

# Salva a visualização
if not os.path.exists('images'):
    os.makedirs('images')

# Salva como HTML interativo
fig.write_html("images/github_3d_visual.html")

# Salva como imagem estática
fig.write_image("images/github_3d_visual.png", scale=2)

# Opcional: Criar uma versão animada com rotação
frames = []
for i in range(0, 360, 5):
    camera = dict(
        eye=dict(
            x=1.5 * np.cos(np.radians(i)),
            y=1.5 * np.sin(np.radians(i)),
            z=0.8
        )
    )
    fig.update_layout(scene_camera=camera)
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

animated_fig.write_html("images/github_3d_visual_animated.html")

print("✅ Visualizações 3D criadas em:")
print("  - images/github_3d_visual.html (versão interativa)")
print("  - images/github_3d_visual.png (imagem estática)")
print("  - images/github_3d_visual_animated.html (versão animada)") 