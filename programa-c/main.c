/*
 * ============================================================
 * PROJETO DE EXTENSAO - Desenvolvimento de Software
 * Turma Noturno 2026
 * ============================================================
 * Responsaveis:
 *   - Willian Soares Santana   (Estrutura principal e menu)
 *   - Guilherme Huilame        (Logica de negocio e cadastros)
 *   - Kaue Machado Vasconcellos (Validacoes e refinamento)
 * ============================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---- CONSTANTES ---- */
#define MAX_REGISTROS 100
#define TAM_NOME 50
#define TAM_EMAIL 60

/* ---- ESTRUTURAS DE DADOS ---- */
typedef struct {
    int id;
    char nome[TAM_NOME];
    char email[TAM_EMAIL];
    float valor;
} Registro;

/* ---- VARIAVEIS GLOBAIS ---- */
Registro registros[MAX_REGISTROS];
int totalRegistros = 0;

/* ---- PROTOTIPOS DAS FUNCOES ---- */
void exibirMenu();
void cadastrar();
void listar();
void buscar();
void limparBuffer();

/* ============================================================
 * FUNCAO PRINCIPAL
 * ============================================================ */
int main() {
    int opcao;

    printf("\n=== Sistema [Nome da Empresa] ===\n");

    do {
        exibirMenu();
        printf("\nDigite a opcao: ");
        scanf("%d", &opcao);
        limparBuffer();

        switch (opcao) {
            case 1:
                cadastrar();
                break;
            case 2:
                listar();
                break;
            case 3:
                buscar();
                break;
            case 0:
                printf("\nSaindo do sistema... Ate logo!\n");
                break;
            default:
                printf("\nOpcao invalida! Tente novamente.\n");
        }
    } while (opcao != 0);

    return 0;
}

/* ============================================================
 * EXIBE O MENU PRINCIPAL
 * Responsavel: Willian Soares Santana
 * ============================================================ */
void exibirMenu() {
    printf("\n----------------------------------------\n");
    printf("  MENU PRINCIPAL\n");
    printf("----------------------------------------\n");
    printf("  1 - Cadastrar registro\n");
    printf("  2 - Listar todos os registros\n");
    printf("  3 - Buscar por nome\n");
    printf("  0 - Sair\n");
    printf("----------------------------------------\n");
}

/* ============================================================
 * CADASTRA UM NOVO REGISTRO
 * Responsavel: Guilherme Huilame
 * ============================================================ */
void cadastrar() {
    if (totalRegistros >= MAX_REGISTROS) {
        printf("\nLimite de registros atingido!\n");
        return;
    }

    Registro novo;
    novo.id = totalRegistros + 1;

    printf("\n--- Novo Cadastro ---\n");
    printf("Nome: ");
    fgets(novo.nome, TAM_NOME, stdin);
    novo.nome[strcspn(novo.nome, "\n")] = '\0'; /* Remove quebra de linha */

    printf("Email: ");
    fgets(novo.email, TAM_EMAIL, stdin);
    novo.email[strcspn(novo.email, "\n")] = '\0';

    printf("Valor (R$): ");
    scanf("%f", &novo.valor);
    limparBuffer();

    /* Validacao basica - Kaue Machado Vasconcellos */
    if (strlen(novo.nome) == 0) {
        printf("\nErro: Nome nao pode ser vazio!\n");
        return;
    }

    registros[totalRegistros] = novo;
    totalRegistros++;

    printf("\nRegistro cadastrado com sucesso! ID: %d\n", novo.id);
}

/* ============================================================
 * LISTA TODOS OS REGISTROS
 * Responsavel: Guilherme Huilame
 * ============================================================ */
void listar() {
    if (totalRegistros == 0) {
        printf("\nNenhum registro cadastrado.\n");
        return;
    }

    printf("\n--- Lista de Registros (%d total) ---\n", totalRegistros);
    printf("%-5s %-30s %-30s %10s\n", "ID", "Nome", "Email", "Valor");
    printf("----------------------------------------------------------------------\n");

    int i;
    for (i = 0; i < totalRegistros; i++) {
        printf("%-5d %-30s %-30s R$%8.2f\n",
            registros[i].id,
            registros[i].nome,
            registros[i].email,
            registros[i].valor);
    }
}

/* ============================================================
 * BUSCA REGISTRO POR NOME
 * Responsavel: Kaue Machado Vasconcellos
 * ============================================================ */
void buscar() {
    char termoBusca[TAM_NOME];
    int encontrado = 0;

    printf("\nDigite o nome para buscar: ");
    fgets(termoBusca, TAM_NOME, stdin);
    termoBusca[strcspn(termoBusca, "\n")] = '\0';

    printf("\n--- Resultado da Busca ---\n");

    int i;
    for (i = 0; i < totalRegistros; i++) {
        /* Busca parcial por nome */
        if (strstr(registros[i].nome, termoBusca) != NULL) {
            printf("ID: %d | Nome: %s | Email: %s | Valor: R$%.2f\n",
                registros[i].id,
                registros[i].nome,
                registros[i].email,
                registros[i].valor);
            encontrado = 1;
        }
    }

    if (!encontrado) {
        printf("Nenhum registro encontrado para: %s\n", termoBusca);
    }
}

/* ============================================================
 * LIMPA O BUFFER DO TECLADO
 * Responsavel: Kaue Machado Vasconcellos
 * ============================================================ */
void limparBuffer() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}
