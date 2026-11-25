/*
 * Projeto de Extensao - Desenvolvimento de Software
 * PixelShop - Sistema de Estoque (menu interativo em memoria e modo --relatorio)
 * UNINOVE - Ciencia da Computacao (Noturno 2026) | Prof.a Priscilla Cunha
 *
 * Autor original deste arquivo: Lucas Byoung Ki Han (RA 3025103388)
 *
 * Equipe atual do projeto (8 integrantes — ver creditos por modulo em documentacao/EQUIPE.md):
 * - Julia Zezilia Rodrigues (RA 3026105026)
 * - Gabriel Cole Ambrosio (RA 3126100300)
 * - Henrique Capetto Fernandez (RA 3126103000)
 * - Lucas Byoung Ki Han (RA 3025103388)
 * - Sophie De Brito Zerbinati (RA 3126103086)
 * - Eduardo Vieira Silva (RA 3026105026)
 * - Riquelly Bagatin (RA 3025103463)
 * - Matheus Nilcen Alves (RA 3026104544)
 *
 * Limites e contratos documentados (em bytes / quantidades):
 * - Menu interativo: opera em memoria com vetor estatico de ate MAX_PRODUTOS (100) produtos.
 * - Modo --relatorio: processa ate MAX_ITENS_RELATORIO (1000) linhas via stdin e emite JSON em stdout.
 * - Strings de nome e categoria: buffer de 101 bytes (ate 100 bytes uteis + '\0').
 *   Por ser medido em bytes, 101 bytes nao garante 100 caracteres Unicode multibyte.
 * - Linha no modo --relatorio: buffer de 128 bytes (ate 127 bytes contando eventual CRLF).
 * - Valores monetarios armazenados e somados exclusivamente em centavos inteiros (long long), sem float/double.
 */

#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_PRODUTOS 100
#define MAX_ITENS_RELATORIO 1000
#define LIMITE_ESTOQUE_CRITICO 3

#define TAM_NOME 101
#define TAM_CATEGORIA 101
#define TAM_LINHA_MENU 256
#define TAM_LINHA_RELATORIO 128

/* Codigos de retorno documentados do programa */
#define EXIT_SUCESSO 0
#define EXIT_ARG_INVALIDO 1
#define EXIT_ERRO_VALIDACAO 2
#define EXIT_ERRO_OVERFLOW 3
#define EXIT_ERRO_IO 4

/* Categorias do banco Oracle — manter alinhado com insert_data.sql */
#define NUM_CATEGORIAS 4
static const char *CATEGORIAS_VALIDAS[NUM_CATEGORIAS] = {
    "Smartphones",
    "Notebooks",
    "Perifericos",
    "Pecas e Componentes",
};

typedef enum
{
    LEITURA_OK = 0,
    LEITURA_EOF,
    LEITURA_LONGA
} StatusLeitura;

typedef enum
{
    PARSE_OK = 0,
    PARSE_VAZIO,
    PARSE_FORMATO,
    PARSE_OVERFLOW,
    PARSE_FAIXA
} StatusParse;

typedef struct
{
    int id;
    char nome[TAM_NOME];
    char categoria[TAM_CATEGORIA];
    long long preco_centavos;
    int qtd_estoque;
} Produto;

typedef struct
{
    long long id;
    long long preco_centavos;
    long long estoque;
} ItemEstoque;

typedef struct
{
    int total_produtos;
    long long total_unidades;
    long long valor_estoque_centavos;
    long long ids_estoque_critico[MAX_ITENS_RELATORIO];
    int total_criticos;
    long long ids_esgotados[MAX_ITENS_RELATORIO];
    int total_esgotados;
} ResumoEstoque;

static Produto produtos[MAX_PRODUTOS];
static int totalProdutos = 0;
static int proximoId = 1;

/* Soma segura para inteiros nao negativos (evita overflow assinado) */
static int somarLLSeguro(long long a, long long b, long long *out)
{
    if (a < 0 || b < 0 || a > LLONG_MAX - b)
    {
        return 0;
    }
    *out = a + b;
    return 1;
}

/* Multiplicacao segura para inteiros nao negativos (evita overflow assinado) */
static int multiplicarLLSeguro(long long a, long long b, long long *out)
{
    if (a < 0 || b < 0)
    {
        return 0;
    }
    if (a == 0 || b == 0)
    {
        *out = 0;
        return 1;
    }
    if (a > LLONG_MAX / b)
    {
        return 0;
    }
    *out = a * b;
    return 1;
}

