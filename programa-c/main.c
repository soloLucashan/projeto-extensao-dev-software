/*
 * ============================================================
 * PROJETO DE EXTENSAO - Desenvolvimento de Software
 * Empresa Parceira: PixelShop
 * Instituicao: UNINOVE - Turma Noturno 2026
 * Professora: Priscila Viana Cunha
 * ============================================================
 * Responsaveis (Squad C):
 *   - Lucas Byoung Ki Han   (Menu, estrutura geral, validacoes de entrada)
 *   - Guilherme Huilame     (Logica de negocio, busca, relatorio de estoque)
 * ============================================================
 * OBSERVACAO: o programa usa um vetor estatico de MAX_PRODUTOS
 * entradas. Funciona bem pra um estoque pequeno de loja fisica,
 * mas tem limitacao de tamanho em tempo de compilacao.
 * ============================================================
 *
 * TODO (Lucas): no proximo semestre, trocar esse vetor por uma lista
 *       encadeada pra nao ter o limite fixo de 100 produtos e conseguir
 *       escalar junto com o crescimento da PixelShop.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_PRODUTOS 100
#define TAM_NOME     50
#define TAM_CATEGORIA 30

/* Usamos int em vez de char porque getchar() retorna int.
 * Se usassemos char, em sistemas onde char e unsigned,
 * a comparacao com EOF (-1) nunca seria verdadeira
 * e o loop de limpeza do buffer nunca terminaria.
 * Bug sutil, mas real — o Lucas queimou a cabeca nisso. */
typedef int CharBuf;

/*
 * lerInteiro: le um inteiro do teclado com validacao robusta.
 *
 * O problema classico do scanf e que, quando o usuario digita
 * letras, o cursor do buffer nao avanca — ai o programa fica
 * em loop eterno. A funcao drena tudo que sobrou no buffer
 * antes de tentar de novo, evitando esse travamento.
 *
 * Implementado pelo Lucas com base em discussao da aula de LP.
 */
int lerInteiro(const char *mensagem) {
    int valor;
    int resultado;
    CharBuf c;
    do {
        printf("%s", mensagem);
        resultado = scanf("%d", &valor);
        if (resultado != 1) {
            printf("Entrada invalida! Digite apenas numeros inteiros.\n");
            /* Drena tudo que ficou no buffer ate o newline
             * pra nao reutilizar o lixo na proxima iteracao */
            while ((c = getchar()) != '\n' && c != EOF);
        }
    } while (resultado != 1);
    /* Consome o '\n' residual que o scanf deixa depois de ler o numero */
    while ((c = getchar()) != '\n' && c != EOF);
    return valor;
}

/*
 * lerFloat: le um decimal do teclado com validacao de tipo e sinal.
 *
 * Alem de evitar o loop infinito do scanf (mesma logica do lerInteiro),
 * essa funcao tambem rejeita precos negativos — regra de negocio basica
 * pra nao baguncar o relatorio financeiro da PixelShop.
 *
 * Implementado pelo Lucas; revisao de edge cases pelo Guilherme.
 */
float lerFloat(const char *mensagem) {
    float valor;
    int resultado;
    CharBuf c;
    do {
        printf("%s", mensagem);
        resultado = scanf("%f", &valor);
        if (resultado != 1) {
            printf("Entrada invalida! Use ponto para separar decimais (ex: 29.90).\n");
            while ((c = getchar()) != '\n' && c != EOF);
        } else if (valor < 0) {
            /* Preco negativo nao faz sentido no contexto de venda.
             * Forcamos nova tentativa em vez de aceitar silenciosamente. */
            printf("Preco nao pode ser negativo. Tente novamente.\n");
            resultado = 0;
        }
    } while (resultado != 1);
    while ((c = getchar()) != '\n' && c != EOF);
    return valor;
}

typedef struct {
    int   id;
    char  nome[TAM_NOME];
    char  categoria[TAM_CATEGORIA];
    float preco;
    int   qtd_estoque;   /* renomeado de quantidade_estoque para qtd_estoque:
                          * mais conciso e padrao que o pessoal usa no projeto */
} Produto;

/* Categorias validas da PixelShop — devem ser identicas aos valores
 * inseridos na tabela CATEGORIA do Oracle (insert_data.sql, linhas 14-21).
 * Se o banco ganhar uma categoria nova, atualiza NUM_CATEGORIAS e o array. */
