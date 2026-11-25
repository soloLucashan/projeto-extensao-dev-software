-- PIXELSHOP - Verificacoes somente leitura apos a carga inicial.

-- 1. Contagens esperadas: CATEGORIA=4, PRODUTO=19, CLIENTE=15, PEDIDO=12, ITEM_PEDIDO=22
SELECT 'CATEGORIA' AS tabela, COUNT(*) AS total FROM CATEGORIA
UNION ALL
SELECT 'PRODUTO' AS tabela, COUNT(*) AS total FROM PRODUTO
UNION ALL
SELECT 'CLIENTE' AS tabela, COUNT(*) AS total FROM CLIENTE
UNION ALL
SELECT 'PEDIDO' AS tabela, COUNT(*) AS total FROM PEDIDO
UNION ALL
SELECT 'ITEM_PEDIDO' AS tabela, COUNT(*) AS total FROM ITEM_PEDIDO;

-- 2. Divergencias entre PEDIDO.total e soma dos itens (esperado: 0 linhas)
SELECT pd.id_pedido,
    pd.total AS total_pedido,
    NVL(SUM(ip.quantidade * ip.preco_unit), 0) AS soma_itens
FROM PEDIDO pd
    LEFT JOIN ITEM_PEDIDO ip ON pd.id_pedido = ip.id_pedido
GROUP BY pd.id_pedido,
    pd.total
HAVING pd.total <> NVL(SUM(ip.quantidade * ip.preco_unit), 0);

-- 3. Vinculos de IDs gerados nos itens-chave do catalogo e pedidos
SELECT p.id_produto,
    p.nome,
    c.nome_categoria AS categoria,
    p.preco,
    p.estoque
FROM PRODUTO p
    JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
WHERE p.id_produto IN (3, 5, 18, 19)
ORDER BY p.id_produto;

-- 4. Distribuicao por estado de estoque (esperado: ESGOTADO=1, CRITICO=1, DISPONIVEL=17)
SELECT CASE
        WHEN estoque <= 0 THEN 'ESGOTADO'
        WHEN estoque < 3 THEN 'CRITICO'
        ELSE 'DISPONIVEL'
    END AS estado,
    COUNT(*) AS quantidade
FROM PRODUTO
GROUP BY CASE
        WHEN estoque <= 0 THEN 'ESGOTADO'
        WHEN estoque < 3 THEN 'CRITICO'
        ELSE 'DISPONIVEL'
    END
ORDER BY estado;