/*
 * Funcao de calculo compartilhada entre o modo --relatorio e o menu interativo.
 * Garante a mesma regra de estoque critico (< 3), esgotado (== 0) e checagem
 * de overflow em multiplicacoes e somas sem usar ponto flutuante.
 */
static int calcularResumoEstoque(
    const ItemEstoque *itens,
    int qtd,
    ResumoEstoque *resumo,
    char *erro,
    size_t tam_erro)
{
    if (resumo == NULL || qtd < 0 || qtd > MAX_ITENS_RELATORIO)
    {
        snprintf(erro, tam_erro, "Quantidade de itens invalida para o resumo (%d).", qtd);
        return 0;
    }

    memset(resumo, 0, sizeof(*resumo));
    resumo->total_produtos = qtd;

    for (int i = 0; i < qtd; i++)
    {
        long long id = itens[i].id;
        long long preco = itens[i].preco_centavos;
        long long estoque = itens[i].estoque;
        long long subtotal = 0;

        if (id <= 0 || preco < 0 || estoque < 0)
        {
            snprintf(
                erro,
                tam_erro,
                "Item %d possui valores invalidos (id=%lld, preco_centavos=%lld, estoque=%lld).",
                i + 1,
                id,
                preco,
                estoque);
            return 0;
        }

        if (!somarLLSeguro(resumo->total_unidades, estoque, &resumo->total_unidades))
        {
            snprintf(erro, tam_erro, "Overflow ao somar total de unidades no item ID %lld.", id);
            return 0;
        }

        if (!multiplicarLLSeguro(preco, estoque, &subtotal))
        {
            snprintf(erro, tam_erro, "Overflow ao multiplicar preco x estoque no item ID %lld.", id);
            return 0;
        }

        if (!somarLLSeguro(resumo->valor_estoque_centavos, subtotal, &resumo->valor_estoque_centavos))
        {
            snprintf(erro, tam_erro, "Overflow ao somar valor total em estoque no item ID %lld.", id);
            return 0;
        }

        if (estoque < LIMITE_ESTOQUE_CRITICO)
        {
            resumo->ids_estoque_critico[resumo->total_criticos++] = id;
        }
        if (estoque == 0)
        {
            resumo->ids_esgotados[resumo->total_esgotados++] = id;
        }
    }

    return 1;
}

/* Conversao estrita de string inteira decimal para long long dentro de [min_val, max_val] */
static StatusParse parseLongLongStrict(
    const char *texto,
    long long min_val,
    long long max_val,
    long long *out)
{
    size_t inicio = 0;
    char *fim = NULL;
    long long valor = 0;

    if (texto == NULL || texto[0] == '\0')
    {
        return PARSE_VAZIO;
    }

    if (texto[0] == '-')
    {
        inicio = 1;
    }

    if (texto[inicio] < '0' || texto[inicio] > '9')
    {
        return PARSE_FORMATO;
    }

    for (size_t i = inicio; texto[i] != '\0'; i++)
    {
        if (texto[i] < '0' || texto[i] > '9')
        {
            return PARSE_FORMATO;
        }
    }

    errno = 0;
    valor = strtoll(texto, &fim, 10);
    if (errno == ERANGE)
    {
        return PARSE_OVERFLOW;
    }
    if (fim == texto || *fim != '\0')
    {
        return PARSE_FORMATO;
    }
    if (valor < min_val || valor > max_val)
    {
        return PARSE_FAIXA;
    }

    *out = valor;
    return PARSE_OK;
}

/*
 * Converte preco decimal textual do menu diretamente para centavos (long long),
 * sem float/double. Politica aceita: ^[0-9]+(\.[0-9]{1,2})?$
 * Exemplos aceitos: "0", "0.10", "0.29", "29.9", "1899.90".
 * Rejeita negativo, NaN/inf, virgula, espacos, sinais '+' e > 2 casas decimais.
 */
