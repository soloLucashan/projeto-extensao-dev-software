-- PIXELSHOP - insercao de dados de exemplo
-- Eduardo Vieira Silva | Revisao: Riquelly
-- Projeto de Extensao - Noturno 2026
--
-- Execute DEPOIS do create_tables.sql.
-- ordem: 1=Smartphones, 2=Notebooks, 3=Perifericos, 4=Pecas
-- ---- CATEGORIAS ----
INSERT INTO CATEGORIA (nome_categoria)
VALUES ('Smartphones');
INSERT INTO CATEGORIA (nome_categoria)
VALUES ('Notebooks');
INSERT INTO CATEGORIA (nome_categoria)
VALUES ('Perifericos');
INSERT INTO CATEGORIA (nome_categoria)
VALUES ('Pecas e Componentes');
-- ---- PRODUTOS - Lote inicial ----
-- Smartphones (id_categoria = 1)
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'iPhone 13 Usado',
        'iPhone 13 64GB seminovo, excelente estado, sem marcas de uso',
        1899.90,
        5,
        1
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Samsung Galaxy A54',
        'Celular novo, 128GB, garantia de 1 ano direto com a Samsung',
        1299.00,
        8,
        1
    );
-- Notebooks (id_categoria = 2)
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Notebook Dell Inspiron',
        'Core i5, 8GB RAM, 256GB SSD, usado — bom custo-beneficio pra quem estuda',
        2199.00,
        3,
        2
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Notebook Lenovo IdeaPad',
        'Ryzen 5, 16GB RAM, 512GB SSD — configuracao solida pra desenvolvimento',
        2799.00,
        4,
        2
    );
-- perifericos (destaques no site)
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Mouse Logitech MX Master',
        'Mouse sem fio, ergonomico, sensor de alta precisao — top pra trabalho longo',
        349.90,
        12,
        3
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Teclado Mecanico Redragon',
        'Switch Red, RGB full, layout ABNT2 — o mais pedido pelos gamers da loja',
        279.90,
        10,
        3
    );
-- Pecas e Componentes (id_categoria = 4)
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Memoria RAM 8GB DDR4',
        'Pente avulso para upgrade — compativel com a maioria dos notebooks da loja',
        149.90,
        20,
        4
    );
-- ---- CLIENTES - Lote inicial ----
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Ana Paula Souza',
        'ana.souza@email.com',
        '(11) 91234-5678',
        'Rua das Flores, 123 - Sao Paulo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Carlos Eduardo Lima',
        'carlos.lima@email.com',
        '(11) 98765-4321',
        'Av. Paulista, 500 - Sao Paulo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Fernanda Oliveira',
        'fernanda.oli@email.com',
        '(11) 97654-3210',
        'Rua Augusta, 88 - Sao Paulo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Rafael Mendes',
        'rafael.m@email.com',
        '(11) 95555-1234',
        'Rua Vergueiro, 210 - Sao Paulo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Juliana Costa',
        'ju.costa@email.com',
        '(11) 94444-9876',
        'Rua Consolacao, 77 - Sao Paulo/SP'
    );
-- ---- PEDIDOS - Lote inicial ----
-- totais conferidos item a item antes do commit
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (1, DATE '2026-03-10', 'CONCLUIDO', 1899.90);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (2, DATE '2026-03-15', 'CONCLUIDO', 1928.80);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (3, DATE '2026-04-01', 'PENDENTE', 2199.00);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (4, DATE '2026-04-05', 'CONCLUIDO', 629.80);
-- ---- ITENS DOS PEDIDOS - Lote inicial ----
-- preco_unit registra o valor cobrado na data da venda;
-- importante pra historico financeiro mesmo que o preco do produto mude depois.
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (1, 1, 1, 1899.90);
-- Ana: iPhone 13
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (2, 2, 1, 1299.00);
-- Carlos: Galaxy A54
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (2, 5, 1, 349.90);
-- Carlos: Mouse MX Master
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (2, 6, 1, 279.90);
-- Carlos: Teclado Redragon
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (3, 3, 1, 2199.00);
-- Fernanda: Notebook Dell
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (4, 5, 1, 349.90);
-- Rafael: Mouse MX Master
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (4, 6, 1, 279.90);
-- Rafael: Teclado Redragon
--  PRODUTOS
-- Mais produtos para testar o BD
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Motorola Moto G52',
        'Smartphone Motorola 128GB, NFC, carregamento turbo',
        1099.00,
        15,
        1
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Xiaomi Redmi Note 12',
        'Celular Xiaomi 128GB Azul, tela AMOLED, bateria de 5000mAh',
        1199.90,
        20,
        1
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Samsung Galaxy S22',
        'Seminovo em perfeito estado, 256GB, camera de 50MP',
        2499.00,
        5,
        1
    );
-- Notebooks
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Notebook Acer Aspire 5',
        'Intel Core i5, 8GB, 256GB SSD — bom custo-beneficio',
        2599.00,
        10,
        2
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Notebook Asus VivoBook',
        'AMD Ryzen 7, 12GB, 512GB SSD — ideal pra designers',
        3199.00,
        7,
        2
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Notebook HP ProBook',
        'Intel Core i7, 16GB, 512GB SSD — linha corporativa',
        4299.00,
        4,
        2
    );
