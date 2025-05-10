# Configuração do Token do GitHub

Este documento explica como configurar corretamente o token de acesso pessoal do GitHub para uso com o projeto BeOnSafe.

## Obtendo um Token Pessoal

1. Acesse [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Clique em "Generate new token" (Clássico ou Fine-grained)
3. Dê um nome ao token (ex: "BeOnSafe API")
4. Selecione os seguintes escopos:
   - `repo` (acesso completo aos repositórios)
   - `read:user` (leitura de informações do usuário)
   - `user:email` (acesso ao email)
5. Gere o token e **copie-o imediatamente** (ele só é exibido uma vez)

## Configuração Local

Para desenvolvimento local, adicione o token ao arquivo `.env` na raiz do projeto:

```
GH_TOKEN=seu_token_aqui
```

## Configuração no GitHub Actions

Para CI/CD e execução automática, adicione o token como segredo do repositório:

1. Acesse as configurações do seu repositório
2. Vá para "Secrets and variables" > "Actions"
3. Adicione um novo segredo com o nome `GH_TOKEN` e o valor do seu token

## Verificando a Configuração

Para verificar se o token está configurado corretamente, execute:

```bash
python src/github_profile.py
```

Se o token estiver corretamente configurado, você verá informações do seu perfil do GitHub.

## Notas de Segurança

- **NUNCA** comite o token diretamente no código
- **NUNCA** compartilhe o token ou o exponha publicamente
- O arquivo `.env` está no `.gitignore` e nunca deve ser commitado
- Revogue tokens expostos imediatamente e gere novos
- Revise regularmente seus tokens e remova os que não estão em uso 