static StatusParse parsePrecoCentavosStrict(const char *texto, long long *out_centavos)
{
    size_t i = 0;
    int negativo = 0;
    long long reais = 0;
    long long centavos_dec = 0;
    long long centavos_reais = 0;
    long long total = 0;
    const long long max_reais = LLONG_MAX / 100;

    if (texto == NULL || texto[0] == '\0')
    {
        return PARSE_VAZIO;
    }

    if (texto[0] == '-')
    {
        negativo = 1;
        i = 1;
    }

    if (texto[i] < '0' || texto[i] > '9')
    {
        return PARSE_FORMATO;
    }

    /* Valida toda a sintaxe antes de checar sinal para distinguir '-5' de '-abc' */
    size_t j = i;
    while (texto[j] >= '0' && texto[j] <= '9')
    {
        j++;
    }

    if (texto[j] == '.')
    {
        size_t casas = 0;
        j++;
        while (texto[j] >= '0' && texto[j] <= '9')
        {
            casas++;
            j++;
        }
        if (casas == 0 || casas > 2 || texto[j] != '\0')
        {
            return PARSE_FORMATO;
        }
    }
    else if (texto[j] != '\0')
    {
        return PARSE_FORMATO;
    }

    if (negativo)
    {
        return PARSE_FAIXA;
    }

    while (texto[i] >= '0' && texto[i] <= '9')
    {
        long long digito = texto[i] - '0';
        if (reais > (max_reais - digito) / 10)
        {
            return PARSE_OVERFLOW;
        }
        reais = reais * 10 + digito;
        i++;
    }

    if (texto[i] == '.')
    {
        i++;
        long long d1 = texto[i] - '0';
        i++;
        if (texto[i] != '\0')
        {
            long long d2 = texto[i] - '0';
            centavos_dec = d1 * 10 + d2;
        }
        else
        {
            centavos_dec = d1 * 10;
        }
    }

    if (!multiplicarLLSeguro(reais, 100, &centavos_reais) ||
        !somarLLSeguro(centavos_reais, centavos_dec, &total))
    {
        return PARSE_OVERFLOW;
    }

    *out_centavos = total;
    return PARSE_OK;
}

static void formatarCentavos(long long centavos, char *buf, size_t tam)
{
    long long reais = centavos / 100;
    long long resto = centavos % 100;
    if (resto < 0)
    {
        resto = -resto;
    }
    snprintf(buf, tam, "%lld.%02lld", reais, resto);
}

/* Remove '\n' e '\r' finais; drena resto da linha se excedeu o buffer no menu */
static StatusLeitura lerLinhaControlada(char *buf, size_t tam)
{
    size_t len = 0;

    if (fgets(buf, (int)tam, stdin) == NULL)
    {
        buf[0] = '\0';
        return LEITURA_EOF;
    }

    len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n')
    {
        buf[--len] = '\0';
        if (len > 0 && buf[len - 1] == '\r')
        {
            buf[--len] = '\0';
        }
        return LEITURA_OK;
    }

    /* Sem '\n': verifica se foi EOF na ultima linha ou linha maior que o buffer */
    if (!feof(stdin))
    {
        int c = fgetc(stdin);
        if (c != EOF)
        {
            if (c != '\n')
            {
                while ((c = getchar()) != '\n' && c != EOF)
                    ;
            }
            buf[0] = '\0';
            return LEITURA_LONGA;
        }
    }

    if (len > 0 && buf[len - 1] == '\r')
    {
        buf[--len] = '\0';
    }
    return LEITURA_OK;
}

static const char *descreverErroParse(StatusParse st)
{
    switch (st)
    {
    case PARSE_VAZIO:
        return "valor vazio";
    case PARSE_FORMATO:
        return "formato numerico invalido";
    case PARSE_OVERFLOW:
        return "valor excede o limite de inteiro 64 bits";
    case PARSE_FAIXA:
        return "valor fora da faixa permitida";
    case PARSE_OK:
    default:
        return "";
    }
}

/* Modo automatico (--relatorio): leitura via stdin, validacao estrita e JSON em stdout */

static void imprimirArrayLLJson(const long long *valores, int qtd)
{
    printf("[");
    for (int i = 0; i < qtd; i++)
    {
        if (i > 0)
        {
            printf(", ");
        }
        printf("%lld", valores[i]);
    }
    printf("]");
}

