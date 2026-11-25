"""Integração entre o backend Flask e o módulo C (programa-c/build/main_bloco2.exe).

Etapas do fluxo:
- converter os produtos consultados no banco para o protocolo de entrada do C (centavos inteiros);
- executar o binário C sem shell, com timeout explícito e sem herdar credenciais Oracle;
- validar estritamente o JSON retornado sem recalcular indicadores em Python.
"""
import json
import os
import subprocess
from collections.abc import Iterable
from decimal import Decimal
from pathlib import Path

PASTA_RAIZ = Path(__file__).resolve().parent.parent
CAMINHO_EXECUTAVEL_C = PASTA_RAIZ / "programa-c" / "build" / "main_bloco2.exe"

TIMEOUT_SEGUNDOS = 5
MAX_ITENS_RELATORIO = 1000
TAM_MAX_LINHA_BYTES = 127
LLONG_MAX = (1 << 63) - 1

CAMPOS_OBRIGATORIOS_JSON = (
    "total_produtos",
    "total_unidades",
    "valor_estoque_centavos",
    "ids_estoque_critico",
    "ids_esgotados",
)

_VARS_AMBIENTE_PERMITIDAS = (
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATH",
    "PATHEXT",
)


class ErroIntegracaoC(Exception):
    """Falha na conversão, execução ou validação do relatório gerado pelo módulo C."""

    def __init__(self, mensagem_segura, detalhe_log=None):
        super().__init__(mensagem_segura)
        self.detalhe_log = detalhe_log or mensagem_segura


def _sanitizar_texto_log(texto, executavel=None):
    """Remove caminhos locais do projeto e credenciais conhecidas para uso apenas em log."""
    if not texto:
        return ""
    limpo = texto.strip().replace("\r\n", " | ").replace("\n", " | ")
    candidatos = [str(PASTA_RAIZ), str(CAMINHO_EXECUTAVEL_C)]
    if executavel is not None:
        candidatos.append(str(executavel))
        candidatos.append(str(Path(executavel).parent))
    for trecho in candidatos:
        if trecho:
            limpo = limpo.replace(trecho, "[CAMINHO]")
    for var in ("ORACLE_PASSWORD", "ORACLE_USER", "ORACLE_DSN"):
        segredo = os.environ.get(var)
        if segredo:
            limpo = limpo.replace(segredo, "[REDACTED]")
    return limpo[:300]


def _converter_inteiro_exato(valor, nome_campo, minimo, maximo=LLONG_MAX):
    """Converte int ou Decimal integral em int sem truncar e rejeitando bool/float."""
    if isinstance(valor, bool):
        raise ErroIntegracaoC(
            f"Campo '{nome_campo}' inválido para o módulo C.",
            f"Campo '{nome_campo}' recebido como bool.",
        )

    if isinstance(valor, int):
        inteiro = valor
    elif isinstance(valor, Decimal):
        if not valor.is_finite() or valor != valor.to_integral_value():
            raise ErroIntegracaoC(
                f"Campo '{nome_campo}' inválido para o módulo C.",
                f"Campo '{nome_campo}' Decimal não integral ou não finito.",
            )
        inteiro = int(valor)
    else:
        raise ErroIntegracaoC(
            f"Campo '{nome_campo}' inválido para o módulo C.",
            f"Campo '{nome_campo}' com tipo não suportado: {type(valor).__name__}.",
        )

    if inteiro < minimo or inteiro > maximo:
        raise ErroIntegracaoC(
            f"Campo '{nome_campo}' fora da faixa suportada pelo módulo C.",
            f"Campo '{nome_campo}' fora da faixa [{minimo}, {maximo}]: {inteiro}.",
        )
    return inteiro


def converter_preco_para_centavos(preco):
    """Converte Decimal finito não negativo (até 2 casas decimais) em centavos inteiros, rejeitando frações menores sem truncar."""
    if isinstance(preco, bool) or not isinstance(preco, Decimal):
        raise ErroIntegracaoC(
            "Preço inválido para envio ao módulo C.",
            f"Preço deve ser Decimal; recebido {type(preco).__name__}.",
        )

    if not preco.is_finite() or preco < 0:
        raise ErroIntegracaoC(
            "Preço inválido para envio ao módulo C.",
            "Preço negativo ou não finito.",
        )

    em_centavos = preco * Decimal(100)
    if em_centavos != em_centavos.to_integral_value():
        raise ErroIntegracaoC(
            "Preço possui mais de 2 casas decimais.",
            "Preço com fração menor que 1 centavo rejeitado sem truncamento.",
        )

    centavos = int(em_centavos)
    if centavos > LLONG_MAX:
        raise ErroIntegracaoC(
            "Preço excede o limite suportado pelo módulo C.",
            "Preço em centavos excede LLONG_MAX.",
        )
    return centavos


