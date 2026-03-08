-- ============================================================
-- CRIACAO DAS TABELAS - Oracle SQL
-- Responsavel: Henrique Capetto
-- Projeto de Extensao - Turma Noturno 2026
-- ============================================================
-- EXECUTE ESTE SCRIPT ANTES DOS OUTROS!
-- ============================================================

-- Tabela: CATEGORIA
CREATE TABLE CATEGORIA (
    id_categoria    NUMBER(5)       PRIMARY KEY,
    nome            VARCHAR2(50)    NOT NULL,
    descricao       VARCHAR2(200)
);

-- Tabela: FUNCIONARIO
CREATE TABLE FUNCIONARIO (
    id_funcionario  NUMBER(5)       PRIMARY KEY,
    nome            VARCHAR2(80)    NOT NULL,
    cargo           VARCHAR2(50)    NOT NULL,
    salario         NUMBER(10,2)    NOT NULL,
    data_admissao   DATE            NOT NULL
);

-- Tabela: CLIENTE
CREATE TABLE CLIENTE (
    id_cliente      NUMBER(5)       PRIMARY KEY,
    nome            VARCHAR2(80)    NOT NULL,
    email           VARCHAR2(100)   NOT NULL UNIQUE,
    telefone        VARCHAR2(20),
    data_cadastro   DATE            DEFAULT SYSDATE
);

-- Tabela: PRODUTO
CREATE TABLE PRODUTO (
    id_produto      NUMBER(5)       PRIMARY KEY,
    nome            VARCHAR2(80)    NOT NULL,
    descricao       VARCHAR2(300),
    preco           NUMBER(10,2)    NOT NULL CHECK (preco > 0),
    estoque         NUMBER(6)       DEFAULT 0,
    id_categoria    NUMBER(5),
    CONSTRAINT fk_produto_categoria FOREIGN KEY (id_categoria)
        REFERENCES CATEGORIA(id_categoria)
);

-- Tabela: PEDIDO
CREATE TABLE PEDIDO (
    id_pedido       NUMBER(7)       PRIMARY KEY,
    id_cliente      NUMBER(5)       NOT NULL,
    id_funcionario  NUMBER(5)       NOT NULL,
    data_pedido     DATE            DEFAULT SYSDATE,
    valor_total     NUMBER(10,2),
    status          VARCHAR2(20)    DEFAULT 'PENDENTE'
                                    CHECK (status IN ('PENDENTE','APROVADO','CANCELADO','ENTREGUE')),
    CONSTRAINT fk_pedido_cliente    FOREIGN KEY (id_cliente)
        REFERENCES CLIENTE(id_cliente),
    CONSTRAINT fk_pedido_funcionario FOREIGN KEY (id_funcionario)
        REFERENCES FUNCIONARIO(id_funcionario)
);

-- Mensagem de confirmacao
SELECT 'Tabelas criadas com sucesso!' AS MENSAGEM FROM DUAL;
