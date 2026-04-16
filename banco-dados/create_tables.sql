-- ============================================================
-- PIXELSHOP - Criacao das Tabelas (Oracle LiveSQL)
-- Responsavel: Henrique Capetto
-- Projeto de Extensao - Turma Noturno 2026
-- ============================================================
-- IMPORTANTE: execute este script ANTES de qualquer INSERT.
-- A ordem importa por causa das chaves estrangeiras:
--   CATEGORIA -> PRODUTO -> ITEM_PEDIDO
--   CLIENTE   -> PEDIDO  -> ITEM_PEDIDO
-- ============================================================

-- Tabela CATEGORIA: centraliza os tipos de produto que a PixelShop
-- comercializa. Manter aqui evita duplicidade de nomes nas telas
-- e facilita filtros no relatorio de estoque do sistema em C.
CREATE TABLE CATEGORIA (
    id_categoria   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome_categoria VARCHAR2(100) NOT NULL
);

-- Tabela PRODUTO: cada item do catalogo pertence a uma categoria.
-- O campo estoque reflete o mesmo limite de alerta usado no main.c
-- (menos de 3 unidades = alerta critico de reposicao).
-- Constraint fk_categoria revisada pela Riquelly.
CREATE TABLE PRODUTO (
    id_produto  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome        VARCHAR2(100) NOT NULL,
    descricao   VARCHAR2(300),
    preco       NUMBER(10, 2) NOT NULL,
    estoque     NUMBER(5)     DEFAULT 0,
    id_categoria NUMBER,
    CONSTRAINT fk_categoria FOREIGN KEY (id_categoria)
        REFERENCES CATEGORIA(id_categoria)
);

-- TODO (Henrique): adicionar CHECK constraint na coluna estoque
--   pra impedir valores negativos diretamente no banco, sem depender
--   so da validacao do sistema em C.

-- Tabela CLIENTE: guarda os dados de contato dos compradores.
-- O email e UNIQUE porque usamos ele como login no fluxo futuro.
CREATE TABLE CLIENTE (
    id_cliente NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome       VARCHAR2(150) NOT NULL,
    email      VARCHAR2(150) NOT NULL UNIQUE,
    telefone   VARCHAR2(20),
    endereco   VARCHAR2(250)
);

-- Tabela PEDIDO: registra cada compra feita por um cliente.
-- O campo status aceita: PENDENTE, CONCLUIDO, CANCELADO.
-- Constraint fk_pedido_cliente revisada pela Riquelly.
CREATE TABLE PEDIDO (
    id_pedido  NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente NUMBER       NOT NULL,
    data_pedido DATE        DEFAULT SYSDATE,
    status      VARCHAR2(20) DEFAULT 'PENDENTE',
    total       NUMBER(10, 2),
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (id_cliente)
        REFERENCES CLIENTE(id_cliente)
);

-- Tabela ITEM_PEDIDO: detalha quais produtos estao em cada pedido
-- e quantas unidades. preco_unit captura o preco da epoca da compra
-- — necessario porque o preco de venda pode mudar depois.
-- Constraints de FK revisadas pela Riquelly.
CREATE TABLE ITEM_PEDIDO (
    id_item    NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_pedido  NUMBER NOT NULL,
    id_produto NUMBER NOT NULL,
    quantidade NUMBER(5)     NOT NULL,
    preco_unit NUMBER(10, 2) NOT NULL,
    CONSTRAINT fk_item_pedido  FOREIGN KEY (id_pedido)  REFERENCES PEDIDO(id_pedido),
    CONSTRAINT fk_item_produto FOREIGN KEY (id_produto) REFERENCES PRODUTO(id_produto)
);