def montar_entrada_protocolo(produtos):
    """Valida e serializa os produtos para o contrato id<TAB>centavos<TAB>estoque."""
    if produtos is None or isinstance(produtos, (str, bytes, bytearray, dict)):
        raise ErroIntegracaoC(
            "Lista de produtos inválida para o módulo C.",
            f"Estrutura de produtos inválida: {type(produtos).__name__}.",
        )

    if not isinstance(produtos, Iterable):
        raise ErroIntegracaoC(
            "Lista de produtos inválida para o módulo C.",
            "Objeto de produtos não iterável.",
        )

    lista_produtos = list(produtos)
    if len(lista_produtos) > MAX_ITENS_RELATORIO:
        raise ErroIntegracaoC(
            "Quantidade de produtos excede o limite do módulo C.",
            f"Total de produtos ({len(lista_produtos)}) excede MAX_ITENS_RELATORIO ({MAX_ITENS_RELATORIO}).",
        )

    ids_vistos = set()
    linhas = []

    for indice, produto in enumerate(lista_produtos, start=1):
        if not isinstance(produto, dict):
            raise ErroIntegracaoC(
                "Registro de produto inválido para o módulo C.",
                f"Item {indice} não é dicionário.",
            )

        id_prod = _converter_inteiro_exato(produto.get("id_produto"), "id_produto", 1)
        if id_prod in ids_vistos:
            raise ErroIntegracaoC(
                "ID de produto duplicado na entrada do módulo C.",
                f"ID de produto duplicado antes de chamar o C: {id_prod}.",
            )
        ids_vistos.add(id_prod)

        preco_centavos = converter_preco_para_centavos(produto.get("preco"))
        estoque = _converter_inteiro_exato(produto.get("estoque"), "estoque", 0)

        linha = f"{id_prod}\t{preco_centavos}\t{estoque}"
        if len((linha + "\n").encode("ascii")) > TAM_MAX_LINHA_BYTES:
            raise ErroIntegracaoC(
                "Registro excede o tamanho máximo de linha do módulo C.",
                f"Linha do produto {id_prod} excede {TAM_MAX_LINHA_BYTES} bytes.",
            )
        linhas.append(linha)

    if not linhas:
        return "", ids_vistos
    return "\n".join(linhas) + "\n", ids_vistos


def _ambiente_minimo_subprocesso():
    """Retorna apenas variáveis de sistema essenciais, omitindo credenciais Oracle."""
    return {
        chave: os.environ[chave]
        for chave in _VARS_AMBIENTE_PERMITIDAS
        if chave in os.environ
    }


def executar_modulo_c(entrada_protocolo, executavel=None, timeout=TIMEOUT_SEGUNDOS):
    """Executa o binário C em modo --relatorio com argumentos fixos, sem shell e com timeout."""
    exe = Path(executavel) if executavel is not None else CAMINHO_EXECUTAVEL_C
    if not exe.is_file():
        raise ErroIntegracaoC(
            "Módulo C de relatório indisponível no ambiente.",
            "Executável do módulo C não encontrado no caminho configurado.",
        )

    try:
        resultado = subprocess.run(
            [str(exe), "--relatorio"],
            input=entrada_protocolo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
            env=_ambiente_minimo_subprocesso(),
        )
    except subprocess.TimeoutExpired as exc:
        raise ErroIntegracaoC(
            "Tempo esgotado ao processar relatório no módulo C.",
            f"Subprocesso do módulo C excedeu timeout de {timeout}s.",
        ) from exc
    except FileNotFoundError as exc:
        raise ErroIntegracaoC(
            "Módulo C de relatório indisponível no ambiente.",
            "Executável do módulo C não localizado ao iniciar subprocesso.",
        ) from exc
    except PermissionError as exc:
        raise ErroIntegracaoC(
            "Sem permissão para executar o módulo C de relatório.",
            "Permissão negada ao executar binário do módulo C.",
        ) from exc
    except OSError as exc:
        raise ErroIntegracaoC(
            "Falha ao executar o módulo C de relatório.",
            f"Erro de sistema operacional ({type(exc).__name__}) ao executar módulo C.",
        ) from exc

    if resultado.returncode != 0:
        diagnostico = _sanitizar_texto_log(resultado.stderr, exe)
        raise ErroIntegracaoC(
            "Módulo C recusou os dados ou falhou ao gerar o relatório.",
            f"Módulo C retornou código {resultado.returncode}: {diagnostico}",
        )

    return resultado.stdout


