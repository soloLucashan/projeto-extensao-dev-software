"""Testes automatizados do programa C (programa-c/build/main_bloco2.exe).

Usa apenas a biblioteca padrao do Python e executa o binario real em subprocessos
com timeout explicito, sem mocks.
Rodar na raiz do projeto:
    backend\\.venv\\Scripts\\python.exe -m unittest discover -s programa-c\\tests -v
"""

import json
import subprocess
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
BINARIO = RAIZ / "programa-c" / "build" / "main_bloco2.exe"
TIMEOUT_SEGUNDOS = 5
LLONG_MAX = (1 << 63) - 1


def executar_c(args, entrada_texto):
    """Executa o binario C real com timeout e retorna CompletedProcess."""
    if not BINARIO.exists():
        raise AssertionError(f"Binario esperado nao encontrado: {BINARIO}")
    return subprocess.run(
        [str(BINARIO), *args],
        input=entrada_texto,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=TIMEOUT_SEGUNDOS,
    )


class TestModoRelatorioC(unittest.TestCase):
    def test_exemplo_oficial_dois_produtos(self):
        entrada = "1\t10000\t2\n2\t25000\t4\n"
        res = executar_c(["--relatorio"], entrada)
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertEqual(res.stderr, "")
        dados = json.loads(res.stdout)
        self.assertEqual(
            dados,
            {
                "total_produtos": 2,
                "total_unidades": 6,
                "valor_estoque_centavos": 120000,
                "ids_estoque_critico": [1],
                "ids_esgotados": [],
            },
        )

    def test_aceita_crlf_e_ultima_linha_sem_quebra(self):
        entrada = "1\t10000\t2\r\n2\t25000\t4"
        res = executar_c(["--relatorio"], entrada)
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertEqual(res.stderr, "")
        dados = json.loads(res.stdout)
        self.assertEqual(dados["total_produtos"], 2)
        self.assertEqual(dados["total_unidades"], 6)
        self.assertEqual(dados["valor_estoque_centavos"], 120000)

    def test_entrada_vazia_retorna_totais_zero_e_listas_vazias(self):
        res = executar_c(["--relatorio"], "")
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertEqual(res.stderr, "")
        dados = json.loads(res.stdout)
        self.assertEqual(
            dados,
            {
                "total_produtos": 0,
                "total_unidades": 0,
                "valor_estoque_centavos": 0,
                "ids_estoque_critico": [],
                "ids_esgotados": [],
            },
        )

    def test_limites_estoque_0_2_3_4(self):
        entrada = (
            "10\t100\t0\n"
            "20\t100\t2\n"
            "30\t100\t3\n"
            "40\t100\t4\n"
        )
        res = executar_c(["--relatorio"], entrada)
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        dados = json.loads(res.stdout)
        self.assertEqual(dados["total_produtos"], 4)
        self.assertEqual(dados["total_unidades"], 9)
        self.assertEqual(dados["valor_estoque_centavos"], 900)
        self.assertEqual(dados["ids_estoque_critico"], [10, 20])
        self.assertEqual(dados["ids_esgotados"], [10])

    def test_valores_em_centavos_10_e_29_sem_perda(self):
        entrada = "1\t10\t3\n2\t29\t1\n3\t1999\t2\n"
        res = executar_c(["--relatorio"], entrada)
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        dados = json.loads(res.stdout)
        self.assertEqual(dados["valor_estoque_centavos"], 4057)

    def test_rejeita_ids_duplicados(self):
        entrada = "7\t1000\t2\n7\t2000\t3\n"
        res = executar_c(["--relatorio"], entrada)
        self.assertEqual(res.returncode, 2)
        self.assertEqual(res.stdout, "")
        self.assertIn("duplicado", res.stderr.lower())

    def test_rejeita_valores_negativos_e_id_zero(self):
        casos = [
            ("1\t-1\t2\n", "preco_centavos"),
            ("1\t100\t-1\n", "estoque"),
            ("0\t100\t2\n", "id_produto"),
            ("-3\t100\t2\n", "id_produto"),
        ]
        for entrada, termo in casos:
            with self.subTest(entrada=entrada):
                res = executar_c(["--relatorio"], entrada)
                self.assertEqual(res.returncode, 2)
                self.assertEqual(res.stdout, "")
                self.assertIn(termo, res.stderr)

    def test_rejeita_nao_numerico_e_parcialmente_numerico(self):
        casos = [
            "abc\t100\t2\n",
            "1\t12abc\t2\n",
            "1\t100\t12abc\n",
            "12abc\t100\t2\n",
            "1\t+100\t2\n",
            "1\t 100\t2\n",
            "1\t100 \t2\n",
            "1\t10.50\t2\n",
        ]
        for entrada in casos:
            with self.subTest(entrada=entrada):
                res = executar_c(["--relatorio"], entrada)
                self.assertEqual(res.returncode, 2)
                self.assertEqual(res.stdout, "")
                self.assertNotEqual(res.stderr.strip(), "")

    def test_rejeita_campo_ausente_linha_vazia_e_campo_extra(self):
        casos = [
            "1\t100\n",
            "1\n",
            "\n",
            "1\t100\t2\t99\n",
            "1\t100\t\n",
        ]
        for entrada in casos:
            with self.subTest(entrada=entrada):
                res = executar_c(["--relatorio"], entrada)
                self.assertEqual(res.returncode, 2)
                self.assertEqual(res.stdout, "")
                self.assertNotEqual(res.stderr.strip(), "")

    def test_rejeita_overflow_de_parse_e_aritmetico_e_aceita_limite_llong(self):
        # Limite exato de LLONG_MAX sem overflow
        res_ok = executar_c(["--relatorio"], f"1\t{LLONG_MAX}\t1\n")
        self.assertEqual(res_ok.returncode, 0, msg=res_ok.stderr)
        self.assertEqual(json.loads(res_ok.stdout)["valor_estoque_centavos"], LLONG_MAX)

        # Overflow no parse (> LLONG_MAX)
        for entrada in [
            f"1\t{LLONG_MAX + 1}\t1\n",
            "99999999999999999999999\t100\t1\n",
        ]:
            with self.subTest(parse_overflow=entrada):
                res = executar_c(["--relatorio"], entrada)
                self.assertEqual(res.returncode, 2)
                self.assertEqual(res.stdout, "")
                self.assertIn("64 bits", res.stderr)

        # Overflow aritmetico na multiplicacao e nas somas
        for entrada in [
            f"1\t{LLONG_MAX}\t2\n",
            f"1\t{LLONG_MAX}\t1\n2\t1\t1\n",
            f"1\t0\t{LLONG_MAX}\n2\t0\t1\n",
        ]:
            with self.subTest(calc_overflow=entrada):
                res = executar_c(["--relatorio"], entrada)
                self.assertEqual(res.returncode, 3)
                self.assertEqual(res.stdout, "")
                self.assertIn("overflow", res.stderr.lower())

    def test_rejeita_linha_longa(self):
        entrada = "1\t100\t" + ("0" * 130) + "\n"
        res = executar_c(["--relatorio"], entrada)
        self.assertEqual(res.returncode, 2)
        self.assertEqual(res.stdout, "")
        self.assertIn("excede o limite", res.stderr.lower())

    def test_aceita_1000_produtos_e_rejeita_1001_produtos(self):
        linhas_1000 = "".join(f"{i}\t100\t1\n" for i in range(1, 1001))
        res_ok = executar_c(["--relatorio"], linhas_1000)
        self.assertEqual(res_ok.returncode, 0, msg=res_ok.stderr)
        dados = json.loads(res_ok.stdout)
        self.assertEqual(dados["total_produtos"], 1000)
        self.assertEqual(dados["total_unidades"], 1000)
        self.assertEqual(dados["valor_estoque_centavos"], 100000)

        linhas_1001 = linhas_1000 + "1001\t100\t1\n"
        res_err = executar_c(["--relatorio"], linhas_1001)
        self.assertEqual(res_err.returncode, 2)
        self.assertEqual(res_err.stdout, "")
        self.assertIn("1000", res_err.stderr)

    def test_argumento_desconhecido_e_extra(self):
        for args in [["--desconhecido"], ["--relatorio", "extra"]]:
            with self.subTest(args=args):
                res = executar_c(args, "")
                self.assertEqual(res.returncode, 1)
                self.assertEqual(res.stdout, "")
                self.assertIn("argumento invalido", res.stderr.lower())


