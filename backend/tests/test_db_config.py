"""Testes unitários de configuração e acesso de backend/db.py e validação estática dos scripts SQL.

Estes testes NÃO executam conexão real com o banco Oracle nem rodam SQL no servidor.
Todas as chamadas ao driver oracledb são simuladas (mock) para validar regras de
configuração, preservação de Decimal, tratamento de falhas e pré-condições estáticas.

Rodar dentro de backend/:
    .\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v
"""
import os
import re
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock

PASTA_BACKEND = Path(__file__).resolve().parent.parent
PASTA_RAIZ = PASTA_BACKEND.parent
PASTA_BANCO = PASTA_RAIZ / "banco-dados"

sys.path.insert(0, str(PASTA_BACKEND))

import db  # noqa: E402


class TestDbConfigSemOracle(unittest.TestCase):
    def test_caminho_env_aponta_para_pasta_backend(self):
        self.assertEqual(db.CAMINHO_ENV, PASTA_BACKEND / ".env")

    def test_carregar_env_le_arquivo_explicito_sem_sobrescrever_ambiente(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_tmp = Path(tmp) / ".env"
            env_tmp.write_text(
                "ORACLE_USER=PIXELSHOP\nORACLE_DSN=127.0.0.1:1522/XEPDB1\n",
                encoding="utf-8",
            )
            with mock.patch.object(db, "CAMINHO_ENV", env_tmp), mock.patch.dict(
                os.environ, {"ORACLE_USER": "JA_DEFINIDO"}, clear=True
            ):
                db._carregar_env()
                self.assertEqual(os.environ.get("ORACLE_USER"), "JA_DEFINIDO")
                self.assertEqual(os.environ.get("ORACLE_DSN"), "127.0.0.1:1522/XEPDB1")

    def test_obter_config_oracle_exige_tres_variaveis_nao_vazias(self):
        for ausente in ("ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"):
            env_base = {
                "ORACLE_USER": "PIXELSHOP",
                "ORACLE_PASSWORD": "segredo-ficticio-nao-vazar",
                "ORACLE_DSN": "127.0.0.1:1522/XEPDB1",
            }
            del env_base[ausente]
            with self.subTest(ausente=ausente), mock.patch.dict(
                os.environ, env_base, clear=True
            ):
                with self.assertRaises(db.ErroBanco) as ctx:
                    db._obter_config_oracle()
                self.assertIn(ausente, str(ctx.exception))
                self.assertNotIn("segredo-ficticio-nao-vazar", str(ctx.exception))

            env_vazio = {
                "ORACLE_USER": "PIXELSHOP",
                "ORACLE_PASSWORD": "segredo-ficticio-nao-vazar",
                "ORACLE_DSN": "127.0.0.1:1522/XEPDB1",
                ausente: "   ",
            }
            with self.subTest(vazio=ausente), mock.patch.dict(
                os.environ, env_vazio, clear=True
            ):
                with self.assertRaises(db.ErroBanco):
                    db._obter_config_oracle()

    def test_conectar_sem_driver_gera_erro_banco(self):
        with mock.patch.dict(sys.modules, {"oracledb": None}):
            with self.assertRaises(db.ErroBanco) as ctx:
                db._conectar()
            self.assertIn("oracledb", str(ctx.exception))

    def test_conectar_simulado_usa_fetch_decimals_e_converte_erro_oracle(self):
        import oracledb

        env_ok = {
            "ORACLE_USER": " PIXELSHOP ",
            "ORACLE_PASSWORD": "segredo-ficticio-nao-vazar",
            "ORACLE_DSN": " 127.0.0.1:1522/XEPDB1 ",
        }
        with mock.patch.dict(os.environ, env_ok, clear=True), mock.patch.object(
            oracledb, "connect", return_value="CONEXAO_SIMULADA"
        ) as mock_connect:
            con = db._conectar()
            self.assertEqual(con, "CONEXAO_SIMULADA")
            self.assertTrue(oracledb.defaults.fetch_decimals)
            mock_connect.assert_called_once_with(
                user="PIXELSHOP",
                password="segredo-ficticio-nao-vazar",
                dsn="127.0.0.1:1522/XEPDB1",
            )

        with mock.patch.dict(os.environ, env_ok, clear=True), mock.patch.object(
            oracledb, "connect", side_effect=oracledb.DatabaseError("DPY-6005 simulado")
        ):
            with self.assertRaises(db.ErroBanco) as ctx:
                db._conectar()
            self.assertIn("Não consegui conectar ao Oracle", str(ctx.exception))
            self.assertNotIn("segredo-ficticio-nao-vazar", str(ctx.exception))

    def test_consultar_mapeia_chaves_minusculas_e_preserva_decimal(self):
        cursor = mock.MagicMock()
        cursor.description = [
            ("ID_PRODUTO",),
            ("NOME",),
            ("DESCRICAO",),
            ("PRECO",),
            ("ESTOQUE",),
            ("CATEGORIA",),
        ]
        cursor.fetchall.return_value = [
            (3, "Notebook Dell Inspiron", "Core i5", Decimal("2199.00"), 2, "Notebooks"),
            (19, "AMD Radeon RX 6600 XT 8GB", None, Decimal("1899.00"), 0, "Pecas e Componentes"),
        ]
        conexao = mock.MagicMock()
        conexao.__enter__.return_value = conexao
        conexao.cursor.return_value.__enter__.return_value = cursor

        with mock.patch.object(db, "_conectar", return_value=conexao):
            linhas = db.listar_produtos()

        self.assertEqual(len(linhas), 2)
        self.assertEqual(linhas[0]["id_produto"], 3)
        self.assertIsInstance(linhas[0]["preco"], Decimal)
        self.assertEqual(linhas[0]["preco"], Decimal("2199.00"))
        self.assertEqual(linhas[1]["estoque"], 0)
        self.assertIsNone(linhas[1]["descricao"])

    def test_listar_produtos_rejeita_preco_ausente_sem_converter_para_zero(self):
        cursor = mock.MagicMock()
        cursor.description = [("ID_PRODUTO",), ("NOME",), ("PRECO",)]
        cursor.fetchall.return_value = [(99, "Produto Sem Preco", None)]
        conexao = mock.MagicMock()
        conexao.__enter__.return_value = conexao
        conexao.cursor.return_value.__enter__.return_value = cursor

        with mock.patch.object(db, "_conectar", return_value=conexao):
            with self.assertRaises(db.ErroBanco) as ctx:
                db.listar_produtos()
            self.assertIn("sem preço válido", str(ctx.exception))


class TestScriptsSqlEProtecaoEstatica(unittest.TestCase):
    def test_env_example_e_gitignore_contem_config_esperada(self):
        env_example = (PASTA_BACKEND / ".env.example").read_text(encoding="utf-8")
        self.assertIn("ORACLE_USER=PIXELSHOP", env_example)
        self.assertIn("ORACLE_PASSWORD=SUBSTITUA_LOCALMENTE", env_example)
        self.assertIn("ORACLE_DSN=127.0.0.1:1522/XEPDB1", env_example)

        gitignore = (PASTA_RAIZ / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", gitignore)
        self.assertIn("!backend/.env.example", gitignore)
        self.assertIn(".venv/", gitignore)
        self.assertIn("__pycache__/", gitignore)
        self.assertIn("programa-c/build/", gitignore)

    def test_precondicoes_e_instalador_bloqueiam_ambiente_errado(self):
        pre = (PASTA_BANCO / "verificar_precondicoes.sql").read_text(encoding="utf-8")
        for termo in (
            "SESSION_USER",
            "CURRENT_SCHEMA",
            "CON_NAME",
            "PIXELSHOP",
            "XEPDB1",
            "USER_OBJECTS",
            "RAISE_APPLICATION_ERROR",
        ):
            self.assertIn(termo, pre)

        inst = (PASTA_BANCO / "instalar_pixelshop.sql").read_text(encoding="utf-8")
        self.assertIn("WHENEVER SQLERROR EXIT", inst)
        self.assertIn("WHENEVER OSERROR EXIT", inst)
        pos_pre = inst.index("@@verificar_precondicoes.sql")
        pos_ddl = inst.index("@@create_tables.sql")
        pos_ins = inst.index("@@insert_data.sql")
        pos_pos = inst.index("@@verificar_pos_carga.sql")
        self.assertTrue(pos_pre < pos_ddl < pos_ins < pos_pos)

    def test_ddl_e_carga_sem_reset_e_com_not_null_e_consulta_7_corrigida(self):
        ddl = (PASTA_BANCO / "create_tables.sql").read_text(encoding="utf-8")
        carga = (PASTA_BANCO / "insert_data.sql").read_text(encoding="utf-8")
        queries = (PASTA_BANCO / "queries.sql").read_text(encoding="utf-8")

        for nome, texto in (("create_tables.sql", ddl), ("insert_data.sql", carga)):
            sem_comentarios = "\n".join(
                linha for linha in texto.splitlines() if not linha.lstrip().startswith("--")
            )
            self.assertIsNone(
                re.search(r"\b(DROP|TRUNCATE|DELETE|CREATE\s+USER)\b", sem_comentarios, re.IGNORECASE),
                msg=f"{nome} nao deve conter DROP/TRUNCATE/DELETE/CREATE USER",
            )

        self.assertIn("estoque NUMBER(5) DEFAULT 0 NOT NULL", ddl)
        self.assertIn("data_pedido DATE DEFAULT SYSDATE NOT NULL", ddl)
        self.assertIn("status VARCHAR2(20) DEFAULT 'PENDENTE' NOT NULL", ddl)
        self.assertIn("total NUMBER(10, 2) DEFAULT 0 NOT NULL", ddl)

        self.assertIn("GROUP BY pr.id_produto,\n    pr.nome", queries)
        self.assertIn("WHERE pd.status = 'CONCLUIDO'", queries)


if __name__ == "__main__":
    unittest.main()