#define NUM_CATEGORIAS 4
static const char *CATEGORIAS_VALIDAS[NUM_CATEGORIAS] = {
    "Smartphones",
    "Notebooks",
    "Perifericos",
    "Pecas e Componentes"
};

Produto produtos[MAX_PRODUTOS];
int totalProdutos = 0;

/* Prototipos — declarados aqui pra o compilador conhecer as assinaturas
 * antes do main, mesmo que as definicoes venham depois */
int   lerInteiro(const char *mensagem);
float lerFloat(const char *mensagem);
void  exibirMenu();
void  cadastrarProduto();
void  listarProdutos();
void  buscarProduto();
void  removerProduto();
void  relatorioEstoque();
void  listarPorCategoria();

/*
 * paraMinusculas: converte string in-place para caixa baixa.
 * Precisamos disso pra busca case-insensitive funcionar direito —
 * usuario pode digitar "MOUSE" ou "mouse" e o resultado e o mesmo.
 * O cast para unsigned char e obrigatorio pra evitar UB com tolower
 * em caracteres com acento (ex: 'é', 'ã').
 */
void paraMinusculas(char *str) {
    for (int i = 0; str[i]; i++) {
        str[i] = tolower((unsigned char)str[i]);
    }
}

/*
 * categoriaValida: checa se a string digitada corresponde a uma das
 * 4 categorias cadastradas no Oracle. Comparacao case-insensitive pra
 * aceitar "perifericos" e "Perifericos" como equivalentes.
 *
 * Retorna 1 se valida, 0 se desconhecida.
 * Funcao adicionada pelo Guilherme (correcao do FIXME em cadastrarProduto).
 */
int categoriaValida(const char *categoria_digitada) {
    char digitada_min[TAM_CATEGORIA];
    char valida_min[TAM_CATEGORIA];

    strncpy(digitada_min, categoria_digitada, TAM_CATEGORIA - 1);
    digitada_min[TAM_CATEGORIA - 1] = '\0';
    paraMinusculas(digitada_min);

    for (int i = 0; i < NUM_CATEGORIAS; i++) {
        strncpy(valida_min, CATEGORIAS_VALIDAS[i], TAM_CATEGORIA - 1);
        valida_min[TAM_CATEGORIA - 1] = '\0';
        paraMinusculas(valida_min);
        if (strcmp(digitada_min, valida_min) == 0)
            return 1;
    }
    return 0;
}

int main() {
    int opcao;
    do {
        exibirMenu();
        /* lerInteiro ja resolve o problema de entrada invalida —
         * sem ele, digitar uma letra aqui travaria o programa inteiro */
        opcao = lerInteiro("Escolha uma opcao: ");

        switch (opcao) {
            case 1: cadastrarProduto();   break;
            case 2: listarProdutos();     break;
            case 3: buscarProduto();      break;
            case 4: removerProduto();     break;
            case 5: relatorioEstoque();   break;
            case 6: listarPorCategoria(); break;
            case 0: printf("Encerrando o sistema PixelShop. Ate logo!\n"); break;
            default: printf("Opcao invalida! Escolha entre 0 e 6.\n");
        }
    } while (opcao != 0);

    return 0;
}

/* Menu principal — mantido simples e direto pra funcionar mesmo em
 * terminais basicos sem suporte a cor ou ANSI escape codes */
void exibirMenu() {
    printf("\n===== PIXELSHOP - Sistema de Estoque =====");
    printf("\n 1. Cadastrar produto");
    printf("\n 2. Listar todos os produtos");
    printf("\n 3. Buscar produto por nome");
    printf("\n 4. Remover produto");
    printf("\n 5. Relatorio de estoque (total, valor medio, alertas)");
    printf("\n 6. Listar por categoria");
    printf("\n 0. Sair");
    printf("\n==========================================\n");
}

/*
 * cadastrarProduto: coleta dados do novo produto via terminal.
 *
 * As categorias validas precisam bater com as do banco Oracle:
 *   Smartphones | Notebooks | Perifericos | Pecas e Componentes
 * O sistema nao valida o nome da categoria automaticamente por enquanto
 * (seria bom adicionar isso futuramente — ver TODO abaixo).
 *
 * FIXME (Guilherme): adicionar validacao das categorias contra uma lista
 *       fixa pra evitar que alguem cadastre "Periferico" (sem 's') e
 *       quebre a coerencia com o banco Oracle.
 */
