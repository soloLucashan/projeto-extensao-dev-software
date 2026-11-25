# Roteiro de apresentação — PixelShop

Sequência curta para demonstrar o projeto integrado sem alterar os dados do banco. Para instalação completa, consulte [README.md](../README.md); para os detalhes do protocolo com o programa C, veja [CONTRATO_RELATORIO_C.md](CONTRATO_RELATORIO_C.md).

## Camadas do sistema

- Banco Oracle (`banco-dados/`): mantém as cinco tabelas (`CATEGORIA`, `PRODUTO`, `CLIENTE`, `PEDIDO` e `ITEM_PEDIDO`) no PDB `XEPDB1`, esquema `PIXELSHOP`.
- Backend Flask (`backend/`): serve as páginas estáticas de `site/`, consulta o catálogo via `backend/db.py` (em `Decimal`) para `/produtos.html` e aciona o módulo C por meio de `backend/integracao_c.py`.
- Módulo C (`programa-c/main.c`, compilado em `programa-c/build/main_bloco2.exe`): abre o menu de terminal em memória quando executado sem argumentos e calcula o resumo em JSON no modo `--relatorio`.

## Sequência sugerida

1. Página inicial (`http://127.0.0.1:5000/`): apresentar o objetivo acadêmico do sistema e explicar a diferença entre a vitrine estática inicial e as páginas ligadas ao banco de dados.
2. Catálogo (`/produtos.html`): clicar em `Ver Catálogo Completo`, mostrar os produtos vindos do Oracle agrupados por categoria e abrir `#produto-3` (`Notebook Dell Inspiron`, `⚠ Últimas unidades (2)`) e `#produto-19` (`AMD Radeon RX 6600 XT 8GB`, `✕ Esgotado`).
3. Relatório de estoque (`/relatorio.html`): acessar `Ver Relatório de Estoque (Módulo C)`, mostrar os indicadores consolidados (`19` produtos distintos, `189` unidades e `R$ 195.660,80`) e explicar que as somas e a regra de estoque crítico (`< 3`, incluindo `0`) vêm de `main_bloco2.exe --relatorio` em centavos inteiros. Se o Oracle ou o executável falhar, a rota devolve HTTP `503` sem inventar totais zerados.
4. Conferência SQL opcional (somente leitura): conectado como `PIXELSHOP` em `XEPDB1`, executar a consulta nº 5 (`WHERE estoque < 3`) de [queries.sql](../banco-dados/queries.sql) e comparar os totais da tela com:
   ```sql
   SELECT COUNT(*) AS total_produtos,
          SUM(estoque) AS total_unidades,
          SUM(preco * estoque) AS valor_estoque
     FROM PRODUTO;
   ```
5. Menu interativo em C: executar `programa-c\build\main_bloco2.exe` sem argumentos no terminal, cadastrar dois produtos para mostrar os IDs sequenciais e sair com `0`, ressaltando que esse modo funciona apenas em memória.
6. Modelo de dados e limites: mostrar [DER_atual.svg](../banco-dados/DER_atual.svg), explicar a correspondência com as tabelas criadas, a diferença entre a cardinalidade física no banco (`0..N`) e a regra de negócio esperada (`1..N` itens por pedido) e os recursos fora do escopo (carrinho, checkout, autenticação e painel administrativo).
