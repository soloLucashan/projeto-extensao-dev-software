"""Testes de coerência da interface, navegação e ajustes mínimos em app.py (sem Oracle).

Rodar dentro de backend/:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""
import re
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

PASTA_BACKEND = Path(__file__).resolve().parent.parent
PASTA_RAIZ = PASTA_BACKEND.parent
PASTA_SITE = PASTA_RAIZ / "site"

sys.path.insert(0, str(PASTA_BACKEND))

import app as modulo_app  # noqa: E402
import db  # noqa: E402
import integracao_c  # noqa: E402

LINKS_NAVEGACAO = (
    "index.html",
    "sobre.html",
    "produtos.html",
    "relatorio.html",
    "portfolio.html",
    "contato.html",
)


class TestAppAjustesECasosDeBorda(unittest.TestCase):
    def setUp(self):
        self.client = modulo_app.app.test_client()

    def test_agrupar_por_categoria_preserva_itens_com_categorias_intercaladas(self):
        produtos_intercalados = [
            {"id_produto": 1, "nome": "Mouse A", "descricao": "", "preco": Decimal("100.00"), "estoque": 5, "categoria": "Perifericos"},
            {"id_produto": 2, "nome": "Dell B", "descricao": "", "preco": Decimal("2199.00"), "estoque": 2, "categoria": "Notebooks"},
            {"id_produto": 3, "nome": "Teclado C", "descricao": "", "preco": Decimal("279.90"), "estoque": 0, "categoria": "Perifericos"},
        ]
        agrupado = modulo_app.agrupar_por_categoria(produtos_intercalados)
        self.assertEqual(len(agrupado["Perifericos"]), 2)
        self.assertEqual([p["nome"] for p in agrupado["Perifericos"]], ["Mouse A", "Teclado C"])
        self.assertEqual(len(agrupado["Notebooks"]), 1)

        with mock.patch.object(db, "listar_produtos", return_value=produtos_intercalados):
            with self.client.get("/produtos.html") as resp:
                self.assertEqual(resp.status_code, 200)
                html = resp.get_data(as_text=True)
        self.assertIn("Mouse A", html)
        self.assertIn("Dell B", html)
        self.assertIn("Teclado C", html)

    def test_catalogo_vazio_exibe_aviso_amigavel(self):
        with mock.patch.object(db, "listar_produtos", return_value=[]):
            with self.client.get("/produtos.html") as resp:
                self.assertEqual(resp.status_code, 200)
                html = resp.get_data(as_text=True)
        self.assertIn("Nenhum produto cadastrado ainda.", html)

    def test_formatar_real_none_nao_vira_zero_e_renderiza_texto_explicito(self):
        self.assertEqual(modulo_app.formatar_real(None), "Preço indisponível")
        self.assertNotIn("0,00", modulo_app.formatar_real(None))
        self.assertEqual(modulo_app.formatar_real(Decimal("1899.9")), "R$ 1.899,90")

        produtos = [
            {"id_produto": 99, "nome": "Sem Preco", "descricao": None, "preco": None, "estoque": 4, "categoria": "Pecas"},
        ]
        with mock.patch.object(db, "listar_produtos", return_value=produtos):
            with self.client.get("/produtos.html") as resp:
                self.assertEqual(resp.status_code, 200)
                html = resp.get_data(as_text=True)
        self.assertIn("Preço indisponível", html)
        self.assertNotIn("R$ 0,00", html)

        with self.assertRaises(integracao_c.ErroIntegracaoC):
            integracao_c.converter_preco_para_centavos(None)

    def test_regra_estoque_0_2_3_preservada(self):
        self.assertEqual(modulo_app.situacao_estoque(0)[0], "esgotado")
        self.assertEqual(modulo_app.situacao_estoque(2)[0], "baixo-estoque")
        self.assertEqual(modulo_app.situacao_estoque(3)[0], "disponivel")


class TestCoerenciaInterfaceENavegacao(unittest.TestCase):
    def setUp(self):
        self.client = modulo_app.app.test_client()

    def test_todas_paginas_flask_retornam_200_com_menu_consistente_e_unico_ativo(self):
        produtos_demo = [
            {"id_produto": 5, "nome": "Mouse Logitech MX Master", "descricao": "Sem fio", "preco": Decimal("349.90"), "estoque": 12, "categoria": "Perifericos"},
            {"id_produto": 6, "nome": "Teclado Mecanico Redragon", "descricao": "RGB", "preco": Decimal("279.90"), "estoque": 10, "categoria": "Perifericos"},
            {"id_produto": 18, "nome": "NVIDIA RTX 3060 12GB GDDR6", "descricao": "12GB", "preco": Decimal("2399.00"), "estoque": 4, "categoria": "Pecas e Componentes"},
        ]
        resumo_demo = {
            "total_produtos": 3,
            "total_unidades": 26,
            "valor_estoque_centavos": 1659380,
            "ids_estoque_critico": [],
            "ids_esgotados": [],
        }
        esperado_ativo = {
            "/": "index.html",
            "/sobre.html": "sobre.html",
            "/produtos.html": "produtos.html",
            "/relatorio.html": "relatorio.html",
            "/portfolio.html": "portfolio.html",
            "/contato.html": "contato.html",
        }
        with mock.patch.object(db, "listar_produtos", return_value=produtos_demo), mock.patch.object(
            integracao_c, "gerar_relatorio_estoque", return_value=resumo_demo
        ):
            for rota, href_ativo in esperado_ativo.items():
                with self.subTest(rota=rota), self.client.get(rota) as resp:
                    self.assertEqual(resp.status_code, 200)
                    html = resp.get_data(as_text=True)
                    for destino in LINKS_NAVEGACAO:
                        self.assertIn(f'href="{destino}"', html)
                    ativos = re.findall(r'<a\s+href="([^"]+)"\s+class="ativo"', html)
                    self.assertEqual(ativos, [href_ativo])

    def test_home_sem_precos_divergentes_e_com_ancoras_validas(self):
        with self.client.get("/") as resp:
            self.assertEqual(resp.status_code, 200)
            html_home = resp.get_data(as_text=True)

        for preco_antigo in ("R$ 69,90", "R$ 139,90", "R$ 1.599,00"):
            self.assertNotIn(preco_antigo, html_home)
        self.assertIn("Consulte preço e disponibilidade no catálogo", html_home)

        links_produtos = re.findall(r'href="produtos\.html#(produto-\d+)"', html_home)
        self.assertEqual(links_produtos, ["produto-5", "produto-6", "produto-18"])
        self.assertNotIn("produto-10", html_home)

        produtos_ids_home = [
            {"id_produto": 5, "nome": "Mouse", "descricao": "", "preco": Decimal("349.90"), "estoque": 12, "categoria": "Perifericos"},
            {"id_produto": 6, "nome": "Teclado", "descricao": "", "preco": Decimal("279.90"), "estoque": 10, "categoria": "Perifericos"},
            {"id_produto": 18, "nome": "RTX 3060", "descricao": "", "preco": Decimal("2399.00"), "estoque": 4, "categoria": "Pecas e Componentes"},
        ]
        with mock.patch.object(db, "listar_produtos", return_value=produtos_ids_home):
            with self.client.get("/produtos.html") as resp_cat:
                html_cat = resp_cat.get_data(as_text=True)
        for frag in links_produtos:
            self.assertIn(f'id="{frag}"', html_cat)

    def test_sem_controles_de_compra_e_contato_sem_post_quebrado(self):
        produtos_demo = [
            {"id_produto": 3, "nome": "Dell", "descricao": "i5", "preco": Decimal("2199.00"), "estoque": 2, "categoria": "Notebooks"},
            {"id_produto": 19, "nome": "RX", "descricao": "8GB", "preco": Decimal("1899.00"), "estoque": 0, "categoria": "Pecas"},
        ]
        with mock.patch.object(db, "listar_produtos", return_value=produtos_demo):
            with self.client.get("/produtos.html") as resp_cat:
                html_cat = resp_cat.get_data(as_text=True)
        self.assertNotIn("Adicionar ao Carrinho", html_cat)
        self.assertNotIn("btn-comprar", html_cat)
        self.assertIn('href="contato.html"', html_cat)
        self.assertIn('href="relatorio.html"', html_cat)

        html_estatico = (PASTA_SITE / "produtos.html").read_text(encoding="utf-8")
        self.assertNotIn("Adicionar ao Carrinho", html_estatico)
        self.assertIn("Versão estática de demonstração", html_estatico)
        self.assertIn('id="produto-19"', html_estatico)
        self.assertNotIn('id="produto-11"', html_estatico)

        with self.client.get("/contato.html") as resp_contato:
            self.assertEqual(resp_contato.status_code, 200)
            html_contato = resp_contato.get_data(as_text=True)
        self.assertNotIn("<form", html_contato.lower())
        self.assertNotIn('method="post"', html_contato.lower())
        self.assertNotIn("enviado com sucesso", html_contato.lower())
        self.assertIn("dados abaixo são fictícios", html_contato.lower())

        with self.client.get("/sobre.html") as resp_sobre:
            html_sobre = resp_sobre.get_data(as_text=True)
        self.assertIn("em memória", html_sobre)
        self.assertNotIn("sem loja física", html_sobre.lower())

        with self.client.get("/portfolio.html") as resp_port:
            html_port = resp_port.get_data(as_text=True)
        self.assertIn("Conteúdo ilustrativo", html_port)
        self.assertIn("não registros de clientes reais", html_port.lower())
        self.assertNotIn("para clientes reais", html_port.lower())


if __name__ == "__main__":
    unittest.main()