class TestMenuInterativoC(unittest.TestCase):
    def test_ids_unicos_e_remocao_nao_reutiliza_id(self):
        entrada = (
            "1\nMouse A\nPerifericos\n100.00\n5\n"
            "1\nTeclado B\nPerifericos\n200.00\n4\n"
            "4\n1\n"
            "1\nMonitor C\nPerifericos\n599.00\n6\n"
            "2\n"
            "0\n"
        )
        res = executar_c([], entrada)
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertIn("Produto 'Mouse A' cadastrado com sucesso! ID: 1", res.stdout)
        self.assertIn("Produto 'Teclado B' cadastrado com sucesso! ID: 2", res.stdout)
        self.assertIn("Produto 'Monitor C' cadastrado com sucesso! ID: 3", res.stdout)
        listagem = res.stdout.split("ID    Nome")[1]
        self.assertNotIn("Mouse A", listagem)
        self.assertIn("Teclado B", listagem)
        self.assertIn("Monitor C", listagem)

    def test_relatorio_menu_limites_0_2_3_4_e_centavos_exatos(self):
        entrada = (
            "1\nProd0\nPerifericos\n0.10\n0\n"
            "1\nProd2\nPerifericos\n0.29\n2\n"
            "1\nProd3\nPerifericos\n10.00\n3\n"
            "1\nProd4\nPerifericos\n20.00\n4\n"
            "5\n"
            "0\n"
        )
        res = executar_c([], entrada)
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertIn("Valor total em estoque:        R$ 110.58", res.stdout)
        self.assertIn("--- Alertas de Reposicao (< 3 unidades) ---", res.stdout)
        secao_alertas = res.stdout.split("--- Alertas de Reposicao (< 3 unidades) ---")[1]
        self.assertIn("[ESGOTADO] Prod0: 0 unidade(s)", secao_alertas)
        self.assertIn("[URGENTE] Prod2: apenas 2 unidade(s)", secao_alertas)
        self.assertNotIn("Prod3", secao_alertas)
        self.assertNotIn("Prod4", secao_alertas)

    def test_eof_imediato_e_meio_operacao_encerram_sem_timeout(self):
        for entrada in ["", "1\nProduto Incompleto\n", "1\nMouse\nPerifericos\n"]:
            with self.subTest(entrada=entrada):
                res = executar_c([], entrada)
                self.assertEqual(res.returncode, 0)
                self.assertIn("fim de entrada", res.stdout.lower())

    def test_entrada_longa_nao_contamina_leitura_seguinte(self):
        nome_longo = "A" * 130
        entrada = (
            f"1\n{nome_longo}\n"
            "Mouse Valido\nPerifericos\n29.90\n5\n"
            "2\n"
            "0\n"
        )
        res = executar_c([], entrada)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Nome excede o limite de 100 bytes", res.stdout)
        self.assertIn("Produto 'Mouse Valido' cadastrado com sucesso! ID: 1", res.stdout)
        self.assertNotIn("AAAA", res.stdout)

    def test_rejeita_numeros_parciais_negativos_e_nao_finitos_no_menu(self):
        entrada = (
            "12abc\n"
            "1\nProduto Teste\nPerifericos\n"
            "-10\nNaN\ninf\n10.123\n12abc\n10,50\n29.90\n"
            "-2\n12abc\n4\n"
            "2\n0\n"
        )
        res = executar_c([], entrada)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Entrada invalida! Digite apenas numeros inteiros.", res.stdout)
        self.assertIn("Preco nao pode ser negativo.", res.stdout)
        self.assertIn("Entrada invalida! Use ponto decimal e ate 2 casas", res.stdout)
        self.assertIn("Valor fora da faixa permitida", res.stdout)
        self.assertIn("Produto 'Produto Teste' cadastrado com sucesso! ID: 1", res.stdout)
        self.assertIn("29.90", res.stdout)


if __name__ == "__main__":
    unittest.main()
