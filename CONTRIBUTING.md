# Contribuindo com o RESPONSA

Obrigado pelo interesse em contribuir! Este documento explica como propor
mudancas, o que esperamos de uma contribuicao, e os principios que guiam
decisoes de design no projeto.

## Antes de contribuir

Leia a secao Uso etico e responsavel do README.md e o CHANGELOG.md,
que documenta decisoes de design ja tomadas -- incluindo funcionalidades
deliberadamente nao implementadas por risco de abuso (ex: enumeracao de
redes sociais via sondagem de e-mail, consulta CPF -> identidade,
reconhecimento facial). Propostas que reintroduzam esse tipo de capacidade
nao serao aceitas, independente da motivacao.

## Como contribuir

1. Abra uma Issue descrevendo o problema ou melhoria antes de escrever
   codigo -- isso evita trabalho duplicado ou PRs que nao se alinham com
   a direcao do projeto.
2. Faca um fork do repositorio.
3. Crie uma branch descritiva:
   git checkout -b fix/nome-do-bug
   git checkout -b feat/nome-da-funcionalidade
4. Siga o padrao de codigo ja existente nos modulos (responsa/modules/):
   - Leitura de chave de API sempre com .strip() or None
     (ver CHANGELOG.md -- evita bugs de header HTTP malformado)
   - Timeout explicito em toda requisicao HTTP (config.REQUEST_TIMEOUT)
   - Tratamento de excecao especifico, nao except Exception generico
     silencioso (esse tipo de captura escondeu um bug real nesta sessao
     de desenvolvimento)
5. Teste localmente antes de abrir o PR:
   python -m responsa
   python -m pytest tests/
6. Abra o Pull Request referenciando a Issue correspondente.

## O que aceitamos

- Correcao de bugs, com reproducao clara do problema
- Novos modulos de OSINT baseados em APIs publicas legitimas (nao
  scraping de dados que violem Termos de Servico)
- Melhorias de performance, testes, documentacao
- Correcoes de seguranca (ver secao abaixo para relatos sensiveis)

## O que nao aceitamos

- Funcionalidades que dependam de scraping agressivo ou sondagem de login
- Qualquer forma de correlacao de dados sensiveis sem base legal
  (ex: CPF -> identidade, sem API publica oficial)
- Reconhecimento facial ou biometria
- Remocao dos avisos de uso etico do banner ou README

## Relatando problemas de seguranca

Se encontrar uma vulnerabilidade (ex: injecao, exposicao de credencial,
SSRF), nao abra uma Issue publica. Entre em contato diretamente com o
mantenedor antes de divulgar, para dar tempo de correcao.

## Licenca

Ao contribuir, voce concorda que seu codigo sera distribuido sob a mesma
licenca do projeto (MIT + Commons Clause -- ver LICENSE).
