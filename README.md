# Projeto de Extensao - Desenvolvimento de Software

**Turma Noturno 2026** | **Lider: Lucas Byoung Ki Han**

---

## Empresa - PixelShop

> **Nome:** PixelShop
> **Missao:** Oferecer produtos de eletrônicos e informática com qualidade e acessibilidade
> **Visao:** Ser referência em tecnologia acessível para estudantes e profissionais
> **Valores:** Inovação, Acessibilidade, Atendimento, Qualidade



---

## Equipe - 6 Integrantes

| # | Nome | RA | Squad | Responsabilidade Principal |
|---|------|----|-------|----------------------------|
| 1 | Lucas Byoung Ki Han | 3025103388 | Lider / Prog C | Coordenacao geral, Estrutura C, Logica de negocio, cadastros, busca e validacoes |
| 2 | Gabriel Cole Ambrosio | 3126100300 | Site | HTML: index, sobre, contato, produtos e portfolio |
| 3 | Eduardo Vieira Silva | Nao informado | Site | CSS completo (style.css) e Tema Dark Tech |
| 4 | Riquelly Barboza Bagatin | 3025103463 | Banco de Dados | Modelagem DER e integridade referencial |
| 5 | Henrique Capetto | 3126103000 | Banco de Dados | Scripts SQL Oracle e definicao das tabelas |
| 6 | Matheus Nilcen Alves | 3026104544 | Documentacao | Documento final escrito e prints |



## Cronograma

| Data | Entrega | Responsavel |
|------|---------|-------------|
| 12/03/2026 | Formacao da equipe + cronograma | Lider |
| 31/03/2026 | Site basico, C estruturado, DER | Squads |
| 30/04/2026 | Entrega parcial (2 pontos) | Todos |
| 25/05/2026 | Versao final + video gravado | Todos |
| 28/05/2026 | ENTREGA FINAL (8 pontos) | Lider posta |

---

## Estrutura do Repositorio

```
projeto-extensao-dev-software/
|
+-- site/                        Squad Site (Gabriel, Eduardo)
|   +-- index.html               Pagina Home
|   +-- sobre.html               Pagina Sobre
|   +-- produtos.html            Pagina Produtos/Servicos
|   +-- portfolio.html           Pagina Portfolio
|   +-- contato.html             Pagina Contato
|   +-- css/
|       +-- style.css            Estilos CSS completos
|   +-- img/                     Imagens do site
|
+-- programa-c/                  Squad C (Lucas)
|   +-- main.c                   Programa principal em C
|
+-- banco-dados/                 Squad BD (Riquelly, Henrique)
|   +-- create_tables.sql        Criacao das 5 tabelas
|   +-- insert_data.sql          Insercao de dados de exemplo
|   +-- queries.sql              10 consultas SELECT
|   +-- DER.png                  Diagrama Entidade-Relacionamento
|
+-- documentacao/                Squad Doc (Matheus)
    +-- LEIA-ME.md               Instrucoes para o Matheus
    +-- documento-final.pdf      (adicionar quando pronto)
    +-- organograma.png          (adicionar quando pronto)
```

---

## Como Usar Este Repositorio

### Clonar o projeto
```bash
git clone https://github.com/soloLucashan/projeto-extensao-dev-software.git
cd projeto-extensao-dev-software
```

### Fluxo de trabalho (OBRIGATORIO para todos)
```bash
# 1. Antes de comecar, atualize sua copia local
git pull origin main

# 2. Crie uma branch com seu nome/feature
git checkout -b nome-da-feature
# Exemplo: git checkout -b gabriel-pagina-home

# 3. Faca suas alteracoes na sua pasta

# 4. Salve as alteracoes
git add .
git commit -m "feat: descricao do que voce fez"

# 5. Envie para o GitHub
git push origin nome-da-feature

# 6. Abra um Pull Request no GitHub
# Va em: Pull requests > New pull request
# Mencione o lider: @soloLucashan para revisao
```

### Compilar o programa C
```bash
cd programa-c
gcc main.c -o programa
./programa
```

### Executar SQL no Oracle
```sql
-- Execute na ordem:
-- 1. create_tables.sql
-- 2. insert_data.sql
-- 3. queries.sql
```

---

## Regras do Repositorio

- Nunca faca push direto na branch `main`
- Sempre crie uma branch antes de editar
- Commits devem ter mensagens descritivas ("fix:", "feat:", "refactor:", "style:")
- Cada pessoa trabalha APENAS na sua localidade estipulada
- Duvidas? Manda no grupo do WhatsApp

---

## Links Importantes

- Repositorio: https://github.com/soloLucashan/projeto-extensao-dev-software
- Video final: [adicionar link YouTube quando pronto]
- Documento final: [adicionar link Drive quando pronto]

---

*Projeto desenvolvido para a disciplina de Extensao - Periodo Noturno 2026*
