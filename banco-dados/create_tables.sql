-- PIXELSHOP - criacao das tabelas (Oracle LiveSQL)
-- Henrique Capetto | Projeto de Extensao - Noturno 2026
--
-- Execute ANTES de qualquer INSERT.
-- Ordem importa por causa das FK:
--   CATEGORIA -> PRODUTO -> ITEM_PEDIDO
--   CLIENTE   -> PEDIDO  -> ITEM_PEDIDO
CREATE TABLE CATEGORIA (
    id_categoria NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome_categoria VARCHAR2(100) NOT NULL UNIQUE
);
CREATE TABLE PRODUTO (
    id_produto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR2(100) NOT NULL,
    descricao VARCHAR2(300),
    preco NUMBER(10, 2) NOT NULL CHECK (preco >= 0),
    estoque NUMBER(5) DEFAULT 0 CHECK (estoque >= 0),
    id_categoria NUMBER NOT NULL,
    CONSTRAINT fk_categoria FOREIGN KEY (id_categoria) REFERENCES CATEGORIA(id_categoria)
);
-- clientes da loja (email unico pra uso como login futuro)
CREATE TABLE CLIENTE (
    id_cliente NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR2(150) NOT NULL,
    email VARCHAR2(150) NOT NULL UNIQUE,
    telefone VARCHAR2(20),
    endereco VARCHAR2(250)
);
-- pedidos: status pode ser PENDENTE, CONCLUIDO ou CANCELADO
CREATE TABLE PEDIDO (
    id_pedido NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente NUMBER NOT NULL,
    data_pedido DATE DEFAULT SYSDATE,
    status VARCHAR2(20) DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE', 'CONCLUIDO', 'CANCELADO')),
    total NUMBER(10, 2) DEFAULT 0 CHECK (total >= 0),
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente)
);
-- itens de cada pedido (preco_unit registra o valor na data da venda)
CREATE TABLE ITEM_PEDIDO (
    id_item NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pedido NUMBER NOT NULL,
    id_produto NUMBER NOT NULL,
    quantidade NUMBER(5) NOT NULL CHECK (quantidade > 0),
    preco_unit NUMBER(10, 2) NOT NULL CHECK (preco_unit >= 0),
    CONSTRAINT fk_item_pedido FOREIGN KEY (id_pedido) REFERENCES PEDIDO(id_pedido),
    CONSTRAINT fk_item_produto FOREIGN KEY (id_produto) REFERENCES PRODUTO(id_produto)
);
