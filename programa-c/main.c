#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_PRODUTOS 100
#define TAM_NOME 50
#define TAM_CATEGORIA 30

/*
 * --------------------------------------------------------
 * PROJETO DE EXTENSAO - Desenvolvimento de Software
 * Empresa: PixelShop
 * Instituicao: UNINOVE - Turma Noturno 2026
 * Professora: Priscila Viana Cunha
 * --------------------------------------------------------
 * Responsaveis (Squad C):
 *   - Lucas Byoung Ki Han   (Menu, estrutura, validacoes)
 *   - Guilherme Huilame     (Logica de negocio, cadastros e refinamento)
 * --------------------------------------------------------
 */

typedef struct {
    int id;
    char nome[TAM_NOME];
    char categoria[TAM_CATEGORIA];
    float preco;
    int quantidade_estoque;
} Produto;

Produto produtos[MAX_PRODUTOS];
int totalProdutos = 0;

// Prototipos das funcoes
void exibirMenu();
void cadastrarProduto();
void listarProdutos();
void buscarProduto();
void removerProduto();
void relatorioEstoque();
void listarPorCategoria();

// Funcao auxiliar para converter string para minusculas
void paraMinusculas(char *str) {
    for (int i = 0; str[i]; i++) {
        str[i] = tolower((unsigned char)str[i]);
    }
}

int main() {
    int opcao;
    do {
        exibirMenu();
        printf("Escolha uma opcao: ");
        scanf("%d", &opcao);
        getchar(); // Limpar o buffer
        
        switch (opcao) {
            case 1: cadastrarProduto();   break;
            case 2: listarProdutos();     break;
            case 3: buscarProduto();      break;
            case 4: removerProduto();     break;
            case 5: relatorioEstoque();   break;
            case 6: listarPorCategoria(); break;
            case 0: printf("Encerrando o sistema PixelShop...\n"); break;
            default: printf("Opcao invalida! Tente novamente.\n");
        }
    } while (opcao != 0);
    
    return 0;
}

// Exibe o menu principal do sistema
void exibirMenu() {
    printf("\n===== PIXELSHOP - Sistema de Estoque =====");
    printf("\n 1. Cadastrar produto");
    printf("\n 2. Listar produtos");
    printf("\n 3. Buscar produto por nome");
    printf("\n 4. Remover produto");
    printf("\n 5. Relatorio de estoque (total, valor medio, estoque baixo)");
    printf("\n 6. Listar por categoria");
    printf("\n 0. Sair");
    printf("\n==========================================\n");
}

// Cadastra um novo produto no estoque
void cadastrarProduto() {
    if (totalProdutos >= MAX_PRODUTOS) {
        printf("Limite de produtos atingido!\n");
        return;
    }
    
    Produto p;
    p.id = totalProdutos + 1;
    
    printf("Nome do produto: ");
    fgets(p.nome, TAM_NOME, stdin);
    p.nome[strcspn(p.nome, "\n")] = '\0';
    
    printf("Categoria (ex: Smartphone, Notebook, Periferico, Peca): ");
    fgets(p.categoria, TAM_CATEGORIA, stdin);
    p.categoria[strcspn(p.categoria, "\n")] = '\0';
    
    printf("Preco (R$): ");
    scanf("%f", &p.preco);
    
    printf("Quantidade em estoque: ");
    scanf("%d", &p.quantidade_estoque);
    getchar(); // Limpar o buffer
    
    produtos[totalProdutos++] = p;
    printf("Produto cadastrado com sucesso! ID: %d\n", p.id);
}

// Lista todos os produtos cadastrados
void listarProdutos() {
    if (totalProdutos == 0) {
        printf("Nenhum produto encontrado.\n");
        return;
    }
    
    printf("\n%-5s %-30s %-20s %10s %10s\n", "ID", "Nome", "Categoria", "Preco", "Estoque");
    for (int i = 0; i < totalProdutos; i++) {
        printf("%-5d %-30s %-20s %10.2f %10d\n",
            produtos[i].id, 
            produtos[i].nome,
            produtos[i].categoria, 
            produtos[i].preco, 
            produtos[i].quantidade_estoque);
    }
}

