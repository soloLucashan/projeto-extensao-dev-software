# Projeto de Extensao - Desenvolvimento de Software

**Turma Noturno 2026** | **Lider: Lucas Byoung Ki Han**

---

## Empresa

> **Nome:** [PixelShop]
> **Missao:** [Oferecer produtos de eletrônicos e informática com qualidade e acessibilidade]
> **Visao:** [Ser referência em tecnologia acessível para estudantes e profissionais]
> **Valores:** [Inovação, Acessibilidade, Atendimento, Qualidade

]

---

## Equipe - 9 Integrantes

| # | Nome | RA | Squad | Responsabilidade Principal |
|---|------|----|-------|----------------------------|
| 1 | Lucas Byoung Ki Han | 3025103388 | Lider / Doc | Coordenacao geral + video |
| 2 | Gabriel Cole Ambrosio | 3126100300 | Site | HTML: index, sobre, contato |
| 3 | Luiz Augusto Tiburcio | 3026102233 | Site | HTML: produtos, portfolio |
| 4 | Eduardo Vieira Silva | [RA] | Site | CSS completo (style.css) |
| 5 | Willian Soares Santana | [RA] | Programa C | Estrutura principal, menu e validacoes |
| 6 | Guilherme Huilame | [RA] | Programa C | Logica de negocio, cadastros, busca e comentarios |
| 7 | Riquelly Barboza Bagatin | [RA] | Banco de Dados | Modelagem DER |
| 8 | Henrique Capetto | [RA] | Banco de Dados | Scripts SQL Oracle |
| 9 | Matheus Nilcen Alves | [RA] | Documentacao | Documento final escrito |

---

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
+-- site/                        Squad Site (Gabriel, Luiz, Eduardo)
|   +-- index.html               Pagina Home
|   +-- sobre.html               Pagina Sobre
|   +-- produtos.html            Pagina Produtos/Servicos
|   +-- portfolio.html           Pagina Portfolio
|   +-- contato.html             Pagina Contato
|   +-- css/
|       +-- style.css            Estilos CSS completos
|
+-- programa-c/                  Squad C (Willian, Guilherme)
|   +-- main.c                   Programa principal em C
|
+-- banco-dados/                 Squad BD (Riquelly, Henrique)
|   +-- create_tables.sql        Criacao das 5 tabelas
|   +-- insert_data.sql          Insercao de dados de exemplo
|   +-- queries.sql              10 consultas SELECT
|
+-- documentacao/                Squad Doc (Matheus + Lider)
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
- Commits devem ter mensagens descritivas
- Cada pessoa trabalha APENAS na sua pasta
- Duvidas? Manda no grupo do WhatsApp

---

## Links Importantes

- Repositorio: https://github.com/soloLucashan/projeto-extensao-dev-software
- Video final: [adicionar link YouTube quando pronto]
- Documento final: [adicionar link Drive quando pronto]

---

*Projeto desenvolvido para a disciplina de Extensao - Periodo Noturno 2026*
