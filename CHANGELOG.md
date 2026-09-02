# Changelog — RESPONSA

Todas as mudanças notáveis do projeto são documentadas neste arquivo.

## [1.1.0] — 2026-09-02

### Corrigido

- **Módulo de geolocalização por IP** (`ip_search.py`): migrado de `ip-api.com`
  (HTTP, porta 80) para `ipinfo.io` (HTTPS). A dependência de porta 80 causava
  falha silenciosa em redes/VMs que bloqueiam tráfego HTTP não criptografado
  na saída. IP privado (ex: `192.168.x.x`) agora recebe mensagem de erro
  específica em vez de erro genérico de API.

- **`ValueError: Invalid header value`** em `link_analysis.py` (módulo
  VirusTotal): causado por um caractere de quebra de linha (`\n`) residual
  em `RESPONSA_VT_KEY`, introduzido por copy-paste da chave via `nano`. O
  Python aceitava a variável de ambiente sem validar o conteúdo, e a
  biblioteca `urllib3` rejeitava o header HTTP malformado apenas no momento
  da requisição — o erro não aparecia no menu interativo porque a exceção
  genérica (`requests.RequestException`) não cobre `ValueError`, deixando o
  módulo "sumir" sem mensagem visível ao usuário.

### Alterado

- **Todas as leituras de variável de ambiente** (`RESPONSA_GITHUB_TOKEN`,
  `RESPONSA_EMAILREP_KEY`, `RESPONSA_HUNTER_KEY`, `RESPONSA_HIBP_KEY`,
  `RESPONSA_IPINFO_KEY`, `RESPONSA_VT_KEY`) passaram de:

  ```python
  api_key = os.environ.get("RESPONSA_X_KEY")
  ```

  para:

  ```python
  api_key = os.environ.get("RESPONSA_X_KEY", "").strip() or None
  ```

  Isso normaliza espaços em branco e quebras de linha acidentais em
  qualquer chave configurada via `export`, `.zshrc`/`.bashrc` ou copy-paste,
  prevenindo recorrência do bug acima com qualquer credencial futura.

### Segurança

- Duas chaves de API do Hunter.io foram expostas acidentalmente em
  capturas de tela durante uma sessão de configuração. Ambas foram
  revogadas no painel do provedor e substituídas por uma chave nova,
  gerada e validada em um fluxo sem exposição visual.
- Reforçado o princípio de *least privilege* na geração de credenciais:
  o `RESPONSA_GITHUB_TOKEN` é gerado como *classic token* sem nenhum
  escopo marcado, suficiente para leitura de commits públicos via
  GitHub Search API — nenhuma permissão de escrita ou acesso a
  repositórios privados é concedida.

### Notas de operação

- Confirmado que o shell padrão do Kali Linux (desde 2020) é `zsh`, não
  `bash`. Variáveis de ambiente exportadas em `~/.bashrc` não são
  carregadas automaticamente nesse ambiente — o arquivo correto é
  `~/.zshrc`.
- Reforçado o fluxo de atualização de projeto: baixar o `.zip` direto
  pelo Firefox *dentro* da VM evita o problema recorrente de versões
  desatualizadas causado pela cadeia Windows → pendrive → VM.

### Chaves de API — status de configuração

| Variável                  | Serviço        | Tier gratuito | Status nesta sessão |
|---------------------------|----------------|:---:|---|
| `RESPONSA_GITHUB_TOKEN`   | GitHub         | Sim | ✅ Configurada e validada |
| `RESPONSA_HUNTER_KEY`     | Hunter.io      | Sim (25/mês) | ✅ Configurada e validada |
| `RESPONSA_VT_KEY`         | VirusTotal     | Sim (4 req/min) | ✅ Configurada e validada |
| `RESPONSA_IPINFO_KEY`     | ipinfo.io      | Sim (50k/mês) | Não necessária — free tier sem chave já suficiente |
| `RESPONSA_EMAILREP_KEY`   | EmailRep.io    | Sim (250/mês) | Pendente — cadastro em análise pelo provedor |
| `RESPONSA_HIBP_KEY`       | HaveIBeenPwned | **Não** (a partir de US$ 4,39/mês) | Não configurada — decisão do usuário |

---

## [1.0.0] — RESPONSA 13 módulos

Versão base com os 13 módulos de busca: username (129 sites), e-mail,
CEP, telefone, nome completo, IP, WHOIS/domínio, subdomínios (crt.sh),
CNPJ, análise de link (VirusTotal), identificador de hash, imagem
reversa/EXIF, validador de CPF offline.

### Excluído por design

- Enumeração de redes sociais via sondagem de formulário de e-mail
  (violação de ToS, vetor de reconhecimento para phishing).
- Consulta CPF → identidade (LGPD; não existe API pública legítima
  equivalente ao BrasilAPI para CNPJ). Substituído por validador de
  checksum offline.
- Busca reversa de imagem por reconhecimento facial (risco de
  facilitação de stalking). Mantida apenas busca reversa por
  similaridade/EXIF.