static int executarModoRelatorio(void)
{
    static ItemEstoque itens[MAX_ITENS_RELATORIO];
    static ResumoEstoque resumo;
    char linha[TAM_LINHA_RELATORIO];
    char erro[256];
    int total_itens = 0;
    int num_linha = 0;

    while (fgets(linha, sizeof(linha), stdin) != NULL)
    {
        num_linha++;
        size_t len = strlen(linha);

        if (len > 0 && linha[len - 1] == '\n')
        {
            linha[--len] = '\0';
            if (len > 0 && linha[len - 1] == '\r')
            {
                linha[--len] = '\0';
            }
        }
        else if (!feof(stdin))
        {
            int prox = fgetc(stdin);
            if (prox != EOF)
            {
                fprintf(
                    stderr,
                    "Erro na linha %d: linha excede o limite maximo de %d bytes de buffer.\n",
                    num_linha,
                    TAM_LINHA_RELATORIO - 1);
                return EXIT_ERRO_VALIDACAO;
            }
            if (len > 0 && linha[len - 1] == '\r')
            {
                linha[--len] = '\0';
            }
        }
        else
        {
            if (len > 0 && linha[len - 1] == '\r')
            {
                linha[--len] = '\0';
            }
        }

        if (linha[0] == '\0')
        {
            fprintf(stderr, "Erro na linha %d: linha vazia ou campos ausentes.\n", num_linha);
            return EXIT_ERRO_VALIDACAO;
        }

        char *tab1 = strchr(linha, '\t');
        if (tab1 == NULL)
        {
            fprintf(
                stderr,
                "Erro na linha %d: campos ausentes (esperado id_produto<TAB>preco_centavos<TAB>estoque).\n",
                num_linha);
            return EXIT_ERRO_VALIDACAO;
        }
        *tab1 = '\0';

        char *campo_id = linha;
        char *campo_preco = tab1 + 1;

        char *tab2 = strchr(campo_preco, '\t');
        if (tab2 == NULL)
        {
            fprintf(
                stderr,
                "Erro na linha %d: campo estoque ausente (esperado 3 colunas separadas por TAB).\n",
                num_linha);
            return EXIT_ERRO_VALIDACAO;
        }
        *tab2 = '\0';

        char *campo_estoque = tab2 + 1;
        if (strchr(campo_estoque, '\t') != NULL)
        {
            fprintf(
                stderr,
                "Erro na linha %d: campos extras encontrados (esperado exatamente 3 colunas).\n",
                num_linha);
            return EXIT_ERRO_VALIDACAO;
        }

        if (total_itens >= MAX_ITENS_RELATORIO)
        {
            fprintf(
                stderr,
                "Erro na linha %d: limite maximo de %d produtos excedido.\n",
                num_linha,
                MAX_ITENS_RELATORIO);
            return EXIT_ERRO_VALIDACAO;
        }

        long long id = 0;
        long long preco_centavos = 0;
        long long estoque = 0;

        StatusParse st_id = parseLongLongStrict(campo_id, 1, LLONG_MAX, &id);
        if (st_id != PARSE_OK)
        {
            fprintf(
                stderr,
                "Erro na linha %d (id_produto '%s'): %s (esperado inteiro positivo).\n",
                num_linha,
                campo_id,
                descreverErroParse(st_id));
            return EXIT_ERRO_VALIDACAO;
        }

        StatusParse st_preco = parseLongLongStrict(campo_preco, 0, LLONG_MAX, &preco_centavos);
        if (st_preco != PARSE_OK)
        {
            fprintf(
                stderr,
                "Erro na linha %d (preco_centavos '%s'): %s (esperado inteiro >= 0).\n",
                num_linha,
                campo_preco,
                descreverErroParse(st_preco));
            return EXIT_ERRO_VALIDACAO;
        }

        StatusParse st_estoque = parseLongLongStrict(campo_estoque, 0, LLONG_MAX, &estoque);
        if (st_estoque != PARSE_OK)
        {
            fprintf(
                stderr,
                "Erro na linha %d (estoque '%s'): %s (esperado inteiro >= 0).\n",
                num_linha,
                campo_estoque,
                descreverErroParse(st_estoque));
            return EXIT_ERRO_VALIDACAO;
        }

        for (int i = 0; i < total_itens; i++)
        {
            if (itens[i].id == id)
            {
                fprintf(
                    stderr,
                    "Erro na linha %d: id_produto duplicado (%lld).\n",
                    num_linha,
                    id);
                return EXIT_ERRO_VALIDACAO;
            }
        }

        itens[total_itens].id = id;
        itens[total_itens].preco_centavos = preco_centavos;
        itens[total_itens].estoque = estoque;
        total_itens++;
    }

    if (ferror(stdin))
    {
        fprintf(stderr, "Erro de I/O ao ler entrada padrao.\n");
        return EXIT_ERRO_IO;
    }

    if (!calcularResumoEstoque(itens, total_itens, &resumo, erro, sizeof(erro)))
    {
        fprintf(stderr, "Erro no calculo do resumo: %s\n", erro);
        return EXIT_ERRO_OVERFLOW;
    }

    printf("{\n");
    printf("  \"total_produtos\": %d,\n", resumo.total_produtos);
    printf("  \"total_unidades\": %lld,\n", resumo.total_unidades);
    printf("  \"valor_estoque_centavos\": %lld,\n", resumo.valor_estoque_centavos);
    printf("  \"ids_estoque_critico\": ");
    imprimirArrayLLJson(resumo.ids_estoque_critico, resumo.total_criticos);
    printf(",\n");
    printf("  \"ids_esgotados\": ");
    imprimirArrayLLJson(resumo.ids_esgotados, resumo.total_esgotados);
    printf("\n}\n");

    return EXIT_SUCESSO;
}

