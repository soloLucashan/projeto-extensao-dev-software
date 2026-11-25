"""Suíte de integração real (opt-in, somente leitura) contra o Oracle XEPDB1.

Características:
- Fica fora de backend/tests/ para não rodar na descoberta normal de unitários.
- Exige PIXELSHOP_RUN_ORACLE_TESTS=1 no ambiente para executar.
- Executa apenas consultas SELECT (nunca cria, altera, apaga ou recarrega tabelas).
- Nunca imprime credenciais ou conteúdo de .env.

Para executar dentro de backend/:
    $env:PIXELSHOP_RUN_ORACLE_TESTS='1'
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests_integracao -v
"""
import os
import re
import sys
import unittest
from decimal import Decimal
from pathlib import Path

PASTA_BACKEND = Path(__file__).resolve().parent.parent
PASTA_RAIZ = PASTA_BACKEND.parent
PASTA_BANCO = PASTA_RAIZ / "banco-dados"

sys.path.insert(0, str(PASTA_BACKEND))

import app as modulo_app  # noqa: E402
import db  # noqa: E402

EXECUTAR_INTEGRACAO = os.environ.get("PIXELSHOP_RUN_ORACLE_TESTS") == "1"


def _carregar_queries_select(caminho_sql):
    """Extrai as instruções SELECT de queries.sql removendo comentários."""
    linhas_sem_comentario = []
    for linha in caminho_sql.read_text(encoding="utf-8").splitlines():
        if "--" in linha:
            linha = linha.split("--", 1)[0]
        linhas_sem_comentario.append(linha)

    texto = "\n".join(linhas_sem_comentario)
    consultas = [parte.strip() for parte in texto.split(";") if parte.strip()]
    for idx, sql in enumerate(consultas, start=1):
        if not sql.upper().startswith("SELECT"):
            raise AssertionError(f"Consulta {idx} não começa com SELECT.")
        if re.search(
            r"\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|MERGE)\b",
            sql,
            re.IGNORECASE,
        ):
            raise AssertionError(f"Consulta {idx} contém palavra proibida fora de leitura.")
    return consultas


