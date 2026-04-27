/*
 * Projeto de Extensao - Desenvolvimento de Software
 * PixelShop - Sistema de Estoque (terminal)
 * UNINOVE - Noturno 2026
 * Prof.a Priscila Viana Cunha
 *
 * Squad C: Lucas Byoung Ki Han
 *
 * OBS: vetor estatico de 100 produtos, suficiente pra entrega.
 * TODO: lista encadeada no semestre que vem talvez
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_PRODUTOS 100
#define TAM_NOME 50
#define TAM_CATEGORIA 30

/* int porque getchar() retorna int — char dava loop infinito no buffer */
typedef int CharBuf;

/* categorias do banco Oracle — precisa bater com insert_data.sql */
#define NUM_CATEGORIAS 4
static const char *CATEGORIAS_VALIDAS[NUM_CATEGORIAS] = {
    "Smartphones",
    "Notebooks",
    "Perifericos",
    "Pecas e Componentes"};

/* le inteiro com validacao — evita loop infinito quando usuario digita letra no scanf */
int lerInteiro(const char *mensagem)
{
    int valor;
    int resultado;
    CharBuf c;
    do
    {
        printf("%s", mensagem);
        resultado = scanf("%d", &valor);
        if (resultado != 1)
        {
            printf("Entrada invalida! Digite apenas numeros inteiros.\n");
            while ((c = getchar()) != '\n' && c != EOF)
                ;
        }
    } while (resultado != 1);
    while ((c = getchar()) != '\n' && c != EOF)
        ;
    return valor;
}

/* le float com validacao — rejeita texto e preco negativo */
float lerFloat(const char *mensagem)
{
    float valor;
    int resultado;
    CharBuf c;
    do
    {
        printf("%s", mensagem);
        resultado = scanf("%f", &valor);
        if (resultado != 1)
        {
            printf("Entrada invalida! Use ponto para separar decimais (ex: 29.90).\n");
            while ((c = getchar()) != '\n' && c != EOF)
                ;
        }
        else if (valor < 0)
        {
            printf("Preco nao pode ser negativo. Tente novamente.\n");
            resultado = 0;
        }
    } while (resultado != 1);
    while ((c = getchar()) != '\n' && c != EOF)
        ;
    return valor;
}

typedef struct
{
    int id;
    char nome[TAM_NOME];
    char categoria[TAM_CATEGORIA];
    float preco;
    int qtd_estoque;
} Produto;

Produto produtos[MAX_PRODUTOS];
int totalProdutos = 0;

/* prototipos */
int lerInteiro(const char *mensagem);
float lerFloat(const char *mensagem);
void exibirMenu();
void cadastrarProduto();
void listarProdutos();
void buscarProduto();
void removerProduto();
void relatorioEstoque();
void listarPorCategoria();

/* converte string pra minusculo — busca case-insensitive */
void paraMinusculas(char *str)
{
    for (int i = 0; str[i]; i++)
    {
        str[i] = tolower((unsigned char)str[i]);
    }
}

/* verifica se a categoria digitada bate com as do banco Oracle (case-insensitive) */
int categoriaValida(const char *categoria_digitada)
{
    char digitada_min[TAM_CATEGORIA];
    char valida_min[TAM_CATEGORIA];

    strncpy(digitada_min, categoria_digitada, TAM_CATEGORIA - 1);
    digitada_min[TAM_CATEGORIA - 1] = '\0';
    paraMinusculas(digitada_min);

    for (int i = 0; i < NUM_CATEGORIAS; i++)
    {
        strncpy(valida_min, CATEGORIAS_VALIDAS[i], TAM_CATEGORIA - 1);
        valida_min[TAM_CATEGORIA - 1] = '\0';
        paraMinusculas(valida_min);
        if (strcmp(digitada_min, valida_min) == 0)
            return 1;
    }
    return 0;
}

int main()
{
    int opcao;
    do
    {
        exibirMenu();
        opcao = lerInteiro("Escolha uma opcao: ");

        switch (opcao)
        {
        case 1:
            cadastrarProduto();
            break;
        case 2:
            listarProdutos();
            break;
        case 3:
            buscarProduto();
            break;
        case 4:
            removerProduto();
            break;
        case 5:
            relatorioEstoque();
            break;
        case 6:
            listarPorCategoria();
            break;
        case 0:
            printf("Encerrando o sistema PixelShop. Ate logo!\n");
            break;
        default:
            printf("Opcao invalida! Escolha entre 0 e 6.\n");
        }
    } while (opcao != 0);

    return 0;
}

void exibirMenu()
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

