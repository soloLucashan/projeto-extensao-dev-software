# PixelShop

Projeto acadêmico da disciplina de Computação Aplicada do curso de Ciência da Computação da UNINOVE (Noturno 2026), sob orientação do professor Sergio João Guimarães da Silva. Entrega prevista para 03/12/2026.

A aplicação combina um site institucional em HTML e CSS, um backend em Python com Flask conectado ao Oracle Database e um programa em C que calcula o relatório consolidado de estoque.

## Funcionalidades

- Site institucional (`site/`): páginas estáticas `index.html`, `sobre.html`, `portfolio.html` e `contato.html`, além de `site/produtos.html` mantido apenas como exemplo estático.
- Catálogo dinâmico (`/produtos.html`): consulta os produtos e categorias no Oracle via Flask (`backend/templates/produtos.html`), agrupa os itens por categoria e indica o estado do estoque (disponível, últimas unidades quando menor que 3 e esgotado quando igual a 0).
- Relatório de estoque (`/relatorio.html`): lê os produtos do Oracle, envia os dados numéricos para o programa em C no modo `--relatorio`, valida o JSON retornado sem refazer cálculos em Python e exibe total de produtos, total de unidades, valor em estoque, itens em estado crítico (`< 3`) e itens esgotados (`0`). Em caso de falha no banco ou no executável C, a rota responde HTTP `503` com mensagem de indisponibilidade.
- Banco de dados (`banco-dados/`): esquema relacional com cinco tabelas (`CATEGORIA`, `PRODUTO`, `CLIENTE`, `PEDIDO` e `ITEM_PEDIDO`), carga de exemplo, scripts de instalação controlada e dez consultas em `queries.sql`.
- Menu interativo em terminal (`programa-c/main.c`): quando executado sem argumentos, permite cadastrar, listar, buscar, filtrar por categoria, remover produtos e consultar um relatório simples diretamente no terminal.

## Tecnologias e fluxo da integração

- Frontend: HTML5 e CSS3 (`site/css/style.css`).
- Backend: Python, Flask, Jinja2, `oracledb` e `python-dotenv` (`backend/`).
- Banco de dados: Oracle Database 21c Express Edition (`banco-dados/`).
- Módulo de cálculo: linguagem C padrão C11 (`programa-c/main.c`).

```text
Oracle (XEPDB1 / PIXELSHOP)
   │  SELECT produtos e categorias
   ▼
backend/db.py (oracledb, Decimal)
   │
   ├──▶ /produtos.html ──▶ Catálogo dinâmico (itens individuais e estoque)
   │
   └──▶ backend/integracao_c.py (id<TAB>centavos<TAB>estoque)
           │
           ▼
        programa-c/build/main_bloco2.exe --relatorio (cálculo em int64)
           │  JSON validado
           ▼
        /relatorio.html ──▶ Resumo consolidado (totais, críticos e esgotados)
```

Duas distinções importantes sobre o funcionamento:

- Menu em C vs. relatório web: ao abrir `programa-c\build\main_bloco2.exe` sem argumentos, o programa funciona apenas em memória (até 100 produtos), sem gravar em disco e sem conexão com o Oracle. A página `/relatorio.html` usa apenas o modo `--relatorio`, alimentado com os registros atuais do banco.
- Catálogo operacional vs. página estática: o catálogo ligado ao Oracle é a rota `/produtos.html` servida pelo Flask (`backend/templates/produtos.html`). O arquivo `site/produtos.html` fica apenas como referência estática.

## Requisitos

Os comandos e testes deste projeto foram validados em Windows 11 Pro (64 bits) com Python 3.14.5, GCC 15.2.0 (MSYS2 UCRT64) e Oracle Database 21c Express Edition (`SQL*Plus 21.3.0.0.0`). Outros sistemas operacionais ou versões ainda não foram testados.

- Python 3 (64 bits) com `venv` e `pip`.
- Compilador C (`gcc`, MSYS2 UCRT64 no Windows; o binário gerado depende apenas de `KERNEL32.dll` e da UCRT do sistema).
- Oracle Database 21c XE com a instância `XE` ativa, o PDB `XEPDB1` em `READ WRITE` e `sqlplus` no `PATH`.
- Pacotes Python listados em [backend/requirements.txt](backend/requirements.txt) (versões exatas usadas no ambiente testado em [backend/requirements-lock.txt](backend/requirements-lock.txt)).