/* Modo interativo (menu em terminal) */

/* Converte string ASCII para minusculas — busca case-insensitive */
static void paraMinusculas(char *str)
{
    for (int i = 0; str[i]; i++)
    {
        str[i] = (char)tolower((unsigned char)str[i]);
    }
}

/* Verifica se a categoria digitada bate com as do banco Oracle (case-insensitive) */
static int categoriaValida(const char *categoria_digitada)
{
    char digitada_min[TAM_CATEGORIA];
    char valida_min[TAM_CATEGORIA];

    snprintf(digitada_min, sizeof(digitada_min), "%s", categoria_digitada);
    paraMinusculas(digitada_min);

    for (int i = 0; i < NUM_CATEGORIAS; i++)
    {
        snprintf(valida_min, sizeof(valida_min), "%s", CATEGORIAS_VALIDAS[i]);
        paraMinusculas(valida_min);
        if (strcmp(digitada_min, valida_min) == 0)
        {
            return 1;
        }
    }
    return 0;
}

/* Retorna 1 em sucesso, 0 em EOF */
static int lerInteiroControlado(
    const char *mensagem,
    long long min_val,
    long long max_val,
    int *out)
{
    char linha[TAM_LINHA_MENU];

    while (1)
    {
        long long valor = 0;
        printf("%s", mensagem);
        StatusLeitura st_leitura = lerLinhaControlada(linha, sizeof(linha));
        if (st_leitura == LEITURA_EOF)
        {
            printf("\nFim de entrada detectado.\n");
            return 0;
        }
        if (st_leitura == LEITURA_LONGA)
        {
            printf("Entrada muito longa! Digite apenas um numero inteiro.\n");
            continue;
        }

        StatusParse st_parse = parseLongLongStrict(linha, min_val, max_val, &valor);
        if (st_parse == PARSE_OK)
        {
            *out = (int)valor;
            return 1;
        }
        if (st_parse == PARSE_FAIXA)
        {
            printf("Valor fora da faixa permitida (%lld a %lld). Tente novamente.\n", min_val, max_val);
        }
        else if (st_parse == PARSE_OVERFLOW)
        {
            printf("Numero muito grande! Tente novamente.\n");
        }
        else
        {
            printf("Entrada invalida! Digite apenas numeros inteiros.\n");
        }
    }
}

/* Retorna 1 em sucesso, 0 em EOF */
static int lerPrecoCentavosControlado(const char *mensagem, long long *out_centavos)
{
    char linha[TAM_LINHA_MENU];

    while (1)
    {
        printf("%s", mensagem);
        StatusLeitura st_leitura = lerLinhaControlada(linha, sizeof(linha));
        if (st_leitura == LEITURA_EOF)
        {
            printf("\nFim de entrada detectado.\n");
            return 0;
        }
        if (st_leitura == LEITURA_LONGA)
        {
            printf("Entrada muito longa! Use formato decimal simples (ex: 29.90).\n");
            continue;
        }

        StatusParse st_parse = parsePrecoCentavosStrict(linha, out_centavos);
        if (st_parse == PARSE_OK)
        {
            return 1;
        }
        if (st_parse == PARSE_FAIXA)
        {
            printf("Preco nao pode ser negativo. Tente novamente.\n");
        }
        else if (st_parse == PARSE_OVERFLOW)
        {
            printf("Preco excede o limite suportado. Tente novamente.\n");
        }
        else
        {
            printf("Entrada invalida! Use ponto decimal e ate 2 casas (ex: 29.90).\n");
        }
    }
}

static void exibirMenu(void)
{
    printf("\n===== PIXELSHOP - Sistema de Estoque =====");
    printf("\n 1. Cadastrar produto");
    printf("\n 2. Listar todos os produtos");
    printf("\n 3. Buscar produto por nome");
    printf("\n 4. Remover produto");
    printf("\n 5. Relatorio de estoque");
    printf("\n 6. Listar por categoria");
    printf("\n 0. Sair");
    printf("\n==========================================\n");
}

