import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import os
from plotly.subplots import make_subplots
import plotly.express as px
import math
import plotly.io as pio
import colorsys
import json
import logging
import sys

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('git3d_renderer')

# Configurações para vídeos e animações
pio.renderers.default = "browser"

# Carrega os dados de contribuições
try:
    df = pd.read_csv('contrib_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    logger.info(f"✅ Dados carregados com sucesso. {len(df)} dias encontrados.")
except Exception as e:
    logger.error(f"❌ Erro ao carregar dados: {str(e)}")
    sys.exit(1)

# Extrai o nome de usuário
USERNAME = "ericvasr"
logger.info(f"🧑‍💻 Gerando visualização para usuário: {USERNAME}")

# Paleta de cores profissional BeOnSafe
BEONSAFE_COLORS = {
    'primary': '#005CB8',       # Azul principal mais intenso
    'secondary': '#00A4FF',     # Azul secundário mais vibrante
    'accent': '#FF5500',        # Laranja mais vibrante
    'dark': '#002E5C',          # Azul escuro mais profundo
    'light': '#E1F0FF',         # Azul claro
    'text': '#1A1A1A',          # Texto quase preto
    'background': '#FFFFFF',    # Fundo branco
    'highlight': '#FFCC00',     # Amarelo de destaque
    'gradient1': '#004080',     # Gradiente escuro
    'gradient2': '#0080FF',     # Gradiente médio
    'gradient3': '#80BFFF',     # Gradiente claro
    'success': '#00CC66',       # Verde sucesso
    'warning': '#FFC107',       # Amarelo alerta
    'dark_edge': '#001F3D'      # Azul escuro para bordas
}

# Gerar uma paleta de cores personalizada melhorada para as contribuições
def generate_professional_colorscale(colors_dict, steps=10):
    base_colors = [
        colors_dict['dark_edge'],
        colors_dict['gradient1'],
        colors_dict['primary'],
        colors_dict['secondary'],
        colors_dict['gradient3'],
        colors_dict['highlight']
    ]
    
    colorscale = []
    for i, color in enumerate(base_colors):
        position = i / (len(base_colors) - 1)
        colorscale.append([position, color])
    
    return colorscale

# Colorscale profissional
beonsafe_colorscale = generate_professional_colorscale(BEONSAFE_COLORS)

# Processamento para visualização 3D
earliest_date = df['date'].min()
latest_date = df['date'].max()

# Determina o número de semanas
total_days = (latest_date - earliest_date).days + 1
total_weeks = (total_days // 7) + 1

# Inicializa matriz 3D (semana, dia da semana, contribuições)
contribution_matrix = np.zeros((total_weeks, 7))

# Estatísticas avançadas
total_contributions = 0
max_contributions_day = 0
max_contributions_week = 0
day_with_most = None
weekly_totals = []
daily_totals = [0] * 7  # Para cada dia da semana
monthly_totals = {}

# Preenche a matriz e computa estatísticas avançadas
for _, row in df.iterrows():
    day_of_week = row['weekday']
    week_num = (row['date'] - earliest_date).days // 7
    contrib_count = row['contributionCount']
    
    # Preencher matriz
    contribution_matrix[week_num, day_of_week] = contrib_count
    
    # Atualizar estatísticas
    total_contributions += contrib_count
    daily_totals[day_of_week] += contrib_count
    
    # Rastrear contribuição por mês
    month_key = row['date'].strftime('%Y-%m')
    if month_key not in monthly_totals:
        monthly_totals[month_key] = 0
    monthly_totals[month_key] += contrib_count
    
    # Verificar máximos
    if contrib_count > max_contributions_day:
        max_contributions_day = contrib_count
        day_with_most = row['date']

# Calcular totais semanais
for week in range(total_weeks):
    weekly_total = np.sum(contribution_matrix[week, :])
    weekly_totals.append(weekly_total)
    max_contributions_week = max(max_contributions_week, weekly_total)

# Encontrar dia da semana com mais contribuições
best_day_index = np.argmax(daily_totals)
dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
best_day_name = dias_semana[best_day_index]

# Métricas avançadas
avg_daily = total_contributions / len(df)
active_days = (df['contributionCount'] > 0).sum()
inactive_days = len(df) - active_days
activity_rate = (active_days / len(df)) * 100
period_length = (latest_date - earliest_date).days + 1
avg_weekly = total_contributions / (total_weeks if total_weeks > 0 else 1)

# Calcular sequências
streak = 0
current_streak = 0
max_streak_start = None
max_streak_end = None
current_streak_start = None

# Ordena por data para calcular sequências corretamente
sorted_df = df.sort_values('date')
for i, row in sorted_df.iterrows():
    if row['contributionCount'] > 0:
        if current_streak == 0:
            current_streak_start = row['date']
        current_streak += 1
    else:
        if current_streak > streak:
            streak = current_streak
            max_streak_start = current_streak_start
            max_streak_end = sorted_df.iloc[i-1]['date'] if i > 0 else None
        current_streak = 0
        current_streak_start = None

# Verificar se atual sequência é a máxima
if current_streak > streak:
    streak = current_streak
    max_streak_start = current_streak_start
    max_streak_end = sorted_df.iloc[-1]['date']

# Verificar sequência atual
current_streak = 0
for i in range(len(sorted_df)-1, -1, -1):
    if sorted_df.iloc[i]['contributionCount'] > 0:
        current_streak += 1
    else:
        break

# Computar métricas de intensidade
high_activity_days = (df['contributionCount'] >= 5).sum()
intensity_score = (high_activity_days / active_days * 100) if active_days > 0 else 0

# Cria coordenadas para o gráfico 3D
weeks = np.arange(total_weeks)
days = np.arange(7)
week_grid, day_grid = np.meshgrid(weeks, days, indexing='ij')

# Prepara dados para o gráfico 3D
z_values = contribution_matrix
max_contribution = z_values.max()

# Adicionar textura e profundidade à visualização
def add_surface_texture(z_values):
    # Criar cópia para não modificar os dados originais
    textured_z = np.copy(z_values)
    
    # Adicionar pequenas variações para textura adicional em células vazias
    for i in range(textured_z.shape[0]):
        for j in range(textured_z.shape[1]):
            # Se for zero, adicionar um valor muito pequeno para textura
            if textured_z[i, j] == 0:
                textured_z[i, j] = np.random.uniform(0.01, 0.05)
    
    return textured_z

# Aplicar textura
textured_z = add_surface_texture(z_values)

# ============= CRIA DASHBOARD PROFISSIONAL COM MÚLTIPLOS GRÁFICOS =============
# Criar uma figura com subplots para um dashboard completo
fig = make_subplots(
    rows=1, cols=1, 
    specs=[[{'type': 'surface'}]],
    subplot_titles=[f"<b>Contribuições 3D do GitHub - {USERNAME}</b>"]
)

# Adiciona o gráfico de superfície 3D com efeitos avançados
surface = go.Surface(
    z=z_values,
    x=week_grid,
    y=day_grid,
    colorscale=beonsafe_colorscale,
    colorbar=dict(
        title=dict(
            text="Contribuições",
            font=dict(
                size=14, 
                family="Arial", 
                color=BEONSAFE_COLORS['dark']
            )
        ),
        tickfont=dict(
            size=12, 
            family="Arial", 
            color=BEONSAFE_COLORS['dark']
        ),
        len=0.75,
        thickness=20,
        outlinewidth=1,
        outlinecolor=BEONSAFE_COLORS['dark_edge']
    ),
    lighting=dict(
        ambient=0.65,
        diffuse=0.9,
        fresnel=0.25,
        roughness=0.1,
        specular=1.0,
    ),
    contours=dict(
        z=dict(
            show=True,
            width=1.5,
            color="white",
            highlightcolor=BEONSAFE_COLORS['highlight']
        )
    ),
    opacity=0.95,  # Ligeira transparência para efeito profissional
    showscale=True,
    hoverinfo='all',
    hovertemplate=
    '<b>Semana</b>: %{x}<br>' +
    '<b>Dia</b>: %{customdata}<br>' +
    '<b>Contribuições</b>: %{z}<br>' +
    '<extra></extra>',
    customdata=np.array([dias_semana[i] for i in range(7)] * total_weeks).reshape(total_weeks, 7)
)

# Adicionar efeitos de iluminação e profundidade
fig.add_trace(surface)

# Configurar o layout para um design premium
dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

# Adicionar informações de datas aos eixos
date_ticks = {}
for i in range(0, total_weeks, 4):  # A cada 4 semanas
    if i < total_weeks:
        date_value = earliest_date + timedelta(weeks=i)
        date_ticks[i] = date_value.strftime('%d/%m/%y')

fig.update_layout(
    title=dict(
        text=f"<b>Visualização 3D Premium - Contribuições GitHub</b><br><span style='font-size:18px;'>{USERNAME}</span>",
        font=dict(
            family="Montserrat, Arial Black, sans-serif",
            size=26,
            color=BEONSAFE_COLORS['dark']
        ),
        x=0.5,
        y=0.97
    ),
    autosize=True,
    width=1500,
    height=950,
    paper_bgcolor=BEONSAFE_COLORS['background'],
    plot_bgcolor=BEONSAFE_COLORS['background'],
    scene=dict(
        xaxis=dict(
            title=dict(
                text="Semanas",
                font=dict(family="Arial", size=14, color=BEONSAFE_COLORS['dark'])
            ),
            tickvals=list(date_ticks.keys()),
            ticktext=list(date_ticks.values()),
            gridcolor="#E5E5E5",
            showbackground=True,
            backgroundcolor=BEONSAFE_COLORS['light'],
            zerolinecolor=BEONSAFE_COLORS['primary'],
            showspikes=False
        ),
        yaxis=dict(
            title=dict(
                text="Dias da Semana",
                font=dict(family="Arial", size=14, color=BEONSAFE_COLORS['dark'])
            ),
            ticktext=dias_semana,
            tickvals=list(range(7)),
            gridcolor="#E5E5E5",
            showbackground=True,
            backgroundcolor=BEONSAFE_COLORS['light'],
            zerolinecolor=BEONSAFE_COLORS['primary'],
            showspikes=False
        ),
        zaxis=dict(
            title=dict(
                text="Contribuições",
                font=dict(family="Arial", size=14, color=BEONSAFE_COLORS['dark'])
            ),
            gridcolor="#E5E5E5",
            showbackground=True,
            backgroundcolor=BEONSAFE_COLORS['light'],
            zerolinecolor=BEONSAFE_COLORS['primary'],
            showspikes=False
        ),
        camera=dict(
            eye=dict(x=1.7, y=-1.7, z=0.9),
            center=dict(x=0, y=0, z=-0.15)  # Ajuste para melhor visualização
        ),
        aspectmode='manual',
        aspectratio=dict(x=2, y=1, z=0.7)
    ),
    margin=dict(l=10, r=10, b=10, t=80),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.05,
        xanchor="center",
        x=0.5,
        font=dict(size=14, color=BEONSAFE_COLORS['dark'])
    ),
)

# Adicionar informações e estatísticas avançadas
data_atual = datetime.now().strftime("%d/%m/%Y")

# Card de estatísticas avançadas
stats_html = f"""
<div style='font-family:Arial; padding:12px; background-color:{BEONSAFE_COLORS['light']}; 
     border:1px solid {BEONSAFE_COLORS['primary']}; border-radius:8px;'>
  <span style='font-weight:bold; color:{BEONSAFE_COLORS['dark']}; font-size:16px;'>🌟 Métricas de Desempenho:</span><br>
  <span style='color:{BEONSAFE_COLORS['dark']}; font-size:14px;'>
    <b>Total:</b> {total_contributions} contribuições | 
    <b>Média:</b> {avg_daily:.1f} por dia | 
    <b>Taxa de Atividade:</b> {activity_rate:.1f}%<br>
    <b>Sequência Atual:</b> {current_streak} dias | 
    <b>Sequência Máxima:</b> {streak} dias | 
    <b>Dia Mais Produtivo:</b> {best_day_name}
  </span>
</div>
"""

fig.add_annotation(
    text=stats_html,
    x=0.5,
    y=0.01,
    xref="paper",
    yref="paper",
    showarrow=False,
    align="center",
)

# Adicionar uma borda profissional ao redor de toda a visualização
fig.update_layout(
    shapes=[
        # Borda externa
        dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0=0,
            y0=0,
            x1=1,
            y1=1,
            line=dict(
                color=BEONSAFE_COLORS['dark_edge'],
                width=2,
            ),
            layer="below"
        )
    ]
)

