"""PixelShop — aplicação web Flask integrada ao Oracle e ao módulo de relatório em C.

Execução local (dentro de backend/):
    .\\.venv\\Scripts\\python.exe app.py
Servidor disponível em http://127.0.0.1:5000
"""
from decimal import Decimal
from pathlib import Path

from flask import Flask, render_template

import db
import integracao_c

PASTA_SITE = Path(__file__).resolve().parent.parent / "site"

# Páginas institucionais estáticas permanecem em site/; rotas com dados dinâmicos usam templates Jinja2.
app = Flask(
    __name__,
    static_folder=str(PASTA_SITE),
    static_url_path="",
    template_folder="templates",
)

# Mesmo limite de estoque crítico (< 3) usado em programa-c/main.c e na consulta nº 5 de banco-dados/queries.sql.
LIMITE_ESTOQUE_BAIXO = 3


@app.template_filter("brl")
def formatar_real(valor):
    """Formata um valor numérico em reais (ex.: 1899.9 -> 'R$ 1.899,90'); preserva None sem converter em zero."""
    if valor is None:
        return "Preço indisponível"
    texto = f"{Decimal(valor):,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def situacao_estoque(quantidade):
    """Retorna (classe_css, texto) para o selo de disponibilidade no catálogo."""
    if quantidade <= 0:
        return "esgotado", "✕ Esgotado"
    if quantidade < LIMITE_ESTOQUE_BAIXO:
        return "baixo-estoque", f"⚠ Últimas unidades ({quantidade})"
    return "disponivel", f"✓ Em estoque ({quantidade} un.)"


def agrupar_por_categoria(produtos):
    """Agrupa produtos por categoria mantendo todos os itens mesmo se as categorias chegarem intercaladas."""
    categorias = {}
    for p in produtos:
        nome_categoria = p["categoria"]
        classe, texto = situacao_estoque(p["estoque"] or 0)
        categorias.setdefault(nome_categoria, []).append(
            {**p, "classe_estoque": classe, "texto_estoque": texto}
        )
    return categorias


@app.route("/")
def home():
    return app.send_static_file("index.html")


@app.route("/produtos.html")
def catalogo():
    try:
        produtos = db.listar_produtos()
    except db.ErroBanco as erro:
        app.logger.error("Falha ao carregar catálogo: %s", erro)
        return render_template("produtos.html", categorias={}, erro=True), 503
    return render_template(
        "produtos.html", categorias=agrupar_por_categoria(produtos), erro=False
    )


def _associar_itens_por_ids(ids_lista, produtos_por_id):
    """Associa os IDs retornados pelo módulo C aos nomes e estoques consultados no banco, sem recalcular totais."""
    return [
        {
            "id_produto": pid,
            "nome": produtos_por_id[pid]["nome"],
            "estoque": int(produtos_por_id[pid]["estoque"]),
        }
        for pid in ids_lista
    ]


@app.route("/relatorio.html")
def relatorio_estoque():
    try:
        produtos = db.listar_produtos()
    except db.ErroBanco as erro:
        app.logger.error("Falha ao consultar banco para relatório: %s", erro)
        return (
            render_template(
                "relatorio.html",
                resumo=None,
                valor_estoque_reais=None,
                criticos=[],
                esgotados=[],
                erro_mensagem="Não foi possível consultar o banco de dados no momento.",
            ),
            503,
        )

    try:
        resumo = integracao_c.gerar_relatorio_estoque(produtos)
    except integracao_c.ErroIntegracaoC as erro:
        app.logger.error("Falha na integração com módulo C: %s", erro.detalhe_log)
        return (
            render_template(
                "relatorio.html",
                resumo=None,
                valor_estoque_reais=None,
                criticos=[],
                esgotados=[],
                erro_mensagem="Não foi possível processar o relatório de estoque pelo módulo C no momento.",
            ),
            503,
        )

    produtos_por_id = {int(p["id_produto"]): p for p in produtos}
    criticos = _associar_itens_por_ids(resumo["ids_estoque_critico"], produtos_por_id)
    esgotados = _associar_itens_por_ids(resumo["ids_esgotados"], produtos_por_id)
    valor_estoque_reais = Decimal(resumo["valor_estoque_centavos"]) / Decimal(100)

    return render_template(
        "relatorio.html",
        resumo=resumo,
        valor_estoque_reais=valor_estoque_reais,
        criticos=criticos,
        esgotados=esgotados,
        erro_mensagem=None,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
