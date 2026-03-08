-- ============================================================
-- INSERCAO DE DADOS DE EXEMPLO - Oracle SQL
-- Responsavel: Henrique Capetto
-- Projeto de Extensao - Turma Noturno 2026
-- ============================================================
-- Execute apos o create_tables.sql
-- ============================================================

-- CATEGORIAS
INSERT INTO CATEGORIA VALUES (1, 'Eletronicos', 'Produtos eletronicos em geral');
INSERT INTO CATEGORIA VALUES (2, 'Informatica', 'Computadores e perifericos');
INSERT INTO CATEGORIA VALUES (3, 'Servicos', 'Servicos prestados pela empresa');
INSERT INTO CATEGORIA VALUES (4, 'Acessorios', 'Acessorios diversos');
INSERT INTO CATEGORIA VALUES (5, 'Software', 'Licencas e softwares');

-- FUNCIONARIOS
INSERT INTO FUNCIONARIO VALUES (1, 'Lucas Byoung Ki Han', 'Gerente', 5000.00, TO_DATE('01/01/2025', 'DD/MM/YYYY'));
INSERT INTO FUNCIONARIO VALUES (2, 'Gabriel Cole Ambrosio', 'Desenvolvedor', 3500.00, TO_DATE('15/02/2025', 'DD/MM/YYYY'));
INSERT INTO FUNCIONARIO VALUES (3, 'Willian Soares Santana', 'Analista', 3800.00, TO_DATE('01/03/2025', 'DD/MM/YYYY'));
INSERT INTO FUNCIONARIO VALUES (4, 'Riquelly Barboza Bagatin', 'DBA', 4200.00, TO_DATE('10/01/2025', 'DD/MM/YYYY'));
INSERT INTO FUNCIONARIO VALUES (5, 'Matheus Nilcen Alves', 'Documentacao', 3000.00, TO_DATE('20/02/2025', 'DD/MM/YYYY'));

-- CLIENTES
INSERT INTO CLIENTE (id_cliente, nome, email, telefone) VALUES (1, 'Maria Silva', 'maria@email.com', '(11) 99999-0001');
INSERT INTO CLIENTE (id_cliente, nome, email, telefone) VALUES (2, 'Joao Oliveira', 'joao@email.com', '(11) 99999-0002');
INSERT INTO CLIENTE (id_cliente, nome, email, telefone) VALUES (3, 'Ana Santos', 'ana@email.com', '(11) 99999-0003');
INSERT INTO CLIENTE (id_cliente, nome, email, telefone) VALUES (4, 'Carlos Lima', 'carlos@email.com', '(11) 99999-0004');
INSERT INTO CLIENTE (id_cliente, nome, email, telefone) VALUES (5, 'Fernanda Costa', 'fernanda@email.com', '(11) 99999-0005');

-- PRODUTOS
INSERT INTO PRODUTO VALUES (1, 'Notebook Dell', 'Notebook i7 16GB RAM', 3500.00, 10, 2);
INSERT INTO PRODUTO VALUES (2, 'Mouse Logitech', 'Mouse sem fio ergonomico', 150.00, 50, 4);
INSERT INTO PRODUTO VALUES (3, 'Manutencao PC', 'Servico de manutencao preventiva', 200.00, 999, 3);
INSERT INTO PRODUTO VALUES (4, 'Licenca Windows 11', 'Licenca original Windows 11 Home', 450.00, 20, 5);
INSERT INTO PRODUTO VALUES (5, 'Smartphone Samsung', 'Galaxy A54 128GB', 1800.00, 15, 1);

-- PEDIDOS
INSERT INTO PEDIDO VALUES (1, 1, 2, TO_DATE('01/03/2026', 'DD/MM/YYYY'), 3650.00, 'APROVADO');
INSERT INTO PEDIDO VALUES (2, 2, 3, TO_DATE('05/03/2026', 'DD/MM/YYYY'), 200.00, 'PENDENTE');
INSERT INTO PEDIDO VALUES (3, 3, 2, TO_DATE('06/03/2026', 'DD/MM/YYYY'), 450.00, 'ENTREGUE');
INSERT INTO PEDIDO VALUES (4, 4, 1, TO_DATE('07/03/2026', 'DD/MM/YYYY'), 1800.00, 'APROVADO');
INSERT INTO PEDIDO VALUES (5, 5, 3, TO_DATE('08/03/2026', 'DD/MM/YYYY'), 350.00, 'PENDENTE');

COMMIT;

SELECT 'Dados inseridos com sucesso!' AS MENSAGEM FROM DUAL;
