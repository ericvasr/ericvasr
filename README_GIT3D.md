# 🔷 Git3D - BeOnSafe

Visualização 3D de contribuições do GitHub com design exclusivo da BeOnSafe.

## 📋 Sobre o Projeto

Git3D é uma ferramenta desenvolvida pela BeOnSafe para criar visualizações 3D interativas e impressionantes das suas contribuições no GitHub. Ideal para:

- Incluir em seu perfil do GitHub
- Exibir em seu portfólio profissional
- Compartilhar em redes sociais
- Analisar seus padrões de contribuição

## 🚀 Características

- **Visualização 3D Interativa**: Explore suas contribuições em um modelo 3D completo
- **Design BeOnSafe**: Identidade visual elegante com paleta exclusiva
- **Animações**: Visualizações animadas para maior impacto visual
- **Estatísticas Detalhadas**: Análise completa dos seus padrões de contribuição
- **Automação**: Processo automatizado de coleta de dados e geração de visualizações
- **Integração com README**: Atualização automática do seu perfil do GitHub

## 🛠️ Requisitos

- Python 3.6 ou superior
- Token de acesso pessoal do GitHub
- Dependências listadas em `requirements.txt`

## ⚙️ Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/ericvasr/git3d.git
   cd git3d
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Para gerar GIFs (opcional, mas recomendado):
   ```bash
   pip install kaleido imageio
   ```

## 📊 Uso

Execute o script principal e siga as instruções:

```bash
python run_git3d.py [seu_usuario_github]
```

O script irá:
1. Solicitar seu token do GitHub (ou usar o definido em variáveis de ambiente)
2. Baixar dados das suas contribuições
3. Gerar visualizações 3D interativas
4. Criar imagens estáticas e animadas
5. Atualizar seu README.md (opcional)

## 🖼️ Exemplos de Saída

- `images/github_3d_beonsafe.html` - Visualização 3D interativa
- `images/github_3d_beonsafe.png` - Imagem estática para inclusão em documentos
- `images/github_3d_beonsafe.gif` - Animação para inclusão em README ou redes sociais
- `images/github_3d_beonsafe_animated.html` - Versão interativa com animação automática

## 📘 Personalização

Você pode personalizar a visualização editando as configurações em `generate_advanced_3d.py`:

- Altere a paleta de cores em `BEONSAFE_COLORS`
- Modifique o layout e estilo em `fig.update_layout()`
- Ajuste a animação e ângulos de visualização

## 🔐 Segurança

Seu token do GitHub é usado apenas localmente para acessar a API. Recomendamos:
- Usar um token com permissões limitadas
- Definir uma data de expiração curta
- Nunca compartilhar seu token

## 📬 Contato

**BeOnSafe**  
Email: eric@beonsafe.com.br  
GitHub: https://github.com/ericvasr

---

Desenvolvido com 💙 pela BeOnSafe 