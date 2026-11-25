# Backend (Flask + Oracle + Integração C)

Aplicação web em Python/Flask da PixelShop que serve os arquivos estáticos de `site/`, consulta o catálogo no banco Oracle e aciona o executável C (`programa-c/build/main_bloco2.exe --relatorio`) para consolidar o relatório de estoque. Veja também a visão completa em [README.md](../README.md).

---

## Estrutura

| Caminho | Responsabilidade |
|---|---|
| `app.py` | Rotas `/`, `/produtos.html` e `/relatorio.html`; formatação monetária (`brl`); agrupamento por categoria; servidor local em `127.0.0.1:5000` (`debug=False`, `use_reloader=False`). |
| `db.py` | Carregamento explícito de `backend/.env` e consultas Oracle com `oracledb` preservando preços em `Decimal`. |
| `integracao_c.py` | Validação e conversão `Decimal → centavos`, execução controlada do módulo C (`timeout=5`, sem herdar variáveis `ORACLE_*`) e validação estrita do JSON retornado. |
| `templates/` | Templates Jinja2 para `produtos.html` (catálogo oficial) e `relatorio.html` (resumo consolidado pelo C). |
| `tests/` | Suíte isolada **sem Oracle** (regras de catálogo, configuração Oracle, conversão/validação C, chamadas reais ao binário C e coerência da interface). |
| `tests_integracao/` | Suíte **opt-in** somente leitura contra o Oracle real (`PIXELSHOP_RUN_ORACLE_TESTS=1`). |
| `requirements.txt` | Dependências diretas mínimas (`Flask>=3.0`, `oracledb>=2.0`, `python-dotenv>=1.0`). |
| `requirements-lock.txt` | Versões exatas validadas no ambiente Python `3.14.5` (Windows 11 Pro 64 bits). |

---

## Instalação e Execução (Windows)

A partir da raiz do projeto:

1. **Criar `.venv` e instalar dependências:**
   ```powershell
   python -m venv backend\.venv
   backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
   ```
2. **Garantir o executável C compilado** em `programa-c\build\main_bloco2.exe`:
   ```powershell
   New-Item -ItemType Directory -Force -Path programa-c\build | Out-Null
   gcc -std=c11 -Wall -Wextra -Wpedantic programa-c\main.c -o programa-c\build\main_bloco2.exe
   ```
3. **Criar `backend\.env` sem sobrescrever arquivo existente:**
   ```powershell
   if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
   notepad backend\.env
   ```
   Preencha `ORACLE_USER=PIXELSHOP`, sua `ORACLE_PASSWORD` local e o `ORACLE_DSN` do seu ambiente (`127.0.0.1:1522/XEPDB1` no ambiente validado localmente; em outras instalações, verifique se o Listener usa `1521` ou outra porta).
4. **Executar o servidor Flask local:**
   ```powershell
   Set-Location backend
   .\.venv\Scripts\python.exe app.py
   ```
   Acesse `http://127.0.0.1:5000/produtos.html` e `http://127.0.0.1:5000/relatorio.html`. Para encerrar, pressione `Ctrl+C`.

---

## Testes

- **Suíte isolada (sem Oracle; inclui chamadas reais ao `main_bloco2.exe`):**
  ```powershell
  Set-Location backend
  .\.venv\Scripts\python.exe -m unittest discover -s tests -v
  ```
- **Suíte de integração real com Oracle (opt-in, somente leitura):**
  ```powershell
  Set-Location backend
  $env:PIXELSHOP_RUN_ORACLE_TESTS='1'
  .\.venv\Scripts\python.exe -m unittest discover -s tests_integracao -v
  ```

---

## Convenções de Segurança e Manutenção

- Todas as consultas SQL permanecem centralizadas em `db.py` com parâmetros ligados (`:param`), sem concatenação de entrada em queries.
- Nunca leia, imprima, compartilhe ou inclua `backend/.env` em repositórios ou pacotes de envio.
- O cálculo dos totais e alertas do relatório em `/relatorio.html` segue o contrato definido em [CONTRATO_RELATORIO_C.md](../documentacao/CONTRATO_RELATORIO_C.md), sem recálculo silencioso em Python em caso de falha no módulo C.
