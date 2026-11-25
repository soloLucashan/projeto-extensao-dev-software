# Integração com o módulo C (`--relatorio`)

Este documento descreve o protocolo de entrada, saída, limites e códigos de retorno do executável `programa-c/build/main_bloco2.exe` usado pelo backend Flask em `backend/integracao_c.py`. Para instruções de compilação e execução geral do projeto, veja [README.md](../README.md).

## Formas de execução

| Chamada | Comportamento |
|---|---|
| `programa-c\build\main_bloco2.exe` | Abre o menu interativo no terminal, operando em memória. |
| `programa-c\build\main_bloco2.exe --relatorio` | Lê produtos pela entrada padrão (`stdin`), calcula o resumo e imprime um único objeto JSON em `stdout`. |
| Qualquer outro argumento ou argumento extra | Escreve mensagem de erro em `stderr` e retorna código `1`. |

O backend chama o executável diretamente via `subprocess.run([caminho_exe, "--relatorio"], input=..., text=True, capture_output=True, timeout=...)`, sem shell e sem passar variáveis `ORACLE_*`. Não utilize o executável legado `programa-c/main.exe`.

## Entrada (`stdin`)

- Formato: texto ASCII, um produto por linha, sem cabeçalho, com três colunas separadas por tabulação (`\t`):
  ```text
  id_produto<TAB>preco_centavos<TAB>estoque
  ```
- Quebras de linha: aceita `LF` (`\n`) e `CRLF` (`\r\n`), com ou sem quebra de linha ao final da última linha.
- Entrada vazia: permitida; gera um JSON válido com totais zerados e listas vazias.
- Linhas em branco: rejeitadas; toda linha presente deve conter exatamente três colunas válidas.

Regras dos campos:

- `id_produto`: inteiro positivo (`1` até `LLONG_MAX`), sem repetição na mesma execução.
- `preco_centavos`: inteiro não negativo (`0` até `LLONG_MAX`), já convertido em centavos (por exemplo, `R$ 100,00` vira `10000` e `R$ 0,29` vira `29`). Não aceita ponto nem vírgula.
- `estoque`: inteiro não negativo (`0` até `LLONG_MAX`).

Validação numérica: apenas dígitos ASCII (`0–9`), sem sinal `+`, sem espaços antes ou depois e sem caracteres extras (`12abc`, `+10`, ` 10`, `10 ` e `10.50` são rejeitados). Nenhum campo ou linha é truncado silenciosamente.

## Saída (`stdout`)

Quando o código de retorno é `0`, o programa imprime apenas um objeto JSON em `stdout`:

```json
{
  "total_produtos": 2,
  "total_unidades": 6,
  "valor_estoque_centavos": 120000,
  "ids_estoque_critico": [1],
  "ids_esgotados": []
}
```

Campos retornados:

- `total_produtos` (`int`): quantidade de produtos processados.
- `total_unidades` (`int`, 64 bits): soma do estoque de todos os itens.
- `valor_estoque_centavos` (`int`, 64 bits): soma de `preco_centavos * estoque` feita com aritmética inteira exata (`long long`, sem `float` ou `double`).
- `ids_estoque_critico` (`list[int]`): IDs com `estoque < 3` (`0`, `1` ou `2`), na ordem de entrada.
- `ids_esgotados` (`list[int]`): IDs com `estoque == 0`, na ordem de entrada. Todo ID desta lista também aparece em `ids_estoque_critico`.

Em caso de erro, `stdout` permanece vazio e a mensagem de diagnóstico vai para `stderr`.

## Limites

| Limite | Valor | Comportamento ao exceder |
|---|---|---|
| Máximo de produtos por chamada | `MAX_ITENS_RELATORIO = 1000` | Erro em `stderr`, retorno `2`. |
| Buffer por linha | `TAM_LINHA_RELATORIO = 128` bytes (até `127` bytes incluindo `\r\n`, ou até `126` bytes antes de `\n` / `125` antes de `\r\n`) | Erro em `stderr`, retorno `2`. |
| Inteiros e acumuladores | `long long` (`LLONG_MAX = 9223372036854775807`) | Erro de leitura (`2`) ou overflow aritmético (`3`) em `stderr`. |

## Códigos de retorno

| Código | Significado | `stdout` | `stderr` |
|---:|---|---|---|
| `0` | Sucesso | Objeto JSON completo | Vazio |
| `1` | Argumento desconhecido ou em excesso | Vazio | Mensagem de uso |
| `2` | Erro de validação na entrada (colunas ausentes/extras, linha vazia, ID inválido ou duplicado, número inválido, linha acima de 127 bytes, mais de 1000 produtos ou inteiro acima de `LLONG_MAX`) | Vazio | Linha e motivo do erro |
| `3` | Overflow aritmético em `preco_centavos * estoque` ou nas somas | Vazio | Diagnóstico e ID do item |
| `4` | Erro de leitura (`ferror`) em `stdin` | Vazio | Mensagem de erro de I/O |

## Exemplos

### Dois produtos válidos

Entrada (`stdin`):

```text
1	10000	2
2	25000	4
```

Retorno `0`, `stderr` vazio e `stdout`:

```json
{
  "total_produtos": 2,
  "total_unidades": 6,
  "valor_estoque_centavos": 120000,
  "ids_estoque_critico": [1],
  "ids_esgotados": []
}
```

### Entrada vazia

Entrada (`stdin`): vazia. Retorno `0`, `stderr` vazio e `stdout`:

```json
{
  "total_produtos": 0,
  "total_unidades": 0,
  "valor_estoque_centavos": 0,
  "ids_estoque_critico": [],
  "ids_esgotados": []
}
```

### Exemplos de erro em `stderr`

- Argumento desconhecido (`--invalido`), retorno `1`:
  `Argumento invalido. Uso: programa-c/build/main_bloco2.exe [--relatorio]`
- ID duplicado, retorno `2`:
  `Erro na linha 2: id_produto duplicado (1).`
- Valor parcialmente numérico (`12abc`), retorno `2`:
  `Erro na linha 1 (preco_centavos '12abc'): formato numerico invalido (esperado inteiro >= 0).`
- Campo ausente, retorno `2`:
  `Erro na linha 1: campo estoque ausente (esperado 3 colunas separadas por TAB).`
- Campo extra, retorno `2`:
  `Erro na linha 1: campos extras encontrados (esperado exatamente 3 colunas).`
- Linha acima de 127 bytes, retorno `2`:
  `Erro na linha 1: linha excede o limite maximo de 127 bytes de buffer.`
- Overflow na multiplicação (`LLONG_MAX * 2`), retorno `3`:
  `Erro no calculo do resumo: Overflow ao multiplicar preco x estoque no item ID 1.`
