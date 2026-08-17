"""
Atividade Prática - Implementação
Gera vetor aleatório, ordena e identifica números primos.
Única biblioteca permitida: random.
"""

import random

TAMANHO = 10000
VALOR_MIN = 0
VALOR_MAX = 15000

vetor = []


def gerar_vetor():
    """Gera um vetor com 10.000 inteiros aleatórios entre 0 e 15.000."""
    global vetor
    vetor = []
    for _ in range(TAMANHO):
        vetor.append(random.randint(VALOR_MIN, VALOR_MAX))
    print(f"Vetor gerado com {len(vetor)} valores (entre {VALOR_MIN} e {VALOR_MAX}).")
    print(f"Primeiros 20 valores: {vetor[:20]}")


def trocar(lista, i, j):
    aux = lista[i]
    lista[i] = lista[j]
    lista[j] = aux


def particionar(lista, inicio, fim):
    """Particiona o vetor em torno do pivô (último elemento)."""
    pivo = lista[fim]
    i = inicio - 1
    for j in range(inicio, fim):
        if lista[j] <= pivo:
            i += 1
            trocar(lista, i, j)
    trocar(lista, i + 1, fim)
    return i + 1


def quicksort(lista, inicio, fim):
    """Ordenação QuickSort em ordem crescente."""
    if inicio < fim:
        pos_pivo = particionar(lista, inicio, fim)
        quicksort(lista, inicio, pos_pivo - 1)
        quicksort(lista, pos_pivo + 1, fim)


def ordenar_vetor():
    """Ordena o vetor atual em ordem crescente (QuickSort)."""
    quicksort(vetor, 0, len(vetor) - 1)
    print(f"Vetor ordenado ({len(vetor)} elementos).")
    print(f"Primeiros 20 valores: {vetor[:20]}")
    print(f"Últimos 20 valores: {vetor[-20:]}")


def eh_primo(n):
    """Verifica se um número é primo."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def filtrar_primos():
    """Mantém no vetor apenas os números primos do estado atual."""
    global vetor
    primos = []
    for valor in vetor:
        if eh_primo(valor):
            primos.append(valor)
    vetor = primos
    print(f"Vetor atualizado: {len(vetor)} números primos.")
    if len(vetor) == 0:
        print("Nenhum número primo no estado atual.")
        return
    print(f"Primeiros 20 valores: {vetor[:20]}")


def exibir_menu():
    print("\n" + "=" * 40)
    print("  Atividade Prática – Implementação")
    print("=" * 40)
    print("1 - Ordenar")
    print("2 - Pegar só os primos do estado atual")
    print("0 - Sair")
    print("=" * 40)


def main():
    gerar_vetor()
    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            ordenar_vetor()
        elif opcao == "2":
            filtrar_primos()
        elif opcao == "0":
            print("Encerrando o programa.")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