// Busca um produto especifico pelo nome (case-insensitive)
void buscarProduto() {
    char termo[TAM_NOME];
    char termoMinusculo[TAM_NOME];
    char nomeProduto[TAM_NOME];
    
    printf("Digite o nome para buscar: ");
    fgets(termo, TAM_NOME, stdin);
    termo[strcspn(termo, "\n")] = '\0';
    
    strcpy(termoMinusculo, termo);
    paraMinusculas(termoMinusculo);
    
    int encontrado = 0;
    for (int i = 0; i < totalProdutos; i++) {
        strcpy(nomeProduto, produtos[i].nome);
        paraMinusculas(nomeProduto);
        
        if (strstr(nomeProduto, termoMinusculo) != NULL) {
            printf("[%d] %s | Categoria: %s | Preco: R$ %.2f | Estoque: %d\n",
                produtos[i].id, 
                produtos[i].nome,
                produtos[i].categoria, 
                produtos[i].preco,
                produtos[i].quantidade_estoque);
            encontrado++;
        }
    }
    if (!encontrado) printf("Nenhum resultado para '%s'.\n", termo);
}

// Remove um produto do sistema pelo ID
void removerProduto() {
    int id;
    printf("ID do produto a remover: ");
    scanf("%d", &id);
    getchar(); // Limpar o buffer
    
    for (int i = 0; i < totalProdutos; i++) {
        if (produtos[i].id == id) {
            for (int j = i; j < totalProdutos - 1; j++) {
                produtos[j] = produtos[j + 1];
            }
            totalProdutos--;
            printf("Produto removido.\n");
            return;
        }
    }
    printf("ID nao encontrado.\n");
}

// Gera um relatorio completo do estoque
void relatorioEstoque() {
    if (totalProdutos == 0) {
        printf("Nao ha produtos no estoque para gerar relatorio.\n");
        return;
    }

    float somaValores = 0;
    Produto maisCaro = produtos[0];
    Produto maisBarato = produtos[0];

    for (int i = 0; i < totalProdutos; i++) {
        somaValores += produtos[i].preco;
        
        if (produtos[i].preco > maisCaro.preco) {
            maisCaro = produtos[i];
        }
        if (produtos[i].preco < maisBarato.preco) {
            maisBarato = produtos[i];
        }
    }

    printf("\n===== RELATORIO DE ESTOQUE =====\n");
    printf("Total de produtos cadastrados: %d\n", totalProdutos);
    printf("Valor medio dos precos:        R$ %.2f\n", somaValores / totalProdutos);
    printf("Produto mais caro:             %s (R$ %.2f)\n", maisCaro.nome, maisCaro.preco);
    printf("Produto mais barato:           %s (R$ %.2f)\n", maisBarato.nome, maisBarato.preco);
    
    printf("\n--- Produtos com Estoque Baixo (<= 3) ---\n");
    int estoqueBaixo = 0;
    for (int i = 0; i < totalProdutos; i++) {
        if (produtos[i].quantidade_estoque <= 3) {
            printf("- %s: %d unidade(s)\n", produtos[i].nome, produtos[i].quantidade_estoque);
            estoqueBaixo++;
        }
    }
    if (estoqueBaixo == 0) {
        printf("Nenhum produto com estoque baixo.\n");
    }
    printf("================================\n");
}

// Lista produtos filtrados por categoria (case-insensitive)
void listarPorCategoria() {
    char categoria[TAM_CATEGORIA];
    char catMinuscula[TAM_CATEGORIA];
    char prodCatMinuscula[TAM_CATEGORIA];
    
    printf("Digite a categoria para listar: ");
    fgets(categoria, TAM_CATEGORIA, stdin);
    categoria[strcspn(categoria, "\n")] = '\0';
    
    strcpy(catMinuscula, categoria);
    paraMinusculas(catMinuscula);
    
    int encontrado = 0;
    printf("\n--- Produtos da Categoria: %s ---\n", categoria);
    for (int i = 0; i < totalProdutos; i++) {
        strcpy(prodCatMinuscula, produtos[i].categoria);
        paraMinusculas(prodCatMinuscula);
        
        if (strcmp(prodCatMinuscula, catMinuscula) == 0) {
            printf("[%d] %s | R$ %.2f | Estoque: %d\n",
                produtos[i].id, 
                produtos[i].nome,
                produtos[i].preco,
                produtos[i].quantidade_estoque);
            encontrado++;
        }
    }
    
    if (!encontrado) {
        printf("Nenhum produto encontrado nesta categoria.\n");
    }
}
