# 🦉 RESPONSA — OSINT Toolkit em Python

**RESPONSA** é uma ferramenta de linha de comando (CLI) para investigação em
fontes abertas (**OSINT** — *Open Source Intelligence*), escrita em Python.
Ao abrir, exibe um banner de "olho de coruja" colorido no terminal e oferece
um menu com 6 tipos de busca baseadas 100% em dados públicos e APIs abertas.

```
                  .:^~7?JY55PGGGGP5YJ7~^:.
              .^7Y5GB###&&&&&&&&&&&&###BG5Y7^.
           :~YG#&&&&&&&&&&&&&&&&&&&&&&&&&&&&#GY~:
                     🦉  R E S P O N S A  🦉
```

## ✨ Funcionalidades

| # | Busca              | O que faz                                                                 | Fonte de dados |
|---|---------------------|----------------------------------------------------------------------------|----------------|
| 1 | **Username**        | Verifica a existência de um nome de usuário em **129 sites** (28 redes sociais + 101 sites gerais, Brasil + internacional) | Requisições HTTP diretas |
| 2 | **E-mail**          | Formato, MX, domínio descartável, avatar no Gravatar, commits públicos no GitHub, reputação/presença em redes sociais (EmailRep), entregabilidade (Hunter.io) e vazamentos (HaveIBeenPwned) | DNS + Gravatar + GitHub + EmailRep.io + Hunter.io + HaveIBeenPwned |
| 3 | **CEP**              | Consulta endereço completo a partir do CEP                                | [ViaCEP](https://viacep.com.br) |
| 4 | **Telefone**         | Valida número, identifica país, operadora, tipo de linha e fuso horário   | libphonenumber (Google) |
| 5 | **Nome completo**    | Busca na web (DuckDuckGo) + gera links diretos para outros mecanismos e bases públicas (Escavador, JusBrasil etc.) | DuckDuckGo + links públicos |
| 6 | **IP**               | Geolocalização aproximada, provedor (ISP), organização, hostname reverso   | [ipinfo.io](https://ipinfo.io) (HTTPS, sem exigir chave) |
| 7 | **WHOIS/domínio**    | Registro do domínio: status, nameservers, datas de registro/expiração      | RDAP ([rdap.org](https://rdap.org)) |
| 8 | **Subdomínios**      | Mapeia subdomínios de um domínio via Certificate Transparency logs         | [crt.sh](https://crt.sh) |
| 9 | **CNPJ**             | Dados cadastrais de empresas brasileiras: razão social, situação, sócios (QSA), endereço | [BrasilAPI](https://brasilapi.com.br) (base da Receita Federal) |
| 10 | **Análise de link**  | Reputação de uma URL — malware/phishing, segundo 70+ motores de antivírus  | [VirusTotal](https://virustotal.com) (exige chave gratuita) |
| 11 | **Identificador de hash** | Identifica o algoritmo provável de um hash (MD5, SHA-1/256/512, bcrypt etc.) — 100% offline | — |
| 12 | **Imagem (reversa/EXIF)** | URL: gera links de busca reversa (Google Lens, Yandex, Bing, TinEye). Arquivo local: extrai metadados EXIF (câmera, data, GPS) | Links diretos + Pillow (local) |
| 13 | **CPF (validador)** | Confere se um CPF é matematicamente válido pelo dígito verificador — não retorna nome/dados pessoais | Algoritmo offline |

Todas as buscas rodam com **threads paralelas** (na busca de username) e
mostram os resultados em tabelas coloridas no terminal, com opção de
**exportar em JSON**.

## 📸 Banner

Ao abrir o programa, um olho de coruja em ASCII art com gradiente de cores
é desenhado no terminal, seguido do menu de opções — dá pra customizar as
cores e o desenho em `responsa/banner.py`.

## 🚀 Instalação

### Pré-requisitos
- Python 3.9 ou superior
- pip

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/alairon330-rgb/responsa.git
cd responsa

# 2. (Recomendado) crie um ambiente virtual
python3 -m venv venv
# Escolha a linha correspondente ao seu sistema operacional:
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o programa
python -m responsa
```

### Instalação como comando global (opcional)

```bash
pip install .
responsa
```

Isso instala o pacote e cria o comando `responsa`, que pode ser chamado de
qualquer lugar do terminal.

## 🧭 Uso

Ao rodar `python -m responsa` (ou `responsa`), você verá o banner e o menu:

```
[1]  Busca por nome de usuário
[2]  Busca por e-mail
[3]  Busca por CEP
[4]  Busca por telefone
[5]  Busca por nome completo
[6]  Busca por IP
[7]  WHOIS / registro de domínio
[8]  Subdomínios (Certificate Transparency)
[9]  Consulta de CNPJ
[10] Análise de link suspeito (VirusTotal)
[11] Identificador de hash
[12] Busca reversa de imagem / EXIF
[13] Validador de CPF (offline)
[0]  Sair
```

Basta escolher o número da opção e informar o dado solicitado. Ao final de
cada busca, é possível exportar o resultado em JSON, salvo na pasta
`responsa_resultados/` (criada automaticamente e ignorada pelo git).

## 🔑 Chaves de API opcionais (busca de e-mail)

A busca de e-mail já funciona sem nenhuma chave (formato, MX, domínio
descartável, Gravatar e commits públicos no GitHub). Para desbloquear
reputação/presença em redes sociais, entregabilidade mais precisa e
checagem de vazamentos, configure chaves gratuitas/pagas via variável
de ambiente antes de rodar o programa:

```bash
export RESPONSA_EMAILREP_KEY="sua_chave"    # grátis — emailrep.io/free (250/mês, 10/dia)
export RESPONSA_HUNTER_KEY="sua_chave"      # grátis — hunter.io (sem cartão, ~100 verificações/mês)
export RESPONSA_HIBP_KEY="sua_chave"        # paga — haveibeenpwned.com/API/Key
export RESPONSA_GITHUB_TOKEN="seu_token"    # grátis — github.com/settings/tokens (aumenta o limite de busca de commits)
export RESPONSA_VT_KEY="sua_chave"          # grátis — virustotal.com (análise de link, 4 req/min)
export RESPONSA_IPINFO_KEY="sua_chave"      # grátis — ipinfo.io (50 mil/mês, opcional — funciona sem chave)
```

Dica: coloque essas linhas no seu `~/.bashrc` ou `~/.zshrc` pra não
precisar exportar toda vez que abrir um terminal novo.

**Por que não sondamos redes sociais diretamente por e-mail:** ao
contrário do username (que verifica páginas de perfil públicas), não
existe uma "página pública" que responda "esse e-mail tem conta no
Instagram?" — a única forma seria abusar dos formulários de cadastro/
recuperação de senha dos sites, o que a maioria bloqueia e que é a
mesma técnica usada em reconhecimento para phishing direcionado. O
EmailRep.io resolve isso de forma legítima: é um serviço comercial de
inteligência de e-mail que já mapeia presença em redes sociais sob os
próprios termos de uso dele, então usamos a API oficial em vez de
reinventar a sondagem por conta própria.

## 🔒 Por que não tem busca de "CPF → pessoa"

CNPJ é público por natureza (transparência empresarial). CPF é o oposto:
dado pessoal protegido pela LGPD. Não existe API legítima que resolva
"CPF → nome/endereço/telefone" — o único serviço oficial (Receita Federal)
exige CPF **+ data de nascimento**, tem captcha de propósito, e mesmo assim
só devolve situação cadastral com nome mascarado. Praticamente todo site
"consulta CPF grátis" que aceita só o número roda sobre bases vazadas
ilegalmente (o vazamento de 223 milhões de CPFs de 2021 é a fonte não
declarada da maioria). Por isso o RESPONSA só valida o **formato** do CPF
(dígito verificador), sem consultar ou revelar identidade nenhuma.

## 🗂️ Estrutura do projeto

```
responsa/
├── responsa/
│   ├── __main__.py         # ponto de entrada (python -m responsa)
│   ├── menu.py              # menu interativo
│   ├── banner.py            # ASCII art do olho de coruja + cores
│   ├── config.py            # constantes e configurações
│   ├── utils.py             # helpers (export, prints coloridos)
│   ├── data/
│   │   └── sites.json       # base de 129 sites para busca de username
│   └── modules/
│       ├── username_search.py
│       ├── email_search.py
│       ├── cep_search.py
│       ├── phone_search.py
│       ├── name_search.py
│       └── ip_search.py
├── tests/
│   └── test_modules.py      # testes offline
├── build_sites_db.py        # script que gera data/sites.json
├── requirements.txt
├── setup.py
├── LICENSE
└── README.md
```

## 🧪 Testes

```bash
pip install -r requirements.txt
python tests/test_modules.py
```

Os testes são todos offline (não dependem de rede) e validam a estrutura da
base de sites, regexes e parsing de telefone/IP.

## 🔧 Manutenção da base de sites

A lista de sites usada na busca de username fica em `responsa/data/sites.json`
e é gerada pelo script `build_sites_db.py`. Sites mudam de layout com
frequência — se algum site passar a dar falso positivo/negativo, edite a
lista em `build_sites_db.py`, rode `python build_sites_db.py` novamente e
abra um Pull Request. Contribuições são bem-vindas!

**Limitação conhecida:** sites com front-end 100% JavaScript às vezes
retornam HTTP 200 mesmo para perfis inexistentes, e alguns bloqueiam
requisições automatizadas. Nesses casos o resultado aparece como
"indefinido" em vez de um falso "encontrado" — sempre confira manualmente
os resultados antes de tirar conclusões.

## ⚖️ Uso ético e responsável

Este projeto foi criado para fins educacionais, de pesquisa em segurança da
informação e verificação de informações públicas. Ao usá-lo:

- Utilize apenas para consultar **dados que já são públicos**.
- Respeite a **LGPD** (Lei Geral de Proteção de Dados, Brasil) e legislações
  equivalentes do seu país.
- **Não** use para assediar, perseguir (stalking), ameaçar ou de qualquer
  forma prejudicar outras pessoas.
- Os autores não se responsabilizam pelo uso indevido desta ferramenta.

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuindo

Pull requests são bem-vindos! Para mudanças grandes, abra uma issue primeiro
para discutirmos o que você gostaria de alterar.

1. Faça um fork do projeto
2. Crie sua branch (`git checkout -b feature/nova-busca`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova busca'`)
4. Push para a branch (`git push origin feature/nova-busca`)
5. Abra um Pull Request
