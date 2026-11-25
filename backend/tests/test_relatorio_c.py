"""Testes do relatório integrado com o módulo C (Camadas A e B, sem Oracle).

Camada A: testes unitários isolados de conversão, sanitização, validação JSON e rota.
Camada B: integração Python <-> binário real (main_bloco2.exe --relatorio), sem Oracle.

Rodar dentro de backend/:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""
import os
import subprocess
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

PASTA_BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PASTA_BACKEND))

import app as modulo_app  # noqa: E402
import db  # noqa: E402
import integracao_c  # noqa: E402


class TestCamadaAIntegracaoCUnitarios(unittest.TestCase):
    def test_converter_preco_para_centavos_valores_validos(self):
        casos = [
            (Decimal("0"), 0),
            (Decimal("0.00"), 0),
            (Decimal("0.10"), 10),
            (Decimal("0.29"), 29),
            (Decimal("1899.9"), 189990),
            (Decimal("92233720368547758.07"), integracao_c.LLONG_MAX),
        ]
        for preco, esperado in casos:
            with self.subTest(preco=preco):
                self.assertEqual(integracao_c.converter_preco_para_centavos(preco), esperado)

    def test_converter_preco_para_centavos_rejeita_invalidos_e_fracao_extra(self):
        invalidos = [
            10.50,
            100,
            True,
            None,
            "10.50",
            Decimal("-0.01"),
            Decimal("NaN"),
            Decimal("Infinity"),
            Decimal("-Infinity"),
            Decimal("10.123"),
            Decimal("0.005"),
            Decimal("92233720368547758.08"),
        ]
        for valor in invalidos:
            with self.subTest(valor=valor):
                with self.assertRaises(integracao_c.ErroIntegracaoC):
                    integracao_c.converter_preco_para_centavos(valor)

    def test_montar_entrada_aceita_decimal_integral_e_rejeita_violacoes(self):
        entrada, ids = integracao_c.montar_entrada_protocolo(
            [
                {
                    "id_produto": Decimal("5"),
                    "nome": "Ignorado no protocolo",
                    "preco": Decimal("349.90"),
                    "estoque": Decimal("12.00"),
                }
            ]
        )
        self.assertEqual(entrada, "5\t34990\t12\n")
        self.assertEqual(ids, {5})

        invalidos = [
            None,
            "1\t100\t1\n",
            {"id_produto": 1},
            [{"id_produto": 0, "preco": Decimal("10.00"), "estoque": 1}],
            [{"id_produto": Decimal("1.5"), "preco": Decimal("10.00"), "estoque": 1}],
            [{"id_produto": True, "preco": Decimal("10.00"), "estoque": 1}],
            [
                {"id_produto": 1, "preco": Decimal("10.00"), "estoque": 1},
                {"id_produto": 1, "preco": Decimal("20.00"), "estoque": 2},
            ],
            [{"id_produto": 1, "preco": Decimal("10.00"), "estoque": -1}],
            [{"id_produto": 1, "preco": Decimal("10.00"), "estoque": Decimal("2.5")}],
            [{"id_produto": 1, "preco": Decimal("10.00"), "estoque": False}],
            [
                {"id_produto": i, "preco": Decimal("1.00"), "estoque": 1}
                for i in range(1, integracao_c.MAX_ITENS_RELATORIO + 2)
            ],
            [
                {
                    "id_produto": 1,
                    "preco": Decimal("1.00"),
                    "estoque": int("9" * 130),
                }
            ],
        ]
        for caso in invalidos:
            with self.subTest(caso=type(caso).__name__):
                with self.assertRaises(integracao_c.ErroIntegracaoC):
                    integracao_c.montar_entrada_protocolo(caso)

    def test_ambiente_minimo_subprocesso_nao_herda_credenciais_oracle(self):
        env_simulado = {
            "ORACLE_USER": "PIXELSHOP",
            "ORACLE_PASSWORD": "segredo-super-sensivel",
            "ORACLE_DSN": "127.0.0.1:1522/XEPDB1",
            "PATH": "C:\\Windows\\System32",
            "SYSTEMROOT": "C:\\Windows",
        }
        with mock.patch.dict(os.environ, env_simulado, clear=True):
            env_c = integracao_c._ambiente_minimo_subprocesso()
        self.assertNotIn("ORACLE_USER", env_c)
        self.assertNotIn("ORACLE_PASSWORD", env_c)
        self.assertNotIn("ORACLE_DSN", env_c)
        self.assertEqual(env_c.get("PATH"), "C:\\Windows\\System32")

    def test_executar_modulo_c_trata_falhas_simuladas_sem_vazar_segredos(self):
        # Executavel ausente
        with self.assertRaises(integracao_c.ErroIntegracaoC):
            integracao_c.executar_modulo_c("", executavel=PASTA_BACKEND / "nao_existe.exe")

        # Subprocesso com FileNotFoundError, PermissionError, TimeoutExpired e returncode != 0
        with mock.patch.object(Path, "is_file", return_value=True):
            for efeito in (
                FileNotFoundError("ausente"),
                PermissionError("negado"),
                subprocess.TimeoutExpired(cmd="main_bloco2.exe", timeout=5),
            ):
                with self.subTest(efeito=type(efeito).__name__), mock.patch(
                    "integracao_c.subprocess.run", side_effect=efeito
                ):
                    with self.assertRaises(integracao_c.ErroIntegracaoC):
                        integracao_c.executar_modulo_c("")

            falha_rc = subprocess.CompletedProcess(
                args=["main_bloco2.exe", "--relatorio"],
                returncode=2,
                stdout="",
                stderr=f"Erro em {integracao_c.PASTA_RAIZ} com segredo-123",
            )
            with mock.patch.dict(
                os.environ, {"ORACLE_PASSWORD": "segredo-123"}, clear=False
            ), mock.patch("integracao_c.subprocess.run", return_value=falha_rc):
                with self.assertRaises(integracao_c.ErroIntegracaoC) as ctx:
                    integracao_c.executar_modulo_c("")
                self.assertNotIn("segredo-123", ctx.exception.detalhe_log)
                self.assertNotIn(str(integracao_c.PASTA_RAIZ), ctx.exception.detalhe_log)

    def test_validar_resposta_c_rejeita_json_invalido_campos_e_tipos_errados(self):
        casos_invalidos = [
            "",
            "nao eh json",
            "[]",
            '{"total_produtos": 1}',
            '{"total_produtos": 1, "total_unidades": 2, "valor_estoque_centavos": 100, "ids_estoque_critico": [], "ids_esgotados": [], "extra": 1}',
            '{"total_produtos": true, "total_unidades": 2, "valor_estoque_centavos": 100, "ids_estoque_critico": [], "ids_esgotados": []}',
            '{"total_produtos": 1, "total_unidades": false, "valor_estoque_centavos": 100, "ids_estoque_critico": [], "ids_esgotados": []}',
            '{"total_produtos": 1, "total_unidades": -1, "valor_estoque_centavos": 100, "ids_estoque_critico": [], "ids_esgotados": []}',
            '{"total_produtos": 2, "total_unidades": 2, "valor_estoque_centavos": 100, "ids_estoque_critico": [], "ids_esgotados": []}',
            '{"total_produtos": 1, "total_unidades": 2, "valor_estoque_centavos": 100, "ids_estoque_critico": [99], "ids_esgotados": []}',
            '{"total_produtos": 1, "total_unidades": 2, "valor_estoque_centavos": 100, "ids_estoque_critico": [1, 1], "ids_esgotados": []}',
            '{"total_produtos": 1, "total_unidades": 2, "valor_estoque_centavos": 100, "ids_estoque_critico": [], "ids_esgotados": [1]}',
        ]
        for payload in casos_invalidos:
            with self.subTest(payload=payload):
                with self.assertRaises(integracao_c.ErroIntegracaoC):
                    integracao_c.validar_resposta_c(
                        payload, ids_esperados={1}, total_esperado=1
                    )

    def test_rota_relatorio_renderiza_sucesso_e_erros_503_sem_totais_zero(self):
        client = modulo_app.app.test_client()
        produtos = [
            {"id_produto": 3, "nome": "Notebook <Teste>", "preco": Decimal("2199.00"), "estoque": 2, "categoria": "Notebooks"},
            {"id_produto": 19, "nome": "Placa Esgotada", "preco": Decimal("1899.00"), "estoque": 0, "categoria": "Pecas"},
        ]
        resumo = {
            "total_produtos": 2,
            "total_unidades": 2,
            "valor_estoque_centavos": 439800,
            "ids_estoque_critico": [3, 19],
            "ids_esgotados": [19],
        }
        with mock.patch.object(db, "listar_produtos", return_value=produtos), mock.patch.object(
            integracao_c, "gerar_relatorio_estoque", return_value=resumo
        ):
            with client.get("/relatorio.html") as resp:
                self.assertEqual(resp.status_code, 200)
                html = resp.get_data(as_text=True)
            self.assertIn("módulo nativo em C", html)
            self.assertIn("R$ 4.398,00", html)
            self.assertIn("Notebook &lt;Teste&gt;", html)
            self.assertNotIn("Notebook <Teste>", html)
            self.assertIn("produtos esgotados (0 unidades) também pertencem aos críticos", html)
            self.assertIn('href="produtos.html"', html)

            with client.get("/produtos.html") as resp_cat:
                self.assertEqual(resp_cat.status_code, 200)
                self.assertIn('href="relatorio.html"', resp_cat.get_data(as_text=True))

        # Erro de banco -> 503 sem cartoes de totais zero
        with mock.patch.object(db, "listar_produtos", side_effect=db.ErroBanco("offline")):
            with client.get("/relatorio.html") as resp:
                self.assertEqual(resp.status_code, 503)
                html = resp.get_data(as_text=True)
            self.assertIn("Não foi possível consultar o banco de dados", html)
            self.assertNotIn("grid-metricas", html)

        # Erro do C -> 503 sem vazar stderr bruto nem totais zero
        erro_c = integracao_c.ErroIntegracaoC(
            "Falha no módulo C.",
            detalhe_log="STDERR_INTERNO_C:/caminho/secreto",
        )
        with mock.patch.object(db, "listar_produtos", return_value=produtos), mock.patch.object(
            integracao_c, "gerar_relatorio_estoque", side_effect=erro_c
        ):
            with client.get("/relatorio.html") as resp:
                self.assertEqual(resp.status_code, 503)
                html = resp.get_data(as_text=True)
            self.assertIn("Não foi possível processar o relatório de estoque pelo módulo C", html)
            self.assertNotIn("STDERR_INTERNO", html)
            self.assertNotIn("grid-metricas", html)


class TestCamadaBIntegracaoPythonCReal(unittest.TestCase):
    def test_exemplo_dois_produtos_contrato_contra_executavel_real(self):
        produtos = [
            {"id_produto": 1, "nome": "Produto 1", "preco": Decimal("100.00"), "estoque": 2},
            {"id_produto": 2, "nome": "Produto 2", "preco": Decimal("250.00"), "estoque": 4},
        ]
        resumo = integracao_c.gerar_relatorio_estoque(produtos)
        self.assertEqual(
            resumo,
            {
                "total_produtos": 2,
                "total_unidades": 6,
                "valor_estoque_centavos": 120000,
                "ids_estoque_critico": [1],
                "ids_esgotados": [],
            },
        )

    def test_entrada_vazia_contra_executavel_real(self):
        resumo = integracao_c.gerar_relatorio_estoque([])
        self.assertEqual(
            resumo,
            {
                "total_produtos": 0,
                "total_unidades": 0,
                "valor_estoque_centavos": 0,
                "ids_estoque_critico": [],
                "ids_esgotados": [],
            },
        )

    def test_estoques_0_2_3_4_e_centavos_contra_executavel_real(self):
        produtos = [
            {"id_produto": Decimal("10"), "nome": "P0", "preco": Decimal("0.10"), "estoque": Decimal("0")},
            {"id_produto": Decimal("20"), "nome": "P2", "preco": Decimal("0.29"), "estoque": Decimal("2")},
            {"id_produto": Decimal("30"), "nome": "P3", "preco": Decimal("10.00"), "estoque": Decimal("3")},
            {"id_produto": Decimal("40"), "nome": "P4", "preco": Decimal("20.00"), "estoque": Decimal("4")},
        ]
        resumo = integracao_c.gerar_relatorio_estoque(produtos)
        self.assertEqual(resumo["total_produtos"], 4)
        self.assertEqual(resumo["total_unidades"], 9)
        self.assertEqual(resumo["valor_estoque_centavos"], 11058)
        self.assertEqual(resumo["ids_estoque_critico"], [10, 20])
        self.assertEqual(resumo["ids_esgotados"], [10])

    def test_rota_relatorio_com_c_real_e_produtos_simulados(self):
        produtos = [
            {"id_produto": 1, "nome": "Item Critico", "preco": Decimal("100.00"), "estoque": 2, "categoria": "Perifericos"},
            {"id_produto": 2, "nome": "Item Normal", "preco": Decimal("250.00"), "estoque": 4, "categoria": "Perifericos"},
        ]
        client = modulo_app.app.test_client()
        with mock.patch.object(db, "listar_produtos", return_value=produtos):
            with client.get("/relatorio.html") as resp:
                self.assertEqual(resp.status_code, 200)
                html = resp.get_data(as_text=True)
        self.assertIn("R$ 1.200,00", html)
        self.assertIn("#1 — Item Critico", html)
        self.assertNotIn("#2 — Item Normal", html)


if __name__ == "__main__":
    unittest.main()