## Configuração e execução

Extraia o projeto em uma pasta local e abra o PowerShell na raiz do projeto. Não copie `.venv` nem `.env` de outra máquina. Todos os blocos de comando abaixo indicam o diretório de partida.

### Ambiente Python

A partir da raiz do projeto, crie o ambiente virtual e instale as dependências:

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Se `python` abrir o atalho da Microsoft Store no Windows, consulte `py -0p` e use `py -m venv backend\.venv` ou o caminho completo do interpretador instalado.

### Compilação do módulo C

Ainda na raiz do projeto, compile `programa-c\main.c` no caminho exato esperado por `backend/integracao_c.py` (`programa-c\build\main_bloco2.exe`):

```powershell
New-Item -ItemType Directory -Force -Path programa-c\build | Out-Null
gcc -std=c11 -Wall -Wextra -Wpedantic programa-c\main.c -o programa-c\build\main_bloco2.exe
```

### Banco Oracle e carga inicial (somente na primeira instalação)

A criação do usuário `PIXELSHOP` e a instalação SQL são etapas únicas da primeira configuração. Se o usuário e o esquema já estiverem preparados no Oracle, pule esta seção e siga diretamente para a configuração do `.env` ou para a execução da aplicação.

Para criar o usuário `PIXELSHOP` e conceder privilégios no PDB `XEPDB1`, pode ser necessária uma sessão com conta administrativa do Oracle:

```sql
CREATE USER PIXELSHOP IDENTIFIED BY "SUA_SENHA_FORTE_LOCAL"
  DEFAULT TABLESPACE USERS
  QUOTA 100M ON USERS;

GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE TO PIXELSHOP;
```

Na instalação validada com Oracle 21c XE, foram utilizados `CREATE SESSION`, `CREATE TABLE` e `CREATE SEQUENCE`, além de cota de 100 MB em `USERS`. Não conceda o papel `DBA` nem privilégios `ANY` ao usuário `PIXELSHOP`.

A partir deste ponto, não utilize `SYS` nem `SYSTEM`: tanto a instalação das tabelas e dos dados quanto a execução do backend devem usar exclusivamente o usuário `PIXELSHOP`.

Antes de conectar, confira a porta configurada no Listener com `lsnrctl status`. Na instalação usada durante os testes locais a porta era `1522` (`127.0.0.1:1522/XEPDB1`), mas em outras instalações Oracle o padrão costuma ser `1521`.

A partir da raiz do projeto, entre em `banco-dados\` e conecte no SQL*Plus como `PIXELSHOP`:

```powershell
Set-Location banco-dados
sqlplus -L PIXELSHOP@127.0.0.1:PORTA/XEPDB1
```

No prompt do SQL*Plus, execute o instalador uma única vez em esquema vazio e encerre a sessão com `EXIT`:

```sql
@instalar_pixelshop.sql
EXIT
```

O script confere se a sessão está em `PIXELSHOP` / `XEPDB1` e se o esquema está vazio (`USER_OBJECTS = 0`), cria as tabelas (`create_tables.sql`), insere os dados de exemplo (`insert_data.sql`) e roda verificações de leitura (`verificar_pos_carga.sql`). Não reexecute `insert_data.sql` sobre tabelas já preenchidas.

Ao retornar ao PowerShell (ainda em `banco-dados\`), volte para a raiz do projeto:

```powershell
Set-Location ..
```

### Arquivo `.env`

A partir da raiz do projeto, crie `backend\.env` a partir do modelo sem sobrescrever um arquivo já existente:

```powershell
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
notepad backend\.env
```

Preencha `ORACLE_USER=PIXELSHOP`, sua `ORACLE_PASSWORD` local e o `ORACLE_DSN` correspondente ao seu Listener (por exemplo, `127.0.0.1:1522/XEPDB1` ou `127.0.0.1:1521/XEPDB1`). Nunca inclua `backend\.env` em pacotes de envio ou repositórios.

### Execução da aplicação

A partir da raiz do projeto, entre em `backend\` e inicie o servidor Flask local:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe app.py
```

A aplicação fica acessível em `http://127.0.0.1:5000` (`debug=False`, `use_reloader=False`):

