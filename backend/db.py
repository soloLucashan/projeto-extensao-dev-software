"""Acesso ao banco Oracle (PixelShop).

Todas as consultas SQL ficam centralizadas nas constantes SQL_* deste módulo com parâmetros
ligados (:param), enquanto as rotas em app.py apenas consomem as funções públicas.
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

CAMINHO_ENV = Path(__file__).resolve().parent / ".env"


def _carregar_env():
    """Carrega backend/.env explicitamente, sem sobrescrever variáveis já definidas."""
    if load_dotenv is not None and CAMINHO_ENV.is_file():
        load_dotenv(dotenv_path=CAMINHO_ENV, override=False)


_carregar_env()


class ErroBanco(Exception):
    """Falha de configuração, conexão ou consulta ao Oracle, sem expor credenciais."""


# Baseada na consulta nº 2 de queries.sql, usando LEFT JOIN para não omitir produtos sem categoria.
SQL_LISTAR_PRODUTOS = """
    SELECT p.id_produto,
           p.nome,
           p.descricao,
           p.preco,
           p.estoque,
           NVL(c.nome_categoria, 'Sem categoria') AS categoria
      FROM PRODUTO p
      LEFT JOIN CATEGORIA c ON p.id_categoria = c.id_categoria
     ORDER BY categoria, p.nome
"""


def _obter_config_oracle():
    """Lê ORACLE_USER, ORACLE_PASSWORD e ORACLE_DSN sem expor valores nas mensagens de erro."""
    config = {}
    for chave in ("ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"):
        valor = os.environ.get(chave)
        if valor is None or not valor.strip():
            raise ErroBanco(
                f"Variável '{chave}' não definida (veja backend/.env.example)"
            )
        config[chave] = valor if chave == "ORACLE_PASSWORD" else valor.strip()
    return config


def _conectar():
    try:
        import oracledb  # Import interno para manter os testes unitários executáveis sem Oracle ativo
    except ImportError as e:
        raise ErroBanco("Driver 'oracledb' não instalado no ambiente Python.") from e

    config = _obter_config_oracle()
    oracledb.defaults.fetch_decimals = True  # Preserva valores monetários em Decimal, evitando float
    try:
        return oracledb.connect(
            user=config["ORACLE_USER"],
            password=config["ORACLE_PASSWORD"],
            dsn=config["ORACLE_DSN"],
        )
    except oracledb.Error as e:
        raise ErroBanco(f"Não consegui conectar ao Oracle: {e}") from e


def _consultar(sql, parametros=None):
    """Executa uma consulta SELECT e retorna uma lista de dicionários (coluna -> valor)."""
    try:
        import oracledb
    except ImportError as e:
        raise ErroBanco("Driver 'oracledb' não instalado no ambiente Python.") from e

    try:
        with _conectar() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(sql, parametros or {})
                if not cursor.description:
                    return []
                colunas = [c[0].lower() for c in cursor.description]
                return [dict(zip(colunas, linha)) for linha in cursor.fetchall()]
    except ErroBanco:
        raise
    except oracledb.Error as e:
        raise ErroBanco(f"Erro na consulta: {e}") from e


def listar_produtos():
    """Retorna todos os produtos ordenados por categoria e nome, rejeitando itens sem preço válido."""
    produtos = _consultar(SQL_LISTAR_PRODUTOS)
    for item in produtos:
        if item.get("preco") is None:
            raise ErroBanco(
                f"Produto {item.get('id_produto', '?')} retornado sem preço válido."
            )
    return produtos
