-- ============================================
-- PIXELSHOP - Consultas SQL
-- ============================================
-- 1. Listagem completa de clientes
SELECT id_cliente,
    nome,
    email,
    telefone
FROM CLIENTE
ORDER BY nome;
-- 2. Catalogo de produtos com categoria e estoque
SELECT p.id_produto,
    p.nome,
    c.nome_categoria,
    p.preco,
    p.estoque
FROM PRODUTO p
    JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
ORDER BY c.nome_categoria,
    p.nome;
-- 3. Pedidos com nome do cliente e status
SELECT pd.id_pedido,
    cl.nome AS cliente,
    pd.data_pedido,
    pd.status,
    pd.total
FROM PEDIDO pd
    JOIN CLIENTE cl ON pd.id_cliente = cl.id_cliente
ORDER BY pd.data_pedido DESC;
-- 4. Itens de cada pedido com detalhes do produto
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
-- 5. Produtos com estoque baixo (menos de 5 unidades)
SELECT nome,
    estoque,
    preco
FROM PRODUTO
WHERE estoque < 5
ORDER BY estoque;
-- 6. Total gasto por cliente
SELECT cl.nome AS cliente,
    COUNT(pd.id_pedido) AS quantidade_pedidos,
    SUM(pd.total) AS valor_total
FROM CLIENTE cl
    JOIN PEDIDO pd ON cl.id_cliente = pd.id_cliente
WHERE pd.status = 'CONCLUIDO'
GROUP BY cl.nome
ORDER BY valor_total DESC;
-- 7. Produtos mais vendidos
SELECT pr.nome AS produto,
    SUM(ip.quantidade) AS total_unidades_vendidas
FROM PRODUTO pr
    JOIN ITEM_PEDIDO ip ON pr.id_produto = ip.id_produto
GROUP BY pr.nome
ORDER BY total_unidades_vendidas DESC;
-- 8. Receita total por categoria
SELECT ca.nome_categoria AS categoria,
    SUM(ip.quantidade * ip.preco_unit) AS total_arrecadado
FROM CATEGORIA ca
    JOIN PRODUTO pr ON ca.id_categoria = pr.id_categoria
    JOIN ITEM_PEDIDO ip ON pr.id_produto = ip.id_produto
    JOIN PEDIDO pd ON ip.id_pedido = pd.id_pedido
GROUP BY ca.nome_categoria
ORDER BY total_arrecadado DESC;
-- 9. Clientes que nunca fizeram pedido
SELECT cl.nome,
    cl.email
FROM CLIENTE cl
    LEFT JOIN PEDIDO pd ON cl.id_cliente = pd.id_cliente
WHERE pd.id_pedido IS NULL;