-- Perifericos
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Webcam Logitech C920',
        'Full HD 1080p, otima pra reunioes e live coding',
        399.90,
        12,
        3
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Headset Gamer HyperX',
        'Cloud Stinger Core, som surround, microfone com cancelamento de ruido',
        259.90,
        25,
        3
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'Monitor LED 21.5 pol LG',
        'Full HD HDMI, painel IPS, 75Hz — opcao economica pra home office',
        599.00,
        8,
        3
    );
-- Pecas e Componentes
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'HD Externo 1TB Seagate',
        'HD Portatil USB 3.0, backup e transporte de projetos pesados',
        329.90,
        18,
        4
    );
-- GPUs adicionadas pra sincronizar com o catalogo HTML (produtos.html).
-- Produtos adicionados para manter o catálogo do site alinhado ao banco.
-- id_produto gerado automaticamente sera 18 (RTX) e 19 (RX) nessa ordem.
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'NVIDIA RTX 3060 12GB GDDR6',
        '12GB GDDR6, 3584 CUDA Cores, Ray Tracing 2a geracao, DLSS 2.0',
        2399.00,
        4,
        4
    );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
        'AMD Radeon RX 6600 XT 8GB',
        '8GB GDDR6, 2048 Stream Processors, AMD FSR 2.0, ideal pra 1080p Ultra',
        1899.00,
        6,
        4
    );
-- ---- CLIENTES - Lote de expansao ----
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Pedro Henrique Alves',
        'pedro.alves@email.com',
        '(11) 91111-2222',
        'Jardim Jaqueline, 45 - Sao Paulo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Mariana Silva Costa',
        'mariana.costa@email.com',
        '(11) 92222-3333',
        'Campo Limpo, 102 - Sao Paulo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Lucas Santos',
        'lucas.santos@email.com',
        '(11) 93333-4444',
        'Vila Assuncao, 55 - Santo Andre/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Beatriz Gomes',
        'beatriz.gomes@email.com',
        '(11) 94444-5555',
        'Centro, 890 - Osasco/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Thiago Rodrigues',
        'thiago.rodrigues@email.com',
        '(11) 95555-6666',
        'Macedo, 12 - Guarulhos/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Camila Pereira',
        'camila.pereira@email.com',
        '(11) 96666-7777',
        'Rudge Ramos, 300 - Sao Bernardo do Campo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Joao Vitor Martins',
        'joaov.martins@email.com',
        '(11) 97777-8888',
        'Jardim Jaqueline, 210 - Sao Paulo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Leticia Ferreira',
        'leticia.ferreira@email.com',
        '(11) 98888-9999',
        'Campo Limpo, 404 - Sao Paulo/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Gabriel Almeida',
        'gabriel.almeida@email.com',
        '(11) 99999-1111',
        'Centro, 45 - Santo Andre/SP'
    );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
        'Amanda Ribeiro',
        'amanda.ribeiro@email.com',
        '(11) 90000-2222',
        'Jardim Florido, 77 - Osasco/SP'
    );
-- ---- PEDIDOS - Lote de expansao ----
-- totais conferidos um por um depois que percebemos que estavam errados
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (6, DATE '2026-04-02', 'CONCLUIDO', 1099.00);
-- Moto G52 (1099)
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (7, DATE '2026-04-03', 'PENDENTE', 2898.90);
-- Galaxy S22 (2499) + Webcam (399.90)
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (8, DATE '2026-04-04', 'CONCLUIDO', 3198.00);
-- Acer Aspire 5 (2599) + Monitor LG (599)
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (9, DATE '2026-04-05', 'CANCELADO', 3718.80);
-- Asus VivoBook (3199) + 2x HyperX (519.80)
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (10, DATE '2026-04-06', 'CONCLUIDO', 2729.70);
-- 2x Redmi Note 12 (2399.80) + HD Seagate (329.90)
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (11, DATE '2026-04-07', 'PENDENTE', 1198.00);
-- 2x Monitor LG (2 x 599)
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (12, DATE '2026-04-08', 'CONCLUIDO', 589.80);
-- HyperX (259.90) + HD Seagate (329.90)
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (15, DATE '2026-04-09', 'CONCLUIDO', 5297.90);
-- HP ProBook (4299) + Webcam (399.90) + Monitor LG (599)
-- ---- ITENS DOS PEDIDOS - Lote de expansao ----
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (5, 8, 1, 1099.00);
-- Moto G52
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (6, 10, 1, 2499.00);
-- Galaxy S22
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (6, 14, 1, 399.90);
-- Webcam C920
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (7, 11, 1, 2599.00);
-- Acer Aspire 5
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (7, 16, 1, 599.00);
-- Monitor LG
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (8, 12, 1, 3199.00);
-- Asus VivoBook
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (8, 15, 2, 259.90);
-- 2x HyperX
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (9, 9, 2, 1199.90);
-- 2x Redmi Note 12
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (9, 17, 1, 329.90);
-- HD Seagate
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (10, 16, 2, 599.00);
-- 2x Monitor LG
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (11, 15, 1, 259.90);
-- HyperX
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (11, 17, 1, 329.90);
-- HD Seagate
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (12, 13, 1, 4299.00);
-- HP ProBook
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (12, 14, 1, 399.90);
-- Webcam C920
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (12, 16, 1, 599.00);
-- Monitor LG
COMMIT;