def _exigir_int_nao_bool(valor, nome_campo, minimo=0):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < minimo:
        raise ErroIntegracaoC(
            "Resposta inválida recebida do módulo C.",
            f"Campo '{nome_campo}' com tipo/faixa inválida no JSON do C.",
        )
    return valor


def _validar_lista_ids(lista, nome_campo, ids_esperados):
    if not isinstance(lista, list):
        raise ErroIntegracaoC(
            "Resposta inválida recebida do módulo C.",
            f"Campo '{nome_campo}' não é lista no JSON do C.",
        )
    vistos = set()
    validados = []
    for item in lista:
        pid = _exigir_int_nao_bool(item, nome_campo, minimo=1)
        if pid in vistos:
            raise ErroIntegracaoC(
                "Resposta inválida recebida do módulo C.",
                f"ID duplicado ({pid}) em '{nome_campo}' no JSON do C.",
            )
        if pid not in ids_esperados:
            raise ErroIntegracaoC(
                "Resposta inconsistente recebida do módulo C.",
                f"ID desconhecido ({pid}) em '{nome_campo}' no JSON do C.",
            )
        vistos.add(pid)
        validados.append(pid)
    return validados


def validar_resposta_c(saida_stdout, ids_esperados, total_esperado):
    """Valida a estrutura, tipos e coerência semântica do JSON retornado pelo C."""
    if not isinstance(saida_stdout, str) or not saida_stdout.strip():
        raise ErroIntegracaoC(
            "Resposta vazia recebida do módulo C.",
            "Stdout vazio ao aguardar JSON do módulo C.",
        )

    try:
        dados = json.loads(saida_stdout)
    except json.JSONDecodeError as exc:
        raise ErroIntegracaoC(
            "Resposta em formato inválido recebida do módulo C.",
            f"Falha ao decodificar JSON do módulo C: {exc.msg}.",
        ) from exc

    if not isinstance(dados, dict):
        raise ErroIntegracaoC(
            "Resposta inválida recebida do módulo C.",
            "JSON retornado pelo módulo C não é um objeto.",
        )

    chaves_esperadas = set(CAMPOS_OBRIGATORIOS_JSON)
    chaves_recebidas = set(dados.keys())
    if chaves_recebidas != chaves_esperadas:
        raise ErroIntegracaoC(
            "Resposta incompleta ou divergente recebida do módulo C.",
            f"Chaves JSON divergentes: recebidas={sorted(chaves_recebidas)}.",
        )

    total_produtos = _exigir_int_nao_bool(dados["total_produtos"], "total_produtos", minimo=0)
    if total_produtos != total_esperado:
        raise ErroIntegracaoC(
            "Resposta inconsistente recebida do módulo C.",
            f"total_produtos divergente: esperado={total_esperado}, obtido={total_produtos}.",
        )

    total_unidades = _exigir_int_nao_bool(dados["total_unidades"], "total_unidades", minimo=0)
    valor_centavos = _exigir_int_nao_bool(
        dados["valor_estoque_centavos"], "valor_estoque_centavos", minimo=0
    )
    ids_criticos = _validar_lista_ids(
        dados["ids_estoque_critico"], "ids_estoque_critico", ids_esperados
    )
    ids_esgotados = _validar_lista_ids(
        dados["ids_esgotados"], "ids_esgotados", ids_esperados
    )

    if not set(ids_esgotados).issubset(set(ids_criticos)):
        raise ErroIntegracaoC(
            "Resposta inconsistente recebida do módulo C.",
            "ids_esgotados não está contido em ids_estoque_critico.",
        )

    return {
        "total_produtos": total_produtos,
        "total_unidades": total_unidades,
        "valor_estoque_centavos": valor_centavos,
        "ids_estoque_critico": ids_criticos,
        "ids_esgotados": ids_esgotados,
    }


def gerar_relatorio_estoque(produtos, executavel=None, timeout=TIMEOUT_SEGUNDOS):
    """Encadeia validação da entrada, chamada do executável C e validação do JSON."""
    entrada, ids_esperados = montar_entrada_protocolo(produtos)
    stdout_c = executar_modulo_c(entrada, executavel=executavel, timeout=timeout)
    return validar_resposta_c(stdout_c, ids_esperados, total_esperado=len(ids_esperados))