void cadastrarProduto() {
    if (totalProdutos >= MAX_PRODUTOS) {
        printf("Limite de %d produtos atingido! Contate o suporte.\n", MAX_PRODUTOS);
        return;
    }

    Produto p;
    p.id = totalProdutos + 1;

    printf("Nome do produto: ");
    fgets(p.nome, TAM_NOME, stdin);
    p.nome[strcspn(p.nome, "\n")] = '\0';
    if (strlen(p.nome) == 0) {
        printf("Nome nao pode ser vazio. Cadastro cancelado.\n");
        return;
    }

    /* Listamos as categorias validas na dica pra o operador nao digitar errado
     * e criar inconsistencia com o banco de dados Oracle da PixelShop.
     * O loop abaixo garante que so uma categoria canonica seja aceita. */
    int cat_ok = 0;
    do {
        printf("Categoria (Smartphones | Notebooks | Perifericos | Pecas e Componentes): ");
        fgets(p.categoria, TAM_CATEGORIA, stdin);
        p.categoria[strcspn(p.categoria, "\n")] = '\0';
        if (strlen(p.categoria) == 0) {
            printf("Categoria nao pode ser vazia.\n");
            continue;
        }
        cat_ok = categoriaValida(p.categoria);
        if (!cat_ok)
            printf("Categoria '%s' invalida. Use exatamente uma das opcoes acima.\n",
                   p.categoria);
    } while (!cat_ok);

    p.preco        = lerFloat("Preco (R$): ");
    p.qtd_estoque  = lerInteiro("Quantidade em estoque: ");

    produtos[totalProdutos++] = p;
    printf("Produto '%s' cadastrado com sucesso! ID: %d\n", p.nome, p.id);
}

/* Lista todos os produtos em formato de tabela alinhada.
 * O %-30s garante que nomes longos nao deformam a tabela. */
void listarProdutos() {
    if (totalProdutos == 0) {
        printf("Nenhum produto cadastrado ainda.\n");
        return;
    }

    printf("\n%-5s %-30s %-22s %10s %10s\n",
           "ID", "Nome", "Categoria", "Preco", "Estoque");
    printf("%-5s %-30s %-22s %10s %10s\n",
           "---", "----------------------------", "----------------------",
           "----------", "----------");

    for (int i = 0; i < totalProdutos; i++) {
        printf("%-5d %-30s %-22s %10.2f %10d\n",
            produtos[i].id,
            produtos[i].nome,
            produtos[i].categoria,
            produtos[i].preco,
            produtos[i].qtd_estoque);
    }
}

/*
 * buscarProduto: localiza produtos pelo nome usando substring case-insensitive.
 *
 * Usamos strstr depois de converter tudo pra minusculo, assim
 * "mouse" acha "Mouse Logitech MX Master" sem o usuario precisar
 * saber a capitalizacao exata — bem mais util no dia a dia da loja.
 *
 * Logica de busca case-insensitive implementada pelo Guilherme.
 */
void buscarProduto() {
    char termo[TAM_NOME];
    char termo_minusculo[TAM_NOME];
    char nome_minusculo[TAM_NOME];

    printf("Digite o nome ou trecho para buscar: ");
    fgets(termo, TAM_NOME, stdin);
    termo[strcspn(termo, "\n")] = '\0';

    strcpy(termo_minusculo, termo);
    paraMinusculas(termo_minusculo);

    int encontrado = 0;
    for (int i = 0; i < totalProdutos; i++) {
        strcpy(nome_minusculo, produtos[i].nome);
        paraMinusculas(nome_minusculo);

        if (strstr(nome_minusculo, termo_minusculo) != NULL) {
            printf("[%d] %s | Categoria: %s | Preco: R$ %.2f | Estoque: %d\n",
                produtos[i].id,
                produtos[i].nome,
                produtos[i].categoria,
                produtos[i].preco,
                produtos[i].qtd_estoque);
            encontrado++;
        }
    }
    if (!encontrado)
        printf("Nenhum resultado encontrado para '%s'.\n", termo);
}

/*
 * removerProduto: exclui um produto pelo ID e compacta o vetor.
 *
 * Apos remover, deslocamos todos os itens seguintes uma posicao
 * pra baixo pra nao deixar buraco no meio do vetor — se deixasse,
 * o listarProdutos mostraria uma posicao vazia no meio da lista.
 */
