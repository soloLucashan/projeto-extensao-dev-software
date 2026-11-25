"""Testes do catálogo sem precisar do Oracle (a consulta é substituída por dados de teste).
Rodar dentro de backend/:  python -m unittest discover tests
"""
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as modulo_app  # noqa: E402
import db  # noqa: E402

PRODUTOS = [
    {"id_produto": 5, "nome": "Mouse <b>Teste</b>", "descricao": "Sem fio", "preco": Decimal("349.90"),
     "estoque": 12, "categoria": "Perifericos"},
    {"id_produto": 3, "nome": "Notebook Dell", "descricao": None, "preco": Decimal("2199.00"),
     "estoque": 2, "categoria": "Notebooks"},
    {"id_produto": 9, "nome": "Placa X", "descricao": "Zerada", "preco": Decimal("1899.9"),
     "estoque": 0, "categoria": "Pecas"},
]


class TestCatalogo(unittest.TestCase):
    def setUp(self):
        self.client = modulo_app.app.test_client()

    def test_mostra_dados_do_banco(self):
        with mock.patch.object(db, "listar_produtos", return_value=PRODUTOS):
            with self.client.get("/produtos.html") as resp:
                html = resp.get_data(as_text=True)
        self.assertIn("Notebook Dell", html)
        self.assertIn("R$ 2.199,00", html)
        self.assertIn("R$ 349,90", html)
        self.assertIn("12 un.", html)
        self.assertIn("Últimas unidades (2)", html)
        self.assertIn("Esgotado", html)
        self.assertIn('id="produto-5"', html)

    def test_escapa_html(self):
        with mock.patch.object(db, "listar_produtos", return_value=PRODUTOS):
            with self.client.get("/produtos.html") as resp:
                html = resp.get_data(as_text=True)
        self.assertNotIn("<b>Teste</b>", html)

    def test_erro_do_banco_nao_derruba_a_pagina(self):
        with mock.patch.object(db, "listar_produtos", side_effect=db.ErroBanco("falhou")):
            with self.client.get("/produtos.html") as resp:
                self.assertEqual(resp.status_code, 503)
                self.assertIn("Não foi possível carregar", resp.get_data(as_text=True))

    def test_css_e_outras_paginas_continuam_funcionando(self):
        for rota in ("/css/style.css", "/sobre.html", "/"):
            with self.subTest(rota=rota), self.client.get(rota) as resp:
                self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
