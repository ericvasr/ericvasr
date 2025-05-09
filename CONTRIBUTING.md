# Guia de Contribuição - Git3D Premium

Obrigado por considerar contribuir para o projeto Git3D Premium! Este documento fornece diretrizes e informações para ajudar no processo de contribuição.

## 🌟 Como Contribuir

Existem várias maneiras de contribuir com o projeto:

1. **Reportar bugs**: Abra issues detalhando problemas encontrados
2. **Sugerir melhorias**: Compartilhe ideias para novos recursos ou melhorias
3. **Submeter código**: Envie pull requests com correções ou novos recursos
4. **Melhorar documentação**: Ajude a manter a documentação atualizada e clara
5. **Compartilhar exemplos**: Mostre como você está usando o Git3D

## 📋 Processo de Contribuição

### Para Reportar Bugs ou Sugerir Melhorias

1. Verifique se já não existe uma issue sobre o mesmo tema
2. Use o template de issue apropriado, se disponível
3. Forneça informações detalhadas que permitam reproduzir o problema
4. Inclua capturas de tela ou logs, quando relevante

### Para Contribuir com Código

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Implemente suas mudanças seguindo o estilo de código do projeto
4. Adicione testes para novos recursos, quando aplicável
5. Certifique-se de que todos os testes estão passando
6. Atualize a documentação conforme necessário
7. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
8. Push para a branch (`git push origin feature/nova-funcionalidade`)
9. Abra um Pull Request descrevendo suas alterações

## 🔧 Ambiente de Desenvolvimento

Para configurar um ambiente de desenvolvimento:

```bash
# Clone seu fork
git clone https://github.com/seu-usuario/git3d.git
cd git3d

# Adicione o upstream para manter-se atualizado
git remote add upstream https://github.com/ericvasr/git3d.git

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale dependências de desenvolvimento
pip install -r requirements-dev.txt  # se existir
```

## 📝 Estilo de Código

- Siga a PEP 8 para código Python
- Use docstrings no formato do NumPy/SciPy
- Mantenha a documentação atualizada
- Adicione comentários explicativos quando necessário

## 🧪 Testes

- Adicione testes para novos recursos sempre que possível
- Execute a suite de testes antes de enviar um PR
- Os testes devem ser executados com:
  ```bash
  pytest
  ```

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a licença MIT do projeto.

## 🤝 Código de Conduta

- Seja respeitoso e inclusivo
- Valorize opiniões e perspectivas diferentes
- Concentre-se em colaboração construtiva
- Mantenha o foco na melhoria do projeto

---

Esperamos que este guia facilite suas contribuições! Se tiver dúvidas, não hesite em abrir uma issue pedindo esclarecimentos.

**Equipe BeOnSafe** 