# Adicionar logo e marca d'água premium BeOnSafe
fig.add_annotation(
    text="<b>Powered by BeOnSafe</b> | Premium Visualization",
    x=0.99,
    y=0.03,
    xref="paper",
    yref="paper",
    showarrow=False,
    font=dict(
        family="Arial",
        size=14,
        color=BEONSAFE_COLORS['accent']
    ),
    align="right",
    bgcolor="rgba(255, 255, 255, 0.8)",
    bordercolor=BEONSAFE_COLORS['dark_edge'],
    borderwidth=1,
    borderpad=4,
    opacity=0.9
)

# Adicionar data de geração
fig.add_annotation(
    text=f"<b>Atualizado em</b> {data_atual}",
    x=0.01,
    y=0.03,
    xref="paper",
    yref="paper",
    showarrow=False,
    font=dict(
        family="Arial",
        size=14,
        color=BEONSAFE_COLORS['dark']
    ),
    align="left",
    bgcolor="rgba(255, 255, 255, 0.8)",
    bordercolor=BEONSAFE_COLORS['dark_edge'],
    borderwidth=1,
    borderpad=4,
    opacity=0.9
)

# Criar diretório para as imagens se não existir
if not os.path.exists('images'):
    os.makedirs('images')
    logger.info("✅ Diretório de imagens criado")