/* Retorna 1 para continuar menu, 0 se ocorreu EOF */
static int cadastrarProduto(void)
{
    if (totalProdutos >= MAX_PRODUTOS)
    {
        printf("Limite de %d produtos atingido! Contate o suporte.\n", MAX_PRODUTOS);
        return 1;
    }

    if (proximoId == INT_MAX)
    {
        printf("Limite de IDs da sessao atingido.\n");
        return 1;
    }

    Produto p;
    memset(&p, 0, sizeof(p));

    while (1)
    {
        printf("Nome do produto: ");
        StatusLeitura st = lerLinhaControlada(p.nome, sizeof(p.nome));
        if (st == LEITURA_EOF)
        {
            printf("\nCadastro cancelado (fim de entrada).\n");
            return 0;
        }
        if (st == LEITURA_LONGA)
        {
            printf("Nome excede o limite de %d bytes. Digite um nome menor.\n", TAM_NOME - 1);
            continue;
        }
        if (p.nome[0] == '\0')
        {
            printf("Nome nao pode ser vazio. Cadastro cancelado.\n");
            return 1;
        }
        break;
    }

    while (1)
    {
        printf("Categoria (Smartphones | Notebooks | Perifericos | Pecas e Componentes): ");
        StatusLeitura st = lerLinhaControlada(p.categoria, sizeof(p.categoria));
        if (st == LEITURA_EOF)
        {
            printf("\nCadastro cancelado (fim de entrada).\n");
            return 0;
        }
        if (st == LEITURA_LONGA)
        {
            printf("Categoria excede o limite de %d bytes. Use uma das opcoes acima.\n", TAM_CATEGORIA - 1);
            continue;
        }
        if (p.categoria[0] == '\0')
        {
            printf("Categoria nao pode ser vazia.\n");
            continue;
        }
        if (!categoriaValida(p.categoria))
        {
            printf("Categoria '%s' nao reconhecida. Use exatamente uma das opcoes acima.\n",
                   p.categoria);
            continue;
        }
        break;
    }

    if (!lerPrecoCentavosControlado("Preco (R$): ", &p.preco_centavos))
    {
        printf("Cadastro cancelado (fim de entrada).\n");
        return 0;
    }

    if (!lerInteiroControlado("Quantidade em estoque: ", 0, INT_MAX, &p.qtd_estoque))
    {
        printf("Cadastro cancelado (fim de entrada).\n");
        return 0;
    }

    p.id = proximoId++;
    produtos[totalProdutos++] = p;
    printf("Produto '%s' cadastrado com sucesso! ID: %d\n", p.nome, p.id);
    return 1;
}

static void listarProdutos(void)
{
    if (totalProdutos == 0)
    {
        printf("Nenhum produto cadastrado ainda.\n");
        return;
    }

    printf("\n%-5s %-30s %-22s %10s %10s\n",
           "ID", "Nome", "Categoria", "Preco", "Estoque");
    printf("%-5s %-30s %-22s %10s %10s\n",
           "---", "----------------------------", "----------------------",
           "----------", "----------");

    for (int i = 0; i < totalProdutos; i++)
    {
        char preco_fmt[32];
        formatarCentavos(produtos[i].preco_centavos, preco_fmt, sizeof(preco_fmt));
        printf("%-5d %-30s %-22s %10s %10d\n",
               produtos[i].id,
               produtos[i].nome,
               produtos[i].categoria,
               preco_fmt,
               produtos[i].qtd_estoque);
    }
}