/* cadastra novo produto validando categoria contra o banco Oracle */
void cadastrarProduto()
{
    if (totalProdutos >= MAX_PRODUTOS)
    {
        printf("Limite de %d produtos atingido! Contate o suporte.\n", MAX_PRODUTOS);
        return;
    }

    Produto p;
    p.id = totalProdutos + 1;

    printf("Nome do produto: ");
    fgets(p.nome, TAM_NOME, stdin);
    p.nome[strcspn(p.nome, "\n")] = '\0';
    if (strlen(p.nome) == 0)
    {
        printf("Nome nao pode ser vazio. Cadastro cancelado.\n");
        return;
    }

    int cat_ok = 0;
    do
    {
        printf("Categoria (Smartphones | Notebooks | Perifericos | Pecas e Componentes): ");
        fgets(p.categoria, TAM_CATEGORIA, stdin);
        p.categoria[strcspn(p.categoria, "\n")] = '\0';
        if (strlen(p.categoria) == 0)
        {
            printf("Categoria nao pode ser vazia.\n");
            continue;
        }
        cat_ok = categoriaValida(p.categoria);
        if (!cat_ok)
            printf("Categoria '%s' nao reconhecida. Use exatamente uma das opcoes acima.\n",
                   p.categoria);
    } while (!cat_ok);

    p.preco = lerFloat("Preco (R$): ");

    /*Evita estoque negativo!!*/
    do
    {
        p.qtd_estoque = lerInteiro("Quantidade em estoque: ");
        if (p.qtd_estoque < 0)
        {
            printf("Quantidade nao pode ser negativa. Tente novamente.\n");
        }
    } while (p.qtd_estoque < 0);

    produtos[totalProdutos++] = p;
    printf("Produto '%s' cadastrado com sucesso! ID: %d\n", p.nome, p.id);
}

/* lista todos os produtos em tabela alinhada */
void listarProdutos()
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
        printf("%-5d %-30s %-22s %10.2f %10d\n",
               produtos[i].id,
               produtos[i].nome,
               produtos[i].categoria,
               produtos[i].preco,
               produtos[i].qtd_estoque);
    }
}

/* busca por substring no nome, case-insensitive */
void buscarProduto()
{
    char termo[TAM_NOME];
    char termo_minusculo[TAM_NOME];
    char nome_minusculo[TAM_NOME];

    printf("Digite o nome ou trecho para buscar: ");
    fgets(termo, TAM_NOME, stdin);
    termo[strcspn(termo, "\n")] = '\0';

    strcpy(termo_minusculo, termo);
    paraMinusculas(termo_minusculo);

    int encontrado = 0;
    for (int i = 0; i < totalProdutos; i++)
    {
        strcpy(nome_minusculo, produtos[i].nome);
        paraMinusculas(nome_minusculo);

        if (strstr(nome_minusculo, termo_minusculo) != NULL)
        {
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

/* remove produto pelo ID e compacta o vetor pra nao deixar buraco */
void removerProduto()
{
    int id = lerInteiro("ID do produto a remover: ");

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
            return;
        }
    }
    printf("Nenhum produto encontrado com ID %d.\n", id);
}

/* gera resumo do estoque: total, preco medio, mais caro, mais barato e alertas de reposicao */
void relatorioEstoque()
{
    if (totalProdutos == 0)
    {
        printf("Estoque vazio — nada a relatar.\n");
        return;
    }

    float soma_precos = 0;
    Produto mais_caro = produtos[0];
    Produto mais_barato = produtos[0];

    for (int i = 0; i < totalProdutos; i++)
    {
        soma_precos += produtos[i].preco;

        if (produtos[i].preco > mais_caro.preco)
            mais_caro = produtos[i];

        if (produtos[i].preco < mais_barato.preco)
            mais_barato = produtos[i];
    }

    printf("\n===== RELATORIO DE ESTOQUE =====\n");
    printf("Total de produtos cadastrados: %d\n", totalProdutos);
    printf("Valor medio dos precos:        R$ %.2f\n", soma_precos / totalProdutos);
    printf("Produto mais caro:             %s (R$ %.2f)\n", mais_caro.nome, mais_caro.preco);
    printf("Produto mais barato:           %s (R$ %.2f)\n", mais_barato.nome, mais_barato.preco);

    /* menos de 3 unidades = alerta de reposicao */
    printf("\n--- Alertas de Reposicao (< 3 unidades) ---\n");
    int qtd_alertas = 0;
    for (int i = 0; i < totalProdutos; i++)
    {
        if (produtos[i].qtd_estoque < 3)
        {
            printf("  [URGENTE] %s: apenas %d unidade(s)\n",
                   produtos[i].nome, produtos[i].qtd_estoque);
            qtd_alertas++;
        }
    }
    if (qtd_alertas == 0)
        printf("Nenhum produto em situacao critica.\n");

    printf("================================\n");
}

/* filtra produtos pela categoria exata (case-insensitive) */
void listarPorCategoria()
{
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
    for (int i = 0; i < totalProdutos; i++)
    {
        strcpy(prod_cat_minuscula, produtos[i].categoria);
        paraMinusculas(prod_cat_minuscula);

        if (strcmp(prod_cat_minuscula, cat_minuscula) == 0)
        {
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
