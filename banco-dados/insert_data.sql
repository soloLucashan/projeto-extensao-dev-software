-- ============================================
-- PIXELSHOP - Insercao de Dados de Exemplo
-- ============================================
-- Categorias
INSERT INTO CATEGORIA (nome_categoria)
VALUES ('Smartphones');
INSERT INTO CATEGORIA (nome_categoria)
VALUES ('Notebooks');
INSERT INTO CATEGORIA (nome_categoria)
VALUES ('Periféricos');
INSERT INTO CATEGORIA (nome_categoria)
VALUES ('Peças e Componentes');
-- Produtos
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'iPhone 13 Usado',
    'iPhone 13 64GB seminovo, excelente estado',
    1899.90,
    5,
    1
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Samsung Galaxy A54',
    'Celular novo, 128GB, garantia de 1 ano',
    1299.00,
    8,
    1
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Notebook Dell Inspiron',
    'Core i5, 8GB RAM, 256GB SSD, usado',
    2199.00,
    3,
    2
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Notebook Lenovo IdeaPad',
    'Ryzen 5, 16GB RAM, 512GB SSD',
    2799.00,
    4,
    2
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Mouse Logitech MX Master',
    'Mouse sem fio, ergonômico',
    349.90,
    12,
    3
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Teclado Mecânico Redragon',
    'Switch Red, RGB, ABNT2',
    279.90,
    10,
    3
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Memória RAM 8GB DDR4',
    'Memória para upgrade de computadores',
    149.90,
    20,
    4
  );
-- Clientes
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Ana Paula Souza',
    'ana.souza@email.com',
    '(11) 91234-5678',
    'Rua das Flores, 123 - São Paulo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Carlos Eduardo Lima',
    'carlos.lima@email.com',
    '(11) 98765-4321',
    'Av. Paulista, 500 - São Paulo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Fernanda Oliveira',
    'fernanda.oli@email.com',
    '(11) 97654-3210',
    'Rua Augusta, 88 - São Paulo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Rafael Mendes',
    'rafael.m@email.com',
    '(11) 95555-1234',
    'Rua Vergueiro, 210 - São Paulo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Juliana Costa',
    'ju.costa@email.com',
    '(11) 94444-9876',
    'Rua Consolação, 77 - São Paulo/SP'
  );
-- Pedidos
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (1, DATE '2026-03-10', 'CONCLUIDO', 1899.90);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (2, DATE '2026-03-15', 'CONCLUIDO', 2478.90);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (3, DATE '2026-04-01', 'PENDENTE', 2199.00);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (4, DATE '2026-04-05', 'CONCLUIDO', 429.80);
-- Itens dos Pedidos
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (1, 1, 1, 1899.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (2, 2, 1, 1299.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (2, 5, 1, 349.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (2, 6, 1, 279.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (3, 3, 1, 2199.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (4, 5, 1, 349.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (4, 6, 1, 279.90);
-- Novos Produtos (deu uma canseira)
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Motorola Moto G52',
    'Smartphone Motorola 128GB',
    1099.00,
    15,
    1
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Xiaomi Redmi Note 12',
    'Celular Xiaomi 128GB Azul',
    1199.90,
    20,
    1
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Samsung Galaxy S22',
    'Seminovo em perfeito estado',
    2499.00,
    5,
    1
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Notebook Acer Aspire 5',
    'Intel Core i5, 8GB, 256GB SSD',
    2599.00,
    10,
    2
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Notebook Asus VivoBook',
    'AMD Ryzen 7, 12GB, 512GB SSD',
    3199.00,
    7,
    2
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Notebook HP ProBook',
    'Intel Core i7, 16GB, 512GB SSD',
    4299.00,
    4,
    2
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Webcam Logitech C920',
    'Webcam Full HD 1080p',
    399.90,
    12,
    3
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Headset Gamer HyperX',
    'Cloud Stinger Core',
    259.90,
    25,
    3
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'Monitor LED 21.5" LG',
    'Monitor Full HD HDMI',
    599.00,
    8,
    3
  );
INSERT INTO PRODUTO (nome, descricao, preco, estoque, id_categoria)
VALUES (
    'HD Externo 1TB Seagate',
    'HD Portátil USB 3.0',
    329.90,
    18,
    4
  );
-- Novos Clientes
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Pedro Henrique Alves',
    'pedro.alves@email.com',
    '(11) 91111-2222',
    'Jardim Jaqueline, 45 - São Paulo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Mariana Silva Costa',
    'mariana.costa@email.com',
    '(11) 92222-3333',
    'Campo Limpo, 102 - São Paulo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Lucas Santos',
    'lucas.santos@email.com',
    '(11) 93333-4444',
    'Vila Assunção, 55 - Santo André/SP'
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
    'Rudge Ramos, 300 - São Bernardo do Campo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'João Vitor Martins',
    'joaov.martins@email.com',
    '(11) 97777-8888',
    'Jardim Jaqueline, 210 - São Paulo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Leticia Ferreira',
    'leticia.ferreira@email.com',
    '(11) 98888-9999',
    'Campo Limpo, 404 - São Paulo/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Gabriel Almeida',
    'gabriel.almeida@email.com',
    '(11) 99999-1111',
    'Centro, 45 - Santo André/SP'
  );
INSERT INTO CLIENTE (nome, email, telefone, endereco)
VALUES (
    'Amanda Ribeiro',
    'amanda.ribeiro@email.com',
    '(11) 90000-2222',
    'Jardim Florido, 77 - Osasco/SP'
  );
-- Novos Pedidos
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (6, DATE '2026-04-02', 'CONCLUIDO', 1099.00);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (7, DATE '2026-04-03', 'PENDENTE', 2898.90);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (8, DATE '2026-04-04', 'CONCLUIDO', 3198.00);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (9, DATE '2026-04-05', 'CANCELADO', 3718.80);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (10, DATE '2026-04-06', 'CONCLUIDO', 2729.70);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (11, DATE '2026-04-07', 'PENDENTE', 1198.00);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (12, DATE '2026-04-08', 'CONCLUIDO', 589.80);
INSERT INTO PEDIDO (id_cliente, data_pedido, status, total)
VALUES (15, DATE '2026-04-09', 'CONCLUIDO', 5297.90);
-- Novos Itens dos Pedidos
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (5, 8, 1, 1099.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (6, 10, 1, 2499.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (6, 14, 1, 399.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (7, 11, 1, 2599.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (7, 16, 1, 599.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (8, 12, 1, 3199.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (8, 15, 2, 259.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (9, 9, 2, 1199.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (9, 17, 1, 329.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (10, 16, 2, 599.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (11, 15, 1, 259.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (11, 17, 1, 329.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (12, 13, 1, 4299.00);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (12, 14, 1, 399.90);
INSERT INTO ITEM_PEDIDO (id_pedido, id_produto, quantidade, preco_unit)
VALUES (12, 16, 1, 599.00);
COMMIT;