/* Busca por substring no nome, case-insensitive. Retorna 1 ou 0 em EOF */
static int buscarProduto(void)
{
    char termo[TAM_NOME];
    char termo_minusculo[TAM_NOME];
    char nome_minusculo[TAM_NOME];

    printf("Digite o nome ou trecho para buscar: ");
    StatusLeitura st = lerLinhaControlada(termo, sizeof(termo));
    if (st == LEITURA_EOF)
    {
        printf("\nBusca cancelada (fim de entrada).\n");
        return 0;
    }
    if (st == LEITURA_LONGA)
    {
        printf("Termo excede o limite de %d bytes. Busca cancelada.\n", TAM_NOME - 1);
        return 1;
    }

    if (termo[0] == '\0')
    {
        printf("Digite pelo menos um caractere para buscar.\n");
        return 1;
    }

    snprintf(termo_minusculo, sizeof(termo_minusculo), "%s", termo);
    paraMinusculas(termo_minusculo);

    int encontrado = 0;
    for (int i = 0; i < totalProdutos; i++)
    {
        snprintf(nome_minusculo, sizeof(nome_minusculo), "%s", produtos[i].nome);
        paraMinusculas(nome_minusculo);

        if (strstr(nome_minusculo, termo_minusculo) != NULL)
        {
            char preco_fmt[32];
            formatarCentavos(produtos[i].preco_centavos, preco_fmt, sizeof(preco_fmt));
            printf("[%d] %s | Categoria: %s | Preco: R$ %s | Estoque: %d\n",
                   produtos[i].id,
                   produtos[i].nome,
                   produtos[i].categoria,
                   preco_fmt,
                   produtos[i].qtd_estoque);
            encontrado++;
        }
    }
    if (!encontrado)
    {
        printf("Nenhum resultado encontrado para '%s'.\n", termo);
    }
    return 1;
}

/* Remove produto pelo ID e compacta o vetor sem reutilizar proximoId. Retorna 1 ou 0 em EOF */
static int removerProduto(void)
{
    int id = 0;
    if (!lerInteiroControlado("ID do produto a remover: ", 1, INT_MAX, &id))
    {
        printf("Remocao cancelada (fim de entrada).\n");
        return 0;
    }

    for (int i = 0; i < totalProdutos; i++)
    {
        if (produtos[i].id == id)
        {
            printf("Removendo '%s'...\n", produtos[i].nome);
            for (int j = i; j < totalProdutos - 1; j++)
            {
                produtos[j] = produtos[j + 1];
            }
            totalProdutos--;
            printf("Produto removido com sucesso.\n");
            return 1;
        }
    }
    printf("Nenhum produto encontrado com ID %d.\n", id);
    return 1;
}

static const Produto *buscarPorIdLocal(int id)
{
    for (int i = 0; i < totalProdutos; i++)
    {
        if (produtos[i].id == id)
        {
            return &produtos[i];
        }
    }
    return NULL;
}

/* Gera resumo do estoque reutilizando calcularResumoEstoque */
static void relatorioEstoque(void)
{
    if (totalProdutos == 0)
    {
        printf("Estoque vazio — nada a relatar.\n");
        return;
    }

    ItemEstoque itens[MAX_PRODUTOS];
    ResumoEstoque resumo;
    char erro[256];
    long long soma_precos = 0;
    Produto mais_caro = produtos[0];
    Produto mais_barato = produtos[0];

    for (int i = 0; i < totalProdutos; i++)
    {
        itens[i].id = produtos[i].id;
        itens[i].preco_centavos = produtos[i].preco_centavos;
        itens[i].estoque = produtos[i].qtd_estoque;

        if (!somarLLSeguro(soma_precos, produtos[i].preco_centavos, &soma_precos))
        {
            printf("Erro: overflow ao somar precos no relatorio.\n");
            return;
        }
        if (produtos[i].preco_centavos > mais_caro.preco_centavos)
        {
            mais_caro = produtos[i];
        }
        if (produtos[i].preco_centavos < mais_barato.preco_centavos)
        {
            mais_barato = produtos[i];
        }
    }

    if (!calcularResumoEstoque(itens, totalProdutos, &resumo, erro, sizeof(erro)))
    {
        printf("Erro ao calcular relatorio: %s\n", erro);
        return;
    }

    char media_fmt[32];
    char valor_total_fmt[32];
    char caro_fmt[32];
    char barato_fmt[32];
    formatarCentavos(soma_precos / totalProdutos, media_fmt, sizeof(media_fmt));
    formatarCentavos(resumo.valor_estoque_centavos, valor_total_fmt, sizeof(valor_total_fmt));
    formatarCentavos(mais_caro.preco_centavos, caro_fmt, sizeof(caro_fmt));
    formatarCentavos(mais_barato.preco_centavos, barato_fmt, sizeof(barato_fmt));

    printf("\n===== RELATORIO DE ESTOQUE =====\n");
    printf("Total de produtos cadastrados: %d\n", resumo.total_produtos);
    printf("Total de unidades em estoque:  %lld\n", resumo.total_unidades);
    printf("Valor total em estoque:        R$ %s\n", valor_total_fmt);
    printf("Valor medio dos precos:        R$ %s\n", media_fmt);
    printf("Produto mais caro:             %s (R$ %s)\n", mais_caro.nome, caro_fmt);
    printf("Produto mais barato:           %s (R$ %s)\n", mais_barato.nome, barato_fmt);

    /* Menos de 3 unidades = alerta de reposicao (0 = esgotado e critico) */
    printf("\n--- Alertas de Reposicao (< %d unidades) ---\n", LIMITE_ESTOQUE_CRITICO);
    for (int i = 0; i < resumo.total_criticos; i++)
    {
        const Produto *p = buscarPorIdLocal((int)resumo.ids_estoque_critico[i]);
        if (p != NULL)
        {
            if (p->qtd_estoque == 0)
            {
                printf("  [ESGOTADO] %s: 0 unidade(s)\n", p->nome);
            }
            else
            {
                printf("  [URGENTE] %s: apenas %d unidade(s)\n",
                       p->nome, p->qtd_estoque);
            }
        }
    }
    if (resumo.total_criticos == 0)
    {
        printf("Nenhum produto em situacao critica.\n");
    }

    printf("================================\n");
}