# Salvar metadados para uso em outras visualizações
metadata = {
    "username": USERNAME,
    "total_contributions": total_contributions,
    "avg_daily": avg_daily,
    "active_days": int(active_days),
    "max_streak": int(streak),
    "current_streak": int(current_streak),
    "best_day": best_day_name,
    "best_day_index": int(best_day_index),
    "max_contributions_day": int(max_contributions_day),
    "max_contributions_week": int(max_contributions_week),
    "activity_rate": float(activity_rate),
    "intensity_score": float(intensity_score),
    "date_generated": data_atual
}

with open("images/github_stats.json", "w") as f:
    json.dump(metadata, f, indent=2)
    logger.info("✅ Metadados salvos para uso em outras visualizações")

# Salvar versão HTML interativa premium
fig.write_html("images/github_3d_beonsafe.html", include_plotlyjs="cdn")
logger.info("✅ Visualização HTML interativa salva")

# Salvar imagem estática em alta resolução
fig.write_image("images/github_3d_beonsafe.png", scale=3, engine="kaleido")
logger.info("✅ Imagem estática de alta resolução salva")

# Configurações para animação premium
frames = []
for i in range(0, 360, 3):  # Movimento mais suave com mais frames
    angle_rad = np.radians(i)
    camera = dict(
        eye=dict(
            x=1.8 * np.cos(angle_rad),
            y=1.8 * np.sin(angle_rad),
            z=0.8 + 0.2 * np.sin(angle_rad/2)  # Movimento de oscilação vertical
        ),
        center=dict(x=0, y=0, z=-0.1 + 0.05 * np.sin(angle_rad/4))  # Movimento suave do centro
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
            "label": "▶️ Animar",
            "method": "animate",
            "args": [None, {"frame": {"duration": 20, "redraw": True}, "fromcurrent": True, "mode": "immediate"}]
        }],
        "direction": "left",
        "showactive": False,
        "x": 0.1,
        "y": 0,
        "xanchor": "right"
    }]
)