void removerProduto() {
    /* lerInteiro ja protege contra o usuario digitar texto aqui */
    int id = lerInteiro("ID do produto a remover: ");

    for (int i = 0; i < totalProdutos; i++) {
        if (produtos[i].id == id) {
            printf("Removendo '%s'...\n", produtos[i].nome);
            /* Desloca os produtos seguintes pra preencher o espaco */
            for (int j = i; j < totalProdutos - 1; j++) {
                produtos[j] = produtos[j + 1];
            }
            totalProdutos--;
            printf("Produto removido com sucesso.\n");
            return;
        }
    }
    printf("Nenhum produto encontrado com ID %d.\n", id);
}

/*
 * relatorioEstoque: gera um resumo gerencial do estoque atual.
 *
 * O alerta de estoque baixo usa o limite de 3 unidades porque,
 * na pratica da PixelShop, o prazo de reposicao dos fornecedores
 * e de 2 a 5 dias uteis. Com 3 unidades em mao, da pra vender
 * durante esse periodo sem zerar antes da entrega chegar.
 *
 * Logica do relatorio consolidada pelo Guilherme. Revisao de
 * edge cases (totalProdutos == 0, todos com preco igual) pelo Lucas.
 */
void relatorioEstoque() {
    if (totalProdutos == 0) {
        printf("Estoque vazio — nada a relatar.\n");
        return;
    }

    float soma_precos  = 0;
    Produto mais_caro  = produtos[0];
    Produto mais_barato = produtos[0];

    for (int i = 0; i < totalProdutos; i++) {
        soma_precos += produtos[i].preco;

        if (produtos[i].preco > mais_caro.preco)
            mais_caro = produtos[i];

        if (produtos[i].preco < mais_barato.preco)
            mais_barato = produtos[i];
    }

    printf("\n===== RELATORIO DE ESTOQUE =====\n");
    printf("Total de produtos cadastrados: %d\n",         totalProdutos);
    printf("Valor medio dos precos:        R$ %.2f\n",    soma_precos / totalProdutos);
    printf("Produto mais caro:             %s (R$ %.2f)\n", mais_caro.nome,   mais_caro.preco);
    printf("Produto mais barato:           %s (R$ %.2f)\n", mais_barato.nome, mais_barato.preco);

    /* Regra de negocio da PixelShop: produtos com menos de 3 unidades
     * entram em alerta critico — a equipe de compras precisa ser
     * avisada com antecedencia pra dar tempo de repor antes de zerar */
    printf("\n--- Alertas Criticos de Reposicao (< 3 unidades) ---\n");
    int qtd_alertas = 0;
    for (int i = 0; i < totalProdutos; i++) {
        if (produtos[i].qtd_estoque < 3) {
            printf("  [URGENTE] %s: apenas %d unidade(s) — contatar fornecedor!\n",
                   produtos[i].nome, produtos[i].qtd_estoque);
            qtd_alertas++;
        }
    }
    if (qtd_alertas == 0)
        printf("Nenhum produto em situacao critica. Estoque saudavel!\n");

    printf("================================\n");
}

/*
 * listarPorCategoria: filtra produtos pela categoria informada (case-insensitive).
 *
 * Usamos strcmp (nao strstr) aqui porque a categoria e um campo exato,
 * diferente do nome — nao queremos que "Peri" retorne "Perifericos".
 * O usuario precisa digitar a categoria completa pra manter consistencia
 * com as 4 categorias do banco Oracle.
 */
void listarPorCategoria() {
    char categoria_busca[TAM_CATEGORIA];
    char cat_minuscula[TAM_CATEGORIA];
    char prod_cat_minuscula[TAM_CATEGORIA];

    printf("Digite a categoria (Smartphones | Notebooks | Perifericos | Pecas e Componentes): ");
    fgets(categoria_busca, TAM_CATEGORIA, stdin);
    categoria_busca[strcspn(categoria_busca, "\n")] = '\0';

    strcpy(cat_minuscula, categoria_busca);
    paraMinusculas(cat_minuscula);

    int encontrado = 0;
    printf("\n--- Produtos em '%s' ---\n", categoria_busca);
    for (int i = 0; i < totalProdutos; i++) {
        strcpy(prod_cat_minuscula, produtos[i].categoria);
        paraMinusculas(prod_cat_minuscula);

        if (strcmp(prod_cat_minuscula, cat_minuscula) == 0) {
            printf("[%d] %s | R$ %.2f | Estoque: %d\n",
                produtos[i].id,
                produtos[i].nome,
                produtos[i].preco,
                produtos[i].qtd_estoque);
            encontrado++;
        }
    }

    if (!encontrado)
        printf("Nenhum produto encontrado nesta categoria.\n");
}