/* Filtra produtos pela categoria exata (case-insensitive). Retorna 1 ou 0 em EOF */
static int listarPorCategoria(void)
{
    char categoria_busca[TAM_CATEGORIA];
    char cat_minuscula[TAM_CATEGORIA];
    char prod_cat_minuscula[TAM_CATEGORIA];

    printf("Digite a categoria (Smartphones | Notebooks | Perifericos | Pecas e Componentes): ");
    StatusLeitura st = lerLinhaControlada(categoria_busca, sizeof(categoria_busca));
    if (st == LEITURA_EOF)
    {
        printf("\nFiltro cancelado (fim de entrada).\n");
        return 0;
    }
    if (st == LEITURA_LONGA)
    {
        printf("Categoria excede o limite de %d bytes. Filtro cancelado.\n", TAM_CATEGORIA - 1);
        return 1;
    }

    snprintf(cat_minuscula, sizeof(cat_minuscula), "%s", categoria_busca);
    paraMinusculas(cat_minuscula);

    int encontrado = 0;
    printf("\n--- Produtos em '%s' ---\n", categoria_busca);
    for (int i = 0; i < totalProdutos; i++)
    {
        snprintf(prod_cat_minuscula, sizeof(prod_cat_minuscula), "%s", produtos[i].categoria);
        paraMinusculas(prod_cat_minuscula);

        if (strcmp(prod_cat_minuscula, cat_minuscula) == 0)
        {
            char preco_fmt[32];
            formatarCentavos(produtos[i].preco_centavos, preco_fmt, sizeof(preco_fmt));
            printf("[%d] %s | R$ %s | Estoque: %d\n",
                   produtos[i].id,
                   produtos[i].nome,
                   preco_fmt,
                   produtos[i].qtd_estoque);
            encontrado++;
        }
    }

    if (!encontrado)
    {
        printf("Nenhum produto encontrado nesta categoria.\n");
    }
    return 1;
}

static void executarMenuInterativo(void)
{
    int opcao = -1;
    do
    {
        exibirMenu();
        if (!lerInteiroControlado("Escolha uma opcao: ", INT_MIN, INT_MAX, &opcao))
        {
            printf("Encerrando o sistema PixelShop (fim de entrada).\n");
            break;
        }

        switch (opcao)
        {
        case 1:
            if (!cadastrarProduto())
            {
                opcao = 0;
            }
            break;
        case 2:
            listarProdutos();
            break;
        case 3:
            if (!buscarProduto())
            {
                opcao = 0;
            }
            break;
        case 4:
            if (!removerProduto())
            {
                opcao = 0;
            }
            break;
        case 5:
            relatorioEstoque();
            break;
        case 6:
            if (!listarPorCategoria())
            {
                opcao = 0;
            }
            break;
        case 0:
            printf("Encerrando o sistema PixelShop. Ate logo!\n");
            break;
        default:
            printf("Opcao invalida! Escolha entre 0 e 6.\n");
        }
    } while (opcao != 0);
}

int main(int argc, char *argv[])
{
    if (argc == 1)
    {
        executarMenuInterativo();
        return EXIT_SUCESSO;
    }

    if (argc == 2 && strcmp(argv[1], "--relatorio") == 0)
    {
        return executarModoRelatorio();
    }

    fprintf(
        stderr,
        "Argumento invalido. Uso: %s [--relatorio]\n",
        (argc > 0 && argv[0] != NULL) ? argv[0] : "programa.exe");
    return EXIT_ARG_INVALIDO;
}
