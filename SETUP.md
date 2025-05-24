# 🛠️ Configuração do Perfil GitHub

Este documento contém as instruções para configurar e manter seu perfil GitHub atualizado.

## 📋 Pré-requisitos

- Conta no GitHub
- Git configurado localmente
- (Opcional) Conta no WakaTime para estatísticas detalhadas

## 🚀 Deploy Inicial

### 1. Clone ou inicialize o repositório

```bash
# Se for um novo repositório
git init
git remote add origin https://github.com/ericvasr/ericvasr.git

# Se for um clone
git clone https://github.com/ericvasr/ericvasr.git
```

### 2. Configure o Git (se necessário)

```bash
git config user.name "Eric Ribeiro"
git config user.email "seu-email@exemplo.com"
```

### 3. Execute o deploy

```bash
# Usando o script automatizado
./deploy.sh "🎉 Primeiro deploy do perfil"

# Ou manualmente
git add .
git commit -m "🎉 Primeiro deploy do perfil"
git push origin main
```

## 🔄 Atualizações Automáticas

### GitHub Actions

O arquivo `.github/workflows/update-readme.yml` configura atualizações automáticas:

- **Frequência**: Diariamente às 6:00 UTC (3:00 BRT)
- **Trigger manual**: Disponível via GitHub Actions tab
- **Auto-commit**: Sim, quando há mudanças nas estatísticas

### WakaTime (Opcional)

Para estatísticas mais detalhadas:

1. Crie uma conta em [WakaTime](https://wakatime.com)
2. Obtenha sua API Key
3. Adicione como secret no GitHub:
   - Vá em Settings > Secrets and variables > Actions
   - Adicione `WAKATIME_API_KEY` com sua chave

## 📝 Personalizações

### Alterando o GIF

1. Substitua o arquivo em `./public/playtape.gif`
2. Execute: `./deploy.sh "🎨 Novo GIF do perfil"`

### Editando conteúdo

1. Edite o arquivo `README.md`
2. Execute: `./deploy.sh "📝 Atualização de conteúdo"`

### Adicionando novas seções

Mantenha a estrutura atual e adicione suas seções personalizadas.

## 🎨 Elementos Visuais

### Badges disponíveis

- [Shields.io](https://shields.io) - Badges personalizados
- [Simple Icons](https://simpleicons.org) - Ícones para tecnologias

### Estatísticas GitHub

- **GitHub Stats**: Estatísticas automáticas do perfil
- **Language Stats**: Linguagens mais utilizadas
- **Streak Stats**: Sequência de commits
- **Profile Views**: Contador de visualizações

## 🔧 Solução de Problemas

### GitHub Actions não executa

1. Verifique se o repositório tem Actions habilitado
2. Confirme se os secrets estão configurados
3. Verifique logs na aba Actions

### GIF não aparece

1. Confirme se o arquivo está em `./public/playtape.gif`
2. Verifique se o arquivo foi commitado
3. Teste o caminho: `./public/playtape.gif`

### Links não funcionam

1. Atualize URLs nos badges de contato
2. Confirme usernames corretos nas estatísticas

## 📚 Recursos Úteis

- [GitHub Profile README](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme)
- [Awesome GitHub Profile README](https://github.com/abhisheknaiidu/awesome-github-profile-readme)
- [GitHub README Stats](https://github.com/anuraghazra/github-readme-stats)

---

**Eric Ribeiro** - [GitHub](https://github.com/ericvasr) | [BeonSafe-Opensource](https://github.com/BeonSafe-Opensource)
