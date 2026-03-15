/*
 * --------------------------------------------------------
 * PROJETO DE EXTENSAO - Desenvolvimento de Software
 * Turma Noturno 2026
 * --------------------------------------------------------
 * Responsaveis (Squad C):
 *   - Willian Soares Santana   (Estrutura principal, menu e validacoes)
 *   - Guilherme Huilame        (Logica de negocio, cadastros e refinamento)
 * --------------------------------------------------------
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

/* ---- PROTOTIPOS ---- */
void exibirMenu();
void cadastrar();
void listar();
void buscar();
void remover();
void calcularTotal();

/* ====================================================
   FUNCAO PRINCIPAL
   ==================================================== */
int main() {
    int opcao;

    do {
        exibirMenu();
        printf("Escolha uma opcao: ");
        scanf("%d", &opcao);
        getchar(); /* limpa buffer */

        switch (opcao) {
            case 1: cadastrar();     break;
            case 2: listar();        break;
            case 3: buscar();        break;
            case 4: remover();       break;
            case 5: calcularTotal(); break;
            case 0: printf("Encerrando...\n"); break;
            default: printf("Opcao invalida!\n");
        }
    } while (opcao != 0);

    return 0;
}

/* ====================================================
   MENU PRINCIPAL  (Willian)
   ==================================================== */
void exibirMenu() {
    printf("\n===== SISTEMA DE GESTAO =====");
    printf("\n 1. Cadastrar");
    printf("\n 2. Listar todos");
    printf("\n 3. Buscar por nome");
    printf("\n 4. Remover registro");
    printf("\n 5. Calcular total");
    printf("\n 0. Sair");
    printf("\n============================\n");
}

/* ====================================================
   CADASTRO  (Guilherme)
   ==================================================== */
void cadastrar() {
    if (totalRegistros >= MAX_REGISTROS) {
        printf("Limite de registros atingido!\n");
        return;
    }

    Registro r;
    r.id = totalRegistros + 1;

    printf("Nome: ");
    fgets(r.nome, TAM_NOME, stdin);
    r.nome[strcspn(r.nome, "\n")] = '\0';

    printf("Email: ");
    fgets(r.email, TAM_EMAIL, stdin);
    r.email[strcspn(r.email, "\n")] = '\0';

    printf("Valor: ");
    scanf("%f", &r.valor);
    getchar();

    registros[totalRegistros++] = r;
    printf("Cadastrado com sucesso! ID: %d\n", r.id);
}

/* ====================================================
   LISTAGEM  (Willian)
   ==================================================== */
void listar() {
    if (totalRegistros == 0) {
        printf("Nenhum registro encontrado.\n");
        return;
    }
    printf("\n%-5s %-30s %-35s %10s\n", "ID", "Nome", "Email", "Valor");
    printf("%-5s %-30s %-35s %10s\n", "----", "------------------------------", "-----------------------------------", "----------");
    for (int i = 0; i < totalRegistros; i++) {
        printf("%-5d %-30s %-35s %10.2f\n",
            registros[i].id,
            registros[i].nome,
            registros[i].email,
            registros[i].valor);
    }
}

/* ====================================================
   BUSCA POR NOME  (Guilherme)
   ==================================================== */
void buscar() {
    char termo[TAM_NOME];
    printf("Digite o nome para buscar: ");
    fgets(termo, TAM_NOME, stdin);
    termo[strcspn(termo, "\n")] = '\0';

    int encontrado = 0;
    for (int i = 0; i < totalRegistros; i++) {
        if (strstr(registros[i].nome, termo) != NULL) {
            printf("[%d] %s | %s | R$ %.2f\n",
                registros[i].id,
                registros[i].nome,
                registros[i].email,
                registros[i].valor);
            encontrado++;
        }
    }
    if (!encontrado) printf("Nenhum resultado para '%s'.\n", termo);
}

/* ====================================================
   REMOCAO  (Willian)
   ==================================================== */
void remover() {
    int id;
    printf("ID do registro a remover: ");
    scanf("%d", &id);
    getchar();

    for (int i = 0; i < totalRegistros; i++) {
        if (registros[i].id == id) {
            for (int j = i; j < totalRegistros - 1; j++) {
                registros[j] = registros[j + 1];
            }
            totalRegistros--;
            printf("Registro removido.\n");
            return;
        }
    }
    printf("ID nao encontrado.\n");
}

/* ====================================================
   CALCULO DE TOTAL  (Guilherme)
   ==================================================== */
void calcularTotal() {
    float total = 0;
    for (int i = 0; i < totalRegistros; i++) {
        total += registros[i].valor;
    }
    printf("Total de registros: %d\n", totalRegistros);
    printf("Soma dos valores:   R$ %.2f\n", total);
    if (totalRegistros > 0)
        printf("Media dos valores:  R$ %.2f\n", total / totalRegistros);
}
