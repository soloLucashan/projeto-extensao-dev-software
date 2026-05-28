
-- PIXELSHOP - Consultas SQL para Relatorios e Gestao
-- Responsavel: Luiz Augusto Tiburcio
-- Projeto de Extensao - Turma Noturno 2026



--1. Lista de clientes ordenada por nome
SELECT id_cliente,
    nome,
    email,
    telefone
FROM CLIENTE
ORDER BY nome;
-- 2. Catalogo completo com categoria e estoque
--    O JOIN com CATEGORIA e necessario pra mostrar o nome legivel
--    em vez do id_categoria, que nao faz sentido pro usuario final.
SELECT p.id_produto,
    p.nome,
    c.nome_categoria AS categoria,
    p.preco,
    p.estoque
FROM PRODUTO p
    JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
ORDER BY c.nome_categoria,
    p.nome;
-- 3. Historico de pedidos com nome do cliente
--    DESC em data_pedido pra mostrar os mais recentes primeiro
SELECT pd.id_pedido,
    cl.nome AS cliente,
    pd.data_pedido,
    pd.status,
    pd.total
FROM PEDIDO pd
    JOIN CLIENTE cl ON pd.id_cliente = cl.id_cliente
ORDER BY pd.data_pedido DESC;
-- 4. Detalhamento de itens por pedido com subtotal calculado
--    subtotal = quantidade * preco_unit (preco da epoca da compra,
--    nao o preco atual do produto — importante pra auditoria financeira).
SELECT pd.id_pedido,
    cl.nome AS cliente,
    pr.nome AS produto,
    ip.quantidade,
    ip.preco_unit,
    (ip.quantidade * ip.preco_unit) AS subtotal
FROM ITEM_PEDIDO ip
    JOIN PEDIDO pd ON ip.id_pedido = pd.id_pedido
    JOIN CLIENTE cl ON pd.id_cliente = cl.id_cliente
    JOIN PRODUTO pr ON ip.id_produto = pr.id_produto
ORDER BY pd.id_pedido;
-- 5. Produtos em alerta critico de estoque (menos de 3 unidades)
--    Esse limite de 3 unidades e o mesmo usado no sistema C (main.c,
--    funcao relatorioEstoque) — manter sincronizado com a regra de negocio.
SELECT nome,
    estoque,
    preco
FROM PRODUTO
WHERE estoque < 3
ORDER BY estoque;
-- 6. Total gasto por cliente (apenas pedidos CONCLUIDOS)
--    Filtramos CANCELADO e PENDENTE porque esses valores ainda
--    nao saíram do caixa de fato.
SELECT cl.nome AS cliente,
    COUNT(pd.id_pedido) AS qtd_pedidos,
    SUM(pd.total) AS valor_total
FROM CLIENTE cl
    JOIN PEDIDO pd ON cl.id_cliente = pd.id_cliente
WHERE pd.status = 'CONCLUIDO'
GROUP BY cl.id_cliente, cl.nome, cl.email
ORDER BY valor_total DESC;
-- 7. Produtos mais vendidos (ranking por unidades comercializadas)
SELECT pr.nome AS produto,
    SUM(ip.quantidade) AS total_unidades_vendidas
FROM PRODUTO pr
    JOIN ITEM_PEDIDO ip ON pr.id_produto = ip.id_produto
GROUP BY pr.nome
ORDER BY total_unidades_vendidas DESC;
-- 8. Receita total gerada por categoria de produto
--    Util pra decisao de qual linha de produto merece mais investimento
--    no proximo ciclo de compras com os fornecedores.
SELECT ca.nome_categoria AS categoria,
    SUM(ip.quantidade * ip.preco_unit) AS total_arrecadado
FROM CATEGORIA ca
    JOIN PRODUTO pr ON ca.id_categoria = pr.id_categoria
    JOIN ITEM_PEDIDO ip ON pr.id_produto = ip.id_produto
    JOIN PEDIDO pd ON ip.id_pedido = pd.id_pedido
    WHERE pd.status = 'CONCLUIDO' -- considera apenas vendas efetivadas de fato
GROUP BY ca.nome_categoria
ORDER BY total_arrecadado DESC;
-- 9. Clientes que nunca fizeram pedido
--    Serve pra identificar cadastros inativos — possivelmente
--    clientes que vieram so pra ver o preco e nao voltaram.
SELECT cl.nome,
    cl.email
FROM CLIENTE cl
    LEFT JOIN PEDIDO pd ON cl.id_cliente = pd.id_cliente
WHERE pd.id_pedido IS NULL;
-- 10. Ticket medio dos pedidos concluidos
SELECT AVG(total) AS ticket_medio
FROM PEDIDO
WHERE status = 'CONCLUIDO';