- Página inicial: `http://127.0.0.1:5000/`
- Catálogo (Oracle): `http://127.0.0.1:5000/produtos.html`
- Relatório de estoque (Oracle + C): `http://127.0.0.1:5000/relatorio.html`

Para encerrar o servidor, use `Ctrl+C` e volte para a raiz do projeto com `Set-Location ..` antes de rodar comandos a partir dela. No menu interativo em C (`programa-c\build\main_bloco2.exe` sem argumentos, a partir da raiz), escolha a opção `0`.

## Testes

Os comandos abaixo consideram partida na raiz do projeto e retornam à raiz ao final quando entram em `backend\`.

Backend isolado, integração real Python ↔ C e coerência da interface (sem necessidade do Oracle), a partir da raiz do projeto:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
Set-Location ..
```

Verifica a exibição do catálogo com dados simulados, o carregamento de configuração sem expor credenciais, regras estáticas dos scripts SQL, a conversão `Decimal` para centavos, chamadas reais ao executável C e a consistência das páginas HTML.

Módulo C (modo `--relatorio` e menu interativo), a partir da raiz do projeto:

```powershell
backend\.venv\Scripts\python.exe -m unittest discover -s programa-c\tests -v
```

Testa o parsing da entrada, limites de linha e quantidade, prevenção de overflow em 64 bits, códigos de retorno e o comportamento do menu em memória.

Integração real com o Oracle (opt-in, somente leitura), a partir da raiz do projeto:

```powershell
Set-Location backend
$env:PIXELSHOP_RUN_ORACLE_TESTS='1'
.\.venv\Scripts\python.exe -m unittest discover -s tests_integracao -v
Remove-Item Env:PIXELSHOP_RUN_ORACLE_TESTS -ErrorAction SilentlyContinue
Set-Location ..
```

Executa apenas consultas `SELECT` no esquema `PIXELSHOP` (`XEPDB1`) para conferir privilégios da sessão, integridade da carga inicial, as dez consultas de `queries.sql` e a correspondência entre os dados do banco, o cálculo do módulo C e as páginas renderizadas pelo Flask.

## Limitações

- Recursos fora do escopo: não existem carrinho de compras, checkout, pagamento, login, painel administrativo (CRUD web) nem envio real de formulário na página `contato.html`.
- Menu C isolado: o menu interativo no terminal opera apenas em memória (limite de 100 produtos) e não altera nem lê o banco Oracle.
- Dependências externas na parte visual: o projeto não carrega recursos visuais 100% offline. Páginas estáticas carregam imagens de `images.unsplash.com` e `img.terabyteshop.com.br`, e a fonte `Inter` vem do Google Fonts (`fonts.googleapis.com`, com fallback para fontes locais do sistema). As rotas `/produtos.html` e `/relatorio.html` não usam imagens externas, mas carregam o CSS local (`site/css/style.css`), que importa a fonte do Google Fonts (com fallback local); por isso, também não são completamente independentes da internet.
- Portabilidade: a instalação e a execução foram verificadas apenas em uma máquina Windows 11 Pro; ainda não houve teste de reprodução em outro computador ou em outros sistemas operacionais.

## Equipe

Professor responsável: Sergio João Guimarães da Silva

| Integrante | RA |
|---|---|
| Julia Zezilia Rodrigues | 3026105026 |
| Gabriel Cole Ambrosio | 3126100300 |
| Henrique Capetto Fernandez | 3126103000 |
| Lucas Byoung Ki Han | 3025103388 |
| Sophie De Brito Zerbinati | 3126103086 |
| Eduardo Vieira Silva | 3026105026 |
| Riquelly Bagatin | 3025103463 |
| Matheus Nilcen Alves | 3026104544 |

## Documentação complementar

- Diagrama entidade-relacionamento: [banco-dados/DER_atual.svg](banco-dados/DER_atual.svg) e [banco-dados/DER_atual.mmd](banco-dados/DER_atual.mmd)
- Detalhes do backend Flask: [backend/README.md](backend/README.md)
- Especificação da integração Python ↔ C (`--relatorio`): [documentacao/CONTRATO_RELATORIO_C.md](documentacao/CONTRATO_RELATORIO_C.md)
- Roteiro de apresentação: [documentacao/apresentacao.md](documentacao/apresentacao.md)
- Equipe e autoria registrada nos arquivos: [documentacao/EQUIPE.md](documentacao/EQUIPE.md)
