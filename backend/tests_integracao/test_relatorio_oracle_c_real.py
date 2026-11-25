"""Suíte de integração completa (Camada C, opt-in, somente leitura):
Oracle real -> db.py -> integracao_c.py -> main_bloco2.exe --relatorio -> Flask /relatorio.html.

Rodar dentro de backend/:
    $env:PIXELSHOP_RUN_ORACLE_TESTS='1'
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests_integracao -v
"""
import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path

PASTA_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PASTA_BACKEND))

import app as modulo_app  # noqa: E402
import db  # noqa: E402
import integracao_c  # noqa: E402

EXECUTAR_INTEGRACAO = os.environ.get("PIXELSHOP_RUN_ORACLE_TESTS") == "1"


@unittest.skipUnless(
    EXECUTAR_INTEGRACAO,
    "Integração completa Oracle + C + Flask desativada (defina PIXELSHOP_RUN_ORACLE_TESTS=1).",
)
class TestRelatorioCompletoOracleCReal(unittest.TestCase):
    def test_fluxo_oracle_c_real_bate_com_sql_independente(self):
        produtos = db.listar_produtos()
        self.assertEqual(len(produtos), 19)

        resumo = integracao_c.gerar_relatorio_estoque(produtos)

        conferencia_sql = db._consultar(
            """
            SELECT COUNT(*) AS total_produtos,
                   SUM(estoque) AS total_unidades,
                   SUM(preco * estoque) AS valor_estoque_reais
              FROM PRODUTO
            """
        )
        self.assertEqual(len(conferencia_sql), 1)
        linha = conferencia_sql[0]

        esperado_produtos = int(linha["total_produtos"])
        esperado_unidades = int(linha["total_unidades"])
        esperado_centavos = int(linha["valor_estoque_reais"] * Decimal(100))

        self.assertEqual(resumo["total_produtos"], 19)
        self.assertEqual(resumo["total_produtos"], esperado_produtos)
        self.assertEqual(resumo["total_unidades"], esperado_unidades)
        self.assertEqual(resumo["valor_estoque_centavos"], esperado_centavos)
        self.assertEqual(set(resumo["ids_estoque_critico"]), {3, 19})
        self.assertEqual(set(resumo["ids_esgotados"]), {19})

    def test_rota_relatorio_html_completa_sem_mock(self):
        client = modulo_app.app.test_client()
        with client.get("/relatorio.html") as resp:
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)

        conferencia_sql = db._consultar(
            """
            SELECT COUNT(*) AS total_produtos,
                   SUM(estoque) AS total_unidades,
                   SUM(preco * estoque) AS valor_estoque_reais
              FROM PRODUTO
            """
        )[0]
        valor_esperado_brl = modulo_app.formatar_real(conferencia_sql["valor_estoque_reais"])

        self.assertIn("módulo nativo em C", html)
        self.assertIn(f">{int(conferencia_sql['total_produtos'])}<", html)
        self.assertIn(f">{int(conferencia_sql['total_unidades'])}<", html)
        self.assertIn(valor_esperado_brl, html)
        self.assertIn("#3 — Notebook Dell Inspiron", html)
        self.assertIn("#19 — AMD Radeon RX 6600 XT 8GB", html)
        self.assertIn("produtos esgotados (0 unidades) também pertencem aos críticos", html)
        self.assertIn('href="produtos.html"', html)


if __name__ == "__main__":
    unittest.main()
