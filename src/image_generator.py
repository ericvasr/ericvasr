#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BeOnSafe - Gerador de Imagens Aleatórias
Biblioteca para gerar imagens para testes e desenvolvimento
"""

import os
import random
import logging
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("image_generator")

class ImagemAleatoria:
    """Classe para gerar imagens aleatórias para o BeOnSafe"""
    
    def __init__(self, diretorio_saida="data/images"):
        """Inicializa o gerador de imagens"""
        self.diretorio_saida = diretorio_saida
        self.cores = [
            (66, 134, 244),  # Azul
            (66, 190, 244),  # Azul claro
            (66, 244, 155),  # Verde-água
            (99, 66, 244),   # Roxo
            (165, 66, 244),  # Violeta
            (244, 66, 161),  # Rosa
            (244, 66, 66),   # Vermelho
            (244, 161, 66),  # Laranja
            (194, 244, 66),  # Verde-limão
            (30, 30, 30)     # Preto
        ]
        
        # Cria o diretório de saída se não existir
        os.makedirs(diretorio_saida, exist_ok=True)
        logger.info(f"Gerador de imagens inicializado. Diretório de saída: {diretorio_saida}")
        
    def _gerar_cor_aleatoria(self):
        """Retorna uma cor aleatória do conjunto predefinido"""
        return random.choice(self.cores)
        
    def _gerar_gradiente(self, tamanho, cor1=None, cor2=None):
        """Gera uma imagem com gradiente aleatório"""
        if cor1 is None:
            cor1 = self._gerar_cor_aleatoria()
        if cor2 is None:
            cor2 = self._gerar_cor_aleatoria()
            # Garante que cor2 é diferente de cor1
            while cor2 == cor1:
                cor2 = self._gerar_cor_aleatoria()
                
        # Cria imagem base
        imagem = Image.new('RGB', tamanho, color=cor1)
        draw = ImageDraw.Draw(imagem)
        
        # Decide direção do gradiente
        direcao = random.choice(['horizontal', 'vertical', 'diagonal'])
        
        largura, altura = tamanho
        
        # Desenha o gradiente
        if direcao == 'horizontal':
            for x in range(largura):
                # Calcula a cor para cada coluna
                r = int(cor1[0] + (cor2[0] - cor1[0]) * x / largura)
                g = int(cor1[1] + (cor2[1] - cor1[1]) * x / largura)
                b = int(cor1[2] + (cor2[2] - cor1[2]) * x / largura)
                
                draw.line([(x, 0), (x, altura)], fill=(r, g, b))
                
        elif direcao == 'vertical':
            for y in range(altura):
                # Calcula a cor para cada linha
                r = int(cor1[0] + (cor2[0] - cor1[0]) * y / altura)
                g = int(cor1[1] + (cor2[1] - cor1[1]) * y / altura)
                b = int(cor1[2] + (cor2[2] - cor1[2]) * y / altura)
                
                draw.line([(0, y), (largura, y)], fill=(r, g, b))
                
        else:  # diagonal
            for x in range(largura):
                for y in range(altura):
                    # Calcula a posição relativa no gradiente
                    pos = (x + y) / (largura + altura)
                    
                    r = int(cor1[0] + (cor2[0] - cor1[0]) * pos)
                    g = int(cor1[1] + (cor2[1] - cor1[1]) * pos)
                    b = int(cor1[2] + (cor2[2] - cor1[2]) * pos)
                    
                    draw.point((x, y), fill=(r, g, b))
                    
        return imagem
        
    def _adicionar_texto(self, imagem, texto=None):
        """Adiciona texto à imagem"""
        if texto is None:
            texto = "BeOnSafe"
            
        draw = ImageDraw.Draw(imagem)
        largura, altura = imagem.size
        
        # Tenta usar uma fonte, ou recorre para a fonte padrão
        try:
            # Tamanho da fonte proporcional à imagem
            tamanho_fonte = int(min(largura, altura) / 10)
            fonte = ImageFont.truetype("arial.ttf", tamanho_fonte)
        except IOError:
            # Usa fonte padrão se arial não estiver disponível
            fonte = ImageFont.load_default()
            
        # Obtém tamanho do texto para centralizar
        try:
            bbox = draw.textbbox((0, 0), texto, font=fonte)
            texto_largura = bbox[2] - bbox[0]
            texto_altura = bbox[3] - bbox[1]
        except AttributeError:
            # Fallback para versões mais antigas do PIL
            texto_largura, texto_altura = draw.textsize(texto, font=fonte)
            
        # Posição centralizada
        posicao_x = (largura - texto_largura) // 2
        posicao_y = (altura - texto_altura) // 2
        
        # Desenha sombra para melhorar legibilidade
        draw.text((posicao_x+2, posicao_y+2), texto, font=fonte, fill=(0, 0, 0, 128))
        # Desenha texto
        draw.text((posicao_x, posicao_y), texto, font=fonte, fill=(255, 255, 255, 255))
        
        return imagem
        
    def gerar_avatar(self, tamanho=(200, 200), texto=None):
        """Gera um avatar aleatório"""
        # Gera base com gradiente
        imagem = self._gerar_gradiente(tamanho)
        
        # Adiciona formas geométricas aleatórias
        draw = ImageDraw.Draw(imagem)
        largura, altura = tamanho
        
        # Adiciona algumas formas aleatórias
        for _ in range(random.randint(2, 5)):
            forma = random.choice(['círculo', 'retângulo', 'linha'])
            cor = self._gerar_cor_aleatoria()
            
            if forma == 'círculo':
                raio = random.randint(10, min(largura, altura) // 4)
                centro_x = random.randint(0, largura)
                centro_y = random.randint(0, altura)
                draw.ellipse(
                    [(centro_x - raio, centro_y - raio), 
                     (centro_x + raio, centro_y + raio)], 
                    fill=cor
                )
                
            elif forma == 'retângulo':
                x1 = random.randint(0, largura - 10)
                y1 = random.randint(0, altura - 10)
                x2 = random.randint(x1 + 10, largura)
                y2 = random.randint(y1 + 10, altura)
                draw.rectangle([(x1, y1), (x2, y2)], fill=cor)
                
            else:  # linha
                x1 = random.randint(0, largura)
                y1 = random.randint(0, altura)
                x2 = random.randint(0, largura)
                y2 = random.randint(0, altura)
                espessura = random.randint(1, 8)
                draw.line([(x1, y1), (x2, y2)], fill=cor, width=espessura)
        
        # Aplica filtro de desfoque para suavizar
        imagem = imagem.filter(ImageFilter.GaussianBlur(radius=1.5))
        
        # Adiciona texto se fornecido
        if texto:
            imagem = self._adicionar_texto(imagem, texto)
            
        # Torna a imagem circular (para avatar)
        mascara = Image.new('L', tamanho, 0)
        mascara_draw = ImageDraw.Draw(mascara)
        mascara_draw.ellipse((0, 0) + tamanho, fill=255)
        
        # Aplica a máscara para criar imagem circular
        imagem_circular = Image.new('RGBA', tamanho, (0, 0, 0, 0))
        imagem_circular.paste(imagem, (0, 0), mascara)
        
        return imagem_circular
    
    def gerar_imagem_imovel(self, tamanho=(800, 600), descricao=None):
        """Gera uma imagem aleatória de imóvel para testes"""
        # Estilo mais adequado para imóveis
        cor1 = (66, 134, 244)  # Azul
        cor2 = (255, 255, 255)  # Branco
        
        # Gera base com gradiente suave
        imagem = self._gerar_gradiente(tamanho, cor1, cor2)
        draw = ImageDraw.Draw(imagem)
        largura, altura = tamanho
        
        # Desenha uma casa esquemática
        # Retângulo para a base da casa
        base_largura = largura // 2
        base_altura = altura // 2
        base_x = (largura - base_largura) // 2
        base_y = altura - base_altura - altura // 10
        
        draw.rectangle(
            [(base_x, base_y), (base_x + base_largura, base_y + base_altura)],
            fill=(180, 180, 180),
            outline=(50, 50, 50),
            width=3
        )
        
        # Desenha o telhado (triângulo)
        telhado_altura = base_altura // 2
        draw.polygon(
            [
                (base_x - base_largura // 10, base_y),  # Esquerda
                (base_x + base_largura + base_largura // 10, base_y),  # Direita
                (base_x + base_largura // 2, base_y - telhado_altura),  # Topo
            ],
            fill=(150, 75, 0),
            outline=(50, 50, 50),
            width=3
        )
        
        # Desenha porta
        porta_largura = base_largura // 4
        porta_altura = base_altura // 2
        porta_x = base_x + (base_largura - porta_largura) // 2
        porta_y = base_y + base_altura - porta_altura
        
        draw.rectangle(
            [(porta_x, porta_y), (porta_x + porta_largura, porta_y + porta_altura)],
            fill=(100, 50, 0),
            outline=(50, 25, 0),
            width=2
        )
        
        # Desenha janelas (2)
        janela_tamanho = base_largura // 6
        # Janela esquerda
        draw.rectangle(
            [
                (base_x + base_largura // 5, base_y + base_altura // 4),
                (base_x + base_largura // 5 + janela_tamanho, base_y + base_altura // 4 + janela_tamanho)
            ],
            fill=(200, 230, 255),
            outline=(50, 50, 50),
            width=2
        )
        # Janela direita
        draw.rectangle(
            [
                (base_x + base_largura - base_largura // 5 - janela_tamanho, base_y + base_altura // 4),
                (base_x + base_largura - base_largura // 5, base_y + base_altura // 4 + janela_tamanho)
            ],
            fill=(200, 230, 255),
            outline=(50, 50, 50),
            width=2
        )
        
        # Adiciona algum texto se fornecido
        if descricao:
            # Adiciona texto na parte superior da imagem
            try:
                fonte = ImageFont.truetype("arial.ttf", tamanho[0] // 20)
            except IOError:
                fonte = ImageFont.load_default()
                
            # Cor de fundo para o texto
            texto_bg = (0, 0, 0, 128)  # Preto semi-transparente
            texto_largura, texto_altura = 0, 0
            
            try:
                bbox = draw.textbbox((0, 0), descricao, font=fonte)
                texto_largura = bbox[2] - bbox[0]
                texto_altura = bbox[3] - bbox[1]
            except AttributeError:
                # Fallback para versões mais antigas do PIL
                texto_largura, texto_altura = draw.textsize(descricao, font=fonte)
                
            # Desenha fundo do texto
            draw.rectangle(
                [(largura // 10, altura // 10), 
                 (largura // 10 + texto_largura + 20, altura // 10 + texto_altura + 10)],
                fill=texto_bg
            )
            
            # Desenha texto
            draw.text(
                (largura // 10 + 10, altura // 10 + 5),
                descricao,
                fill=(255, 255, 255),
                font=fonte
            )
            
        return imagem
        
    def gerar_imagem_veiculo(self, tamanho=(800, 400), descricao=None):
        """Gera uma imagem aleatória de veículo para testes"""
        # Estilo mais adequado para veículos
        cor1 = (30, 30, 30)  # Preto
        cor2 = (150, 150, 150)  # Cinza
        
        # Gera base com gradiente
        imagem = self._gerar_gradiente(tamanho, cor1, cor2)
        draw = ImageDraw.Draw(imagem)
        largura, altura = tamanho
        
        # Desenha um carro esquemático
        # Base do carro (retângulo)
        base_largura = largura // 2
        base_altura = altura // 4
        base_x = (largura - base_largura) // 2
        base_y = altura - base_altura - altura // 5
        
        # Cor aleatória para o carro
        cores_carro = [
            (255, 0, 0),     # Vermelho
            (0, 0, 255),     # Azul
            (0, 255, 0),     # Verde
            (255, 255, 0),   # Amarelo
            (0, 0, 0),       # Preto
            (255, 255, 255), # Branco
            (128, 0, 128),   # Roxo
            (255, 165, 0)    # Laranja
        ]
        cor_carro = random.choice(cores_carro)
        
        # Desenha o corpo do carro
        draw.rectangle(
            [(base_x, base_y), (base_x + base_largura, base_y + base_altura)],
            fill=cor_carro,
            outline=(0, 0, 0),
            width=3
        )
        
        # Desenha o teto do carro
        teto_largura = base_largura * 0.6
        teto_altura = base_altura * 0.7
        teto_x = base_x + (base_largura - teto_largura) // 2
        teto_y = base_y - teto_altura
        
        draw.rectangle(
            [(teto_x, teto_y), (teto_x + teto_largura, base_y)],
            fill=cor_carro,
            outline=(0, 0, 0),
            width=2
        )
        
        # Desenha rodas (círculos)
        roda_raio = base_altura // 3
        # Roda traseira
        draw.ellipse(
            [(base_x + base_largura // 5 - roda_raio, base_y + base_altura - roda_raio),
             (base_x + base_largura // 5 + roda_raio, base_y + base_altura + roda_raio)],
            fill=(50, 50, 50),
            outline=(0, 0, 0),
            width=2
        )
        # Roda dianteira
        draw.ellipse(
            [(base_x + base_largura - base_largura // 5 - roda_raio, base_y + base_altura - roda_raio),
             (base_x + base_largura - base_largura // 5 + roda_raio, base_y + base_altura + roda_raio)],
            fill=(50, 50, 50),
            outline=(0, 0, 0),
            width=2
        )
        
        # Janelas (simplificadas)
        # Janela dianteira
        draw.rectangle(
            [(teto_x + teto_largura * 0.6, teto_y + teto_altura * 0.2),
             (teto_x + teto_largura * 0.95, teto_y + teto_altura * 0.8)],
            fill=(200, 230, 255),
            outline=(0, 0, 0),
            width=1
        )
        # Janela traseira
        draw.rectangle(
            [(teto_x + teto_largura * 0.05, teto_y + teto_altura * 0.2),
             (teto_x + teto_largura * 0.4, teto_y + teto_altura * 0.8)],
            fill=(200, 230, 255),
            outline=(0, 0, 0),
            width=1
        )
        
        # Adiciona farol
        farol_tamanho = base_altura // 5
        draw.ellipse(
            [(base_x + base_largura - farol_tamanho - 10, base_y + base_altura // 3 - farol_tamanho // 2),
             (base_x + base_largura - 10, base_y + base_altura // 3 + farol_tamanho // 2)],
            fill=(255, 255, 200),
            outline=(200, 200, 0),
            width=1
        )
        
        # Adiciona algum texto se fornecido
        if descricao:
            # Adiciona texto na parte superior da imagem
            try:
                fonte = ImageFont.truetype("arial.ttf", tamanho[0] // 20)
            except IOError:
                fonte = ImageFont.load_default()
                
            # Cor de fundo para o texto
            texto_bg = (0, 0, 0, 128)  # Preto semi-transparente
            texto_largura, texto_altura = 0, 0
            
            try:
                bbox = draw.textbbox((0, 0), descricao, font=fonte)
                texto_largura = bbox[2] - bbox[0]
                texto_altura = bbox[3] - bbox[1]
            except AttributeError:
                # Fallback para versões mais antigas do PIL
                texto_largura, texto_altura = draw.textsize(descricao, font=fonte)
                
            # Desenha fundo do texto
            draw.rectangle(
                [(largura // 10, altura // 10), 
                 (largura // 10 + texto_largura + 20, altura // 10 + texto_altura + 10)],
                fill=texto_bg
            )
            
            # Desenha texto
            draw.text(
                (largura // 10 + 10, altura // 10 + 5),
                descricao,
                fill=(255, 255, 255),
                font=fonte
            )
            
        return imagem
        
    def salvar_imagem(self, imagem, prefixo="img", formato="png"):
        """Salva a imagem gerada com timestamp no nome"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        aleatorio = random.randint(1000, 9999)
        nome_arquivo = f"{prefixo}_{timestamp}_{aleatorio}.{formato}"
        caminho_completo = os.path.join(self.diretorio_saida, nome_arquivo)
        
        # Salva a imagem
        if imagem.mode == 'RGBA' and formato.lower() != 'png':
            # Converte para RGB se o formato não suportar transparência
            imagem = imagem.convert('RGB')
            
        imagem.save(caminho_completo)
        logger.info(f"Imagem salva em {caminho_completo}")
        
        return caminho_completo
        
    def obter_bytes_imagem(self, imagem, formato="png"):
        """Retorna a imagem como bytes para uso em APIs"""
        buffer = BytesIO()
        
        if imagem.mode == 'RGBA' and formato.lower() != 'png':
            # Converte para RGB se o formato não suportar transparência
            imagem = imagem.convert('RGB')
            
        imagem.save(buffer, format=formato.upper())
        return buffer.getvalue()
        
    def gerar_lote_avatares(self, quantidade=5, tamanho=(200, 200), prefixo_texto="Agente"):
        """Gera um lote de avatares e retorna os caminhos para as imagens"""
        caminhos = []
        
        for i in range(quantidade):
            texto = f"{prefixo_texto} {i+1}"
            avatar = self.gerar_avatar(tamanho, texto)
            caminho = self.salvar_imagem(avatar, prefixo="avatar")
            caminhos.append(caminho)
            
        return caminhos
        
    def gerar_lote_imoveis(self, quantidade=5, tamanhos=None, descricoes=None):
        """Gera um lote de imagens de imóveis e retorna os caminhos"""
        caminhos = []
        
        # Descrições padrão se não fornecidas
        if not descricoes:
            descricoes = [
                "Apartamento 2 quartos",
                "Casa com piscina",
                "Cobertura duplex",
                "Sobrado 3 quartos",
                "Flat mobiliado",
                "Casa de campo",
                "Apartamento studios",
                "Loft industrial"
            ]
            
        # Tamanhos padrão se não fornecidos
        if not tamanhos:
            tamanhos = [(800, 600), (1024, 768), (640, 480)]
            
        for i in range(quantidade):
            tamanho = random.choice(tamanhos)
            descricao = random.choice(descricoes) if i < len(descricoes) else f"Imóvel {i+1}"
            imagem = self.gerar_imagem_imovel(tamanho, descricao)
            caminho = self.salvar_imagem(imagem, prefixo="imovel")
            caminhos.append(caminho)
            
        return caminhos
        
    def gerar_lote_veiculos(self, quantidade=5, tamanhos=None, descricoes=None):
        """Gera um lote de imagens de veículos e retorna os caminhos"""
        caminhos = []
        
        # Descrições padrão se não fornecidas
        if not descricoes:
            descricoes = [
                "Sedan 1.6 automático",
                "SUV 4x4 turbo",
                "Hatch compacto",
                "Pick-up diesel",
                "Esportivo V8",
                "Elétrico 100kW",
                "Minivan 7 lugares",
                "Conversível"
            ]
            
        # Tamanhos padrão se não fornecidos
        if not tamanhos:
            tamanhos = [(800, 400), (1024, 512), (640, 320)]
            
        for i in range(quantidade):
            tamanho = random.choice(tamanhos)
            descricao = random.choice(descricoes) if i < len(descricoes) else f"Veículo {i+1}"
            imagem = self.gerar_imagem_veiculo(tamanho, descricao)
            caminho = self.salvar_imagem(imagem, prefixo="veiculo")
            caminhos.append(caminho)
            
        return caminhos


def main():
    """Função principal de demonstração"""
    gerador = ImagemAleatoria()
    
    print("=== Gerando exemplos de imagens ===")
    
    # Gera um avatar
    avatar = gerador.gerar_avatar(texto="BeOnSafe")
    avatar_path = gerador.salvar_imagem(avatar, prefixo="avatar")
    print(f"Avatar gerado: {avatar_path}")
    
    # Gera uma imagem de imóvel
    imovel = gerador.gerar_imagem_imovel(descricao="Casa 3 quartos")
    imovel_path = gerador.salvar_imagem(imovel, prefixo="imovel")
    print(f"Imagem de imóvel gerada: {imovel_path}")
    
    # Gera uma imagem de veículo
    veiculo = gerador.gerar_imagem_veiculo(descricao="SUV Automático")
    veiculo_path = gerador.salvar_imagem(veiculo, prefixo="veiculo")
    print(f"Imagem de veículo gerada: {veiculo_path}")
    
    # Gera lote de avatares
    avatar_paths = gerador.gerar_lote_avatares(quantidade=3)
    print(f"Lote de avatares gerado: {len(avatar_paths)} imagens")
    
    print("Todas as imagens foram salvas em:", gerador.diretorio_saida)
    

if __name__ == "__main__":
    main() 