animated_fig.write_html("images/github_3d_beonsafe_animated.html", include_plotlyjs="cdn")
logger.info("✅ Visualização HTML animada premium salva")

# Criar GIF de alta qualidade para o README
try:
    import kaleido
    import imageio
    
    logger.info("Gerando sequência de imagens de alta qualidade para GIF...")
    frames_gif = []
    total_frames = 36  # Número de frames para o GIF
    
    # Criar diretório temporário para os frames
    if not os.path.exists('temp_frames'):
        os.makedirs('temp_frames')
    
    for i in range(total_frames):
        angle = i * (360 / total_frames)
        angle_rad = np.radians(angle)
        
        # Câmera com movimento dinâmico
        camera = dict(
            eye=dict(
                x=1.7 * np.cos(angle_rad),
                y=1.7 * np.sin(angle_rad),
                z=0.9 + 0.15 * np.sin(angle_rad/2)
            ),
            center=dict(x=0, y=0, z=-0.15)
        )
        
        temp_fig = go.Figure(data=fig.data, layout=fig.layout)
        temp_fig.update_layout(scene_camera=camera)
        
        # Salvar frame em alta resolução
        temp_file = f"temp_frames/frame_{i:03d}.png"
        temp_fig.write_image(temp_file, scale=2, width=800, height=600)
        frames_gif.append(temp_file)
    
    # Criar o GIF otimizado com melhor qualidade
    logger.info("Criando GIF animado premium...")
    images = [imageio.imread(frame) for frame in frames_gif]
    
    # Usar configurações de alta qualidade para o GIF
    imageio.mimsave(
        "images/github_3d_beonsafe.gif", 
        images, 
        fps=12,
        optimize=True,
        subrectangles=True
    )
    
    # Limpar arquivos temporários
    for frame in frames_gif:
        os.remove(frame)
    os.rmdir("temp_frames")
    
    logger.info("✅ GIF animado premium criado com sucesso")
