-- ============================================================
-- CRIACAO DAS TABELAS - Oracle SQL
-- Responsavel: Henrique Capetto
-- Projeto de Extensao - Turma Noturno 2026
-- ============================================================
-- EXECUTE ESTE SCRIPT ANTES DOS OUTROS!
-- ============================================================
-- Tabela: CATEGORIA
CREATE TABLE CATEGORIA (
    id_categoria NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome_categoria VARCHAR2(100) NOT NULL
);
-- Tabela: PRODUTO
CREATE TABLE PRODUTO (
    id_produto NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR2(100) NOT NULL,
    descricao VARCHAR2(300),
    preco NUMBER(10, 2) NOT NULL,
    estoque NUMBER(5) DEFAULT 0,
    id_categoria NUMBER,
    CONSTRAINT fk_categoria FOREIGN KEY (id_categoria) REFERENCES CATEGORIA(id_categoria)
);
-- Tabela: CLIENTE
CREATE TABLE CLIENTE (
    id_cliente NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR2(150) NOT NULL,
    email VARCHAR2(150) NOT NULL UNIQUE,
    telefone VARCHAR2(20),
    endereco VARCHAR2(250)
);
-- Tabela: PEDIDO
CREATE TABLE PEDIDO (
    id_pedido NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente NUMBER NOT NULL,
    data_pedido DATE DEFAULT SYSDATE,
    status VARCHAR2(20) DEFAULT 'PENDENTE',
    total NUMBER(10, 2),
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente)
);
-- Tabela: ITEM_PEDIDO
CREATE TABLE ITEM_PEDIDO (
    id_item NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pedido NUMBER NOT NULL,
    id_produto NUMBER NOT NULL,
    quantidade NUMBER(5) NOT NULL,
    preco_unit NUMBER(10, 2) NOT NULL,
    CONSTRAINT fk_item_pedido FOREIGN KEY (id_pedido) REFERENCES PEDIDO(id_pedido),
    CONSTRAINT fk_item_produto FOREIGN KEY (id_produto) REFERENCES PRODUTO(id_produto)
);