@unittest.skipUnless(
    EXECUTAR_INTEGRACAO,
    "Integração Oracle real desativada (defina PIXELSHOP_RUN_ORACLE_TESTS=1).",
)
class TestOracleRealSomenteLeitura(unittest.TestCase):
    def test_identidade_e_privilegios_sessao(self):
        sess = db._consultar(
            """
            SELECT SYS_CONTEXT('USERENV', 'SESSION_USER') AS session_user,
                   SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') AS current_schema,
                   SYS_CONTEXT('USERENV', 'CON_NAME') AS con_name
              FROM DUAL
            """
        )
        self.assertEqual(len(sess), 1)
        self.assertEqual(sess[0]["session_user"], "PIXELSHOP")
        self.assertEqual(sess[0]["current_schema"], "PIXELSHOP")
        self.assertEqual(sess[0]["con_name"], "XEPDB1")

        privs = {
            r["privilege"]
            for r in db._consultar("SELECT privilege FROM SESSION_PRIVS")
        }
        self.assertTrue(
            {"CREATE SESSION", "CREATE TABLE", "CREATE SEQUENCE"}.issubset(privs)
        )
        roles = {
            r["granted_role"]
            for r in db._consultar("SELECT granted_role FROM USER_ROLE_PRIVS")
        }
        self.assertNotIn("DBA", roles)

    def test_contagens_vinculos_totais_e_estoque(self):
        contagens = db._consultar(
            """
            SELECT 'CATEGORIA' AS tabela, COUNT(*) AS total FROM CATEGORIA
            UNION ALL
            SELECT 'PRODUTO' AS tabela, COUNT(*) AS total FROM PRODUTO
            UNION ALL
            SELECT 'CLIENTE' AS tabela, COUNT(*) AS total FROM CLIENTE
            UNION ALL
            SELECT 'PEDIDO' AS tabela, COUNT(*) AS total FROM PEDIDO
            UNION ALL
            SELECT 'ITEM_PEDIDO' AS tabela, COUNT(*) AS total FROM ITEM_PEDIDO
            """
        )
        esperado = [
            ("CATEGORIA", 4),
            ("PRODUTO", 19),
            ("CLIENTE", 15),
            ("PEDIDO", 12),
            ("ITEM_PEDIDO", 22),
        ]
        observado = [(r["tabela"], int(r["total"])) for r in contagens]
        self.assertEqual(observado, esperado)

        divergencias = db._consultar(
            """
            SELECT pd.id_pedido,
                   pd.total AS total_pedido,
                   NVL(SUM(ip.quantidade * ip.preco_unit), 0) AS soma_itens
              FROM PEDIDO pd
              LEFT JOIN ITEM_PEDIDO ip ON pd.id_pedido = ip.id_pedido
             GROUP BY pd.id_pedido, pd.total
            HAVING pd.total <> NVL(SUM(ip.quantidade * ip.preco_unit), 0)
            """
        )
        self.assertEqual(divergencias, [])

        pedidos_sem_itens = db._consultar(
            """
            SELECT pd.id_pedido
              FROM PEDIDO pd
              LEFT JOIN ITEM_PEDIDO ip ON pd.id_pedido = ip.id_pedido
             WHERE ip.id_item IS NULL
            """
        )
        self.assertEqual(pedidos_sem_itens, [])

        produtos_chave = {
            int(r["id_produto"]): r
            for r in db._consultar(
                """
                SELECT p.id_produto, p.nome, c.nome_categoria AS categoria, p.preco, p.estoque
                  FROM PRODUTO p
                  JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
                 WHERE p.id_produto IN (3, 5, 18, 19)
                """
            )
        }
        self.assertEqual(set(produtos_chave.keys()), {3, 5, 18, 19})
        self.assertEqual(produtos_chave[3]["nome"], "Notebook Dell Inspiron")
        self.assertEqual(produtos_chave[3]["categoria"], "Notebooks")
        self.assertEqual(produtos_chave[3]["preco"], Decimal("2199.00"))
        self.assertEqual(int(produtos_chave[3]["estoque"]), 2)

        self.assertEqual(produtos_chave[5]["nome"], "Mouse Logitech MX Master")
        self.assertEqual(produtos_chave[5]["preco"], Decimal("349.90"))
        self.assertEqual(int(produtos_chave[5]["estoque"]), 12)

        self.assertEqual(produtos_chave[18]["nome"], "NVIDIA RTX 3060 12GB GDDR6")
        self.assertEqual(produtos_chave[18]["preco"], Decimal("2399.00"))
        self.assertEqual(int(produtos_chave[18]["estoque"]), 4)

        self.assertEqual(produtos_chave[19]["nome"], "AMD Radeon RX 6600 XT 8GB")
        self.assertEqual(produtos_chave[19]["preco"], Decimal("1899.00"))
        self.assertEqual(int(produtos_chave[19]["estoque"]), 0)

        dist = {
            r["estado"]: int(r["quantidade"])
            for r in db._consultar(
                """
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
                """
            )
        }
        self.assertEqual(dist, {"ESGOTADO": 1, "CRITICO": 1, "DISPONIVEL": 17})

    def test_dez_consultas_queries_sql(self):
        consultas = _carregar_queries_select(PASTA_BANCO / "queries.sql")
        self.assertEqual(len(consultas), 10)

        resultados = [db._consultar(sql) for sql in consultas]

        # Q1: 15 clientes ordenados por nome
        q1 = resultados[0]
        self.assertEqual(len(q1), 15)
        self.assertEqual(q1[0]["nome"], "Amanda Ribeiro")
        self.assertEqual(q1[-1]["nome"], "Thiago Rodrigues")

        # Q2: 19 produtos com categoria
        q2 = resultados[1]
        self.assertEqual(len(q2), 19)
        self.assertEqual(
            {r["categoria"] for r in q2},
            {"Notebooks", "Pecas e Componentes", "Perifericos", "Smartphones"},
        )

        # Q3: 12 pedidos em ordem decrescente de data
        q3 = resultados[2]
        self.assertEqual(len(q3), 12)
        self.assertEqual(int(q3[0]["id_pedido"]), 12)
        self.assertEqual(int(q3[-1]["id_pedido"]), 1)

        # Q4: 22 itens com subtotal exato
        q4 = resultados[3]
        self.assertEqual(len(q4), 22)
        for item in q4:
            self.assertEqual(
                item["subtotal"], item["quantidade"] * item["preco_unit"]
            )

        # Q5: alertas criticos (< 3)
        q5 = resultados[4]
        self.assertEqual(
            [(r["nome"], int(r["estoque"]), r["preco"]) for r in q5],
            [
                ("AMD Radeon RX 6600 XT 8GB", 0, Decimal("1899.00")),
                ("Notebook Dell Inspiron", 2, Decimal("2199.00")),
            ],
        )

        # Q6: 8 clientes com pedidos CONCLUIDO
        q6 = resultados[5]
        self.assertEqual(len(q6), 8)
        self.assertEqual(q6[0]["cliente"], "Amanda Ribeiro")
        self.assertEqual(q6[0]["valor_total"], Decimal("5297.90"))
        self.assertEqual(sum(r["valor_total"] for r in q6), Decimal("17372.90"))

        # Q7: ranking de produtos vendidos apenas em pedidos CONCLUIDO
        q7 = resultados[6]
        self.assertEqual(len(q7), 12)
        por_id = {int(r["id_produto"]): int(r["total_unidades_vendidas"]) for r in q7}
        self.assertEqual(sum(por_id.values()), 17)
        self.assertEqual(por_id[15], 1)
        self.assertEqual(por_id[16], 2)
        self.assertNotIn(3, por_id)
        self.assertNotIn(10, por_id)
        self.assertNotIn(12, por_id)

        # Q8: receita total por categoria (CONCLUIDO)
        q8 = resultados[7]
        por_cat = {r["categoria"]: r["total_arrecadado"] for r in q8}
        self.assertEqual(
            por_cat,
            {
                "Notebooks": Decimal("6898.00"),
                "Smartphones": Decimal("6697.70"),
                "Perifericos": Decimal("3117.40"),
                "Pecas e Componentes": Decimal("659.80"),
            },
        )
        self.assertEqual(sum(por_cat.values()), Decimal("17372.90"))

        # Q9: 3 clientes sem pedido
        q9 = resultados[8]
        self.assertEqual(
            {r["nome"] for r in q9},
            {"Juliana Costa", "Leticia Ferreira", "Gabriel Almeida"},
        )

        # Q10: ticket medio dos pedidos concluidos
        q10 = resultados[9]
        self.assertEqual(len(q10), 1)
        self.assertEqual(q10[0]["ticket_medio"], Decimal("2171.6125"))

    def test_db_listar_produtos_real_sem_mock(self):
        produtos = db.listar_produtos()
        self.assertEqual(len(produtos), 19)
        for p in produtos:
            self.assertIsInstance(p["preco"], Decimal)
            self.assertIn(
                p["categoria"],
                {"Notebooks", "Pecas e Componentes", "Perifericos", "Smartphones"},
            )
            self.assertGreaterEqual(int(p["estoque"]), 0)

        por_id = {int(p["id_produto"]): p for p in produtos}
        self.assertEqual(int(por_id[3]["estoque"]), 2)
        self.assertEqual(int(por_id[19]["estoque"]), 0)

    def test_rota_produtos_html_real_sem_mock(self):
        client = modulo_app.app.test_client()
        with client.get("/produtos.html") as resp:
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

        for i in range(1, 20):
            self.assertIn(f'id="produto-{i}"', html)

        self.assertIn("Notebook Dell Inspiron", html)
        self.assertIn("R$ 2.199,00", html)
        self.assertIn("AMD Radeon RX 6600 XT 8GB", html)
        self.assertIn("R$ 1.899,00", html)
        self.assertIn("Mouse Logitech MX Master", html)
        self.assertIn("R$ 349,90", html)

        self.assertIn("badge-estoque disponivel", html)
        self.assertIn("badge-estoque baixo-estoque", html)
        self.assertIn("Últimas unidades (2)", html)
        self.assertIn("badge-estoque esgotado", html)
        self.assertIn("✕ Esgotado", html)
        self.assertNotIn("Adicionar ao Carrinho", html)


if __name__ == "__main__":
    unittest.main()
