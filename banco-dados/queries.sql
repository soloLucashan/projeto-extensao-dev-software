-- ============================================================
-- CONSULTAS SQL (SELECT) - Oracle SQL
-- Responsavel: Henrique Capetto
-- Projeto de Extensao - Turma Noturno 2026
-- ============================================================

-- 1. SELECT SIMPLES: Listar todos os clientes
SELECT * FROM CLIENTE;

-- 2. SELECT COM WHERE: Pedidos aprovados
SELECT * FROM PEDIDO WHERE status = 'APROVADO';

-- 3. SELECT COM WHERE: Produtos com preco acima de R$500
SELECT nome, preco, estoque
FROM PRODUTO
WHERE preco > 500
ORDER BY preco DESC;

-- 4. SELECT COM JOIN: Pedidos com nome do cliente e funcionario
SELECT
    p.id_pedido,
    c.nome        AS cliente,
    f.nome        AS funcionario,
    p.data_pedido,
    p.valor_total,
    p.status
FROM PEDIDO p
JOIN CLIENTE    c ON p.id_cliente     = c.id_cliente
JOIN FUNCIONARIO f ON p.id_funcionario = f.id_funcionario
ORDER BY p.data_pedido;

-- 5. SELECT COM JOIN: Produtos com nome da categoria
SELECT
    pr.nome     AS produto,
    pr.preco,
    pr.estoque,
    ca.nome     AS categoria
FROM PRODUTO pr
JOIN CATEGORIA ca ON pr.id_categoria = ca.id_categoria;

-- 6. SELECT COM COUNT: Total de pedidos por status
SELECT
    status,
    COUNT(*) AS total_pedidos
FROM PEDIDO
GROUP BY status
ORDER BY total_pedidos DESC;

-- 7. SELECT COM SUM: Faturamento total por funcionario
SELECT
    f.nome          AS funcionario,
    COUNT(p.id_pedido)  AS qtd_pedidos,
    SUM(p.valor_total)  AS faturamento_total
FROM PEDIDO p
JOIN FUNCIONARIO f ON p.id_funcionario = f.id_funcionario
GROUP BY f.nome
ORDER BY faturamento_total DESC;

-- 8. SELECT COM AVG: Ticket medio dos pedidos
SELECT
    ROUND(AVG(valor_total), 2) AS ticket_medio
FROM PEDIDO;

-- 9. SELECT COM MAX/MIN: Produto mais caro e mais barato
SELECT
    MAX(preco) AS produto_mais_caro,
    MIN(preco) AS produto_mais_barato
FROM PRODUTO;

-- 10. SELECT com subquery: Clientes que fizeram pedidos aprovados
SELECT nome, email
FROM CLIENTE
WHERE id_cliente IN (
    SELECT id_cliente FROM PEDIDO WHERE status = 'APROVADO'
);