except ImportError as e:
    logger.warning(f"⚠️ Pacotes necessários não encontrados: {str(e)}")
    logger.warning("   Para gerar GIFs, instale: pip install kaleido imageio")
except Exception as e:
    logger.error(f"❌ Erro ao gerar GIF: {str(e)}")
    logger.error("   O GIF não foi gerado, mas as outras visualizações estão disponíveis")

logger.info("\n✅ Visualizações 3D Premium BeOnSafe criadas com sucesso:")
logger.info("  - images/github_3d_beonsafe.html (versão interativa premium)")
logger.info("  - images/github_3d_beonsafe.png (imagem estática em alta resolução)")
logger.info("  - images/github_3d_beonsafe_animated.html (versão animada avançada)")
logger.info("  - images/github_3d_beonsafe.gif (GIF animado otimizado)")

logger.info("\n🔍 Estatísticas avançadas do usuário:")
logger.info(f"  - Total de Contribuições: {total_contributions}")
logger.info(f"  - Média Diária: {avg_daily:.2f}")
logger.info(f"  - Dias Ativos: {active_days} ({activity_rate:.1f}%)")
logger.info(f"  - Sequência Atual: {current_streak} dias")
logger.info(f"  - Sequência Máxima: {streak} dias")
logger.info(f"  - Melhor Dia da Semana: {best_day_name}")
logger.info(f"  - Dia com mais contribuições: {day_with_most.strftime('%d/%m/%Y')} ({max_contributions_day})")
logger.info(f"  - Score de Intensidade: {intensity_score:.1f}%") 