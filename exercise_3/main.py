import csv
import os
import random
import time
from typing import Callable

import matplotlib.pyplot as plt

MIN_VALUE = 0
MAX_VALUE = 10500

# Tamanhos de entrada avaliados.
# OBS: o enunciado sugere escalar até 500k/1.000k, mas para algoritmos O(n^2)
# em Python isso levaria horas (bubble sort com 20k elementos já leva ~14s
# apenas na passada "sem ordenação"). Reduzimos a escala para valores que
# terminam em tempo viável e ainda evidenciam o comportamento quadrático.
SIZES = [1000, 2000, 5000, 10000, 15000, 20000]


def generate_array(length: int) -> list[int]:
    array = []
    for _ in range(length):
        array.append(random.randint(MIN_VALUE, MAX_VALUE))
    return array


def swap(array: list[int], i: int, j: int) -> None:
    aux = array[i]
    array[i] = array[j]
    array[j] = aux


def bubble_sort(array: list[int]) -> list[int]:
    n = len(array)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if array[j] > array[j + 1]:
                swap(array, j, j + 1)
                swapped = True
        if not swapped:
            break
    return array


def insertion_sort(array: list[int]) -> list[int]:
    for i in range(1, len(array)):
        key = array[i]
        j = i - 1
        while j >= 0 and array[j] > key:
            array[j + 1] = array[j]
            j -= 1
        array[j + 1] = key
    return array


def exec_sort(func: Callable[[list[int]], list[int]], arrays: list[list[int]]) -> dict:
    """Executa `func` sobre cada array (sem ordenação) e depois sobre o
    resultado já ordenado (reordenação), medindo o tempo em ms."""
    result = {"unsorted": {}, "sorted": {}}
    sorted_arrays = []
    for array in arrays:
        data = array[:]
        start = time.perf_counter()
        func(data)
        elapsed = time.perf_counter() - start
        result["unsorted"][len(data)] = {
            "sort": func.__name__,
            "time_ms": elapsed * 1000,
        }
        sorted_arrays.append(data)

    for array in sorted_arrays:
        data = array[:]
        start = time.perf_counter()
        func(data)
        elapsed = time.perf_counter() - start
        result["sorted"][len(data)] = {
            "sort": func.__name__,
            "time_ms": elapsed * 1000,
        }
    return result


def collect_results(sizes: list[int]) -> dict:
    """Roda os dois algoritmos sobre os MESMOS conjuntos de dados (para
    comparação justa) e devolve um dicionário único com tudo."""
    unsorted_arrays = [generate_array(n) for n in sizes]

    bubble = exec_sort(bubble_sort, unsorted_arrays)
    insertion = exec_sort(insertion_sort, unsorted_arrays)

    return {
        "bubble_unsorted": bubble["unsorted"],
        "bubble_sorted": bubble["sorted"],
        "insertion_unsorted": insertion["unsorted"],
        "insertion_sorted": insertion["sorted"],
    }


def to_series(data: dict, key: str) -> tuple[list[int], list[float]]:
    """Extrai (tamanhos, tempos_ms) ordenados por tamanho a partir de um
    dos sub-dicionários retornados por collect_results."""
    d = data[key]
    ns = sorted(d.keys())
    times = [d[n]["time_ms"] for n in ns]
    return ns, times


def save_csv(data: dict, path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["algoritmo", "cenario", "n", "tempo_ms"])
        for key in ["bubble_unsorted", "bubble_sorted", "insertion_unsorted", "insertion_sorted"]:
            algoritmo = "bubble_sort" if "bubble" in key else "insertion_sort"
            cenario = "sem_ordenacao" if "unsorted" in key else "ja_ordenado"
            ns, times = to_series(data, key)
            for n, t in zip(ns, times):
                writer.writerow([algoritmo, cenario, n, f"{t:.4f}"])


def plot_pair(ax, data, keys, labels, title, log_y=False):
    for key, label in zip(keys, labels):
        ns, times = to_series(data, key)
        ax.plot(ns, times, marker="o", label=label)
    ax.set_xlabel("n (tamanho da entrada)")
    ax.set_ylabel("Tempo (ms)" + (" - escala log" if log_y else ""))
    if log_y:
        ax.set_yscale("log")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)


def make_graphs(data: dict, outdir: str) -> None:
    # 1) Bubble vs Insertion - dados SEM ordenação
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_pair(
        ax, data,
        keys=["bubble_unsorted", "insertion_unsorted"],
        labels=["Bubble Sort", "Insertion Sort"],
        title="Tempo de execução - dados sem ordenação",
    )
    fig.tight_layout()
    fig.savefig(f"{outdir}/1_sem_ordenacao.png", dpi=150)
    plt.close(fig)

    # 2) Bubble vs Insertion - dados JÁ ordenados (reordenação)
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_pair(
        ax, data,
        keys=["bubble_sorted", "insertion_sorted"],
        labels=["Bubble Sort", "Insertion Sort"],
        title="Tempo de execução - dados já ordenados",
    )
    fig.tight_layout()
    fig.savefig(f"{outdir}/2_ja_ordenado.png", dpi=150)
    plt.close(fig)

    # 3) Os dois algoritmos, sem ordenação + já ordenados (4 linhas)
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_pair(
        ax, data,
        keys=["bubble_unsorted", "insertion_unsorted", "bubble_sorted", "insertion_sorted"],
        labels=["Bubble - sem ordenação", "Insertion - sem ordenação",
                "Bubble - já ordenado", "Insertion - já ordenado"],
        title="Comparação combinada - sem ordenação x já ordenado",
        log_y=True,
    )
    fig.tight_layout()
    fig.savefig(f"{outdir}/3_combinado.png", dpi=150)
    plt.close(fig)

    # 4) Compilação de todos os gráficos anteriores em um painel único
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    plot_pair(
        axes[0], data,
        keys=["bubble_unsorted", "insertion_unsorted"],
        labels=["Bubble Sort", "Insertion Sort"],
        title="Sem ordenação",
    )
    plot_pair(
        axes[1], data,
        keys=["bubble_sorted", "insertion_sorted"],
        labels=["Bubble Sort", "Insertion Sort"],
        title="Já ordenado (reordenação)",
    )
    plot_pair(
        axes[2], data,
        keys=["bubble_unsorted", "insertion_unsorted", "bubble_sorted", "insertion_sorted"],
        labels=["Bubble - sem ordenação", "Insertion - sem ordenação",
                "Bubble - já ordenado", "Insertion - já ordenado"],
        title="Todos os cenários",
        log_y=True,
    )
    fig.suptitle("Compilação - Bubble Sort x Insertion Sort")
    fig.tight_layout()
    fig.savefig(f"{outdir}/4_compilacao.png", dpi=150)
    plt.close(fig)


def main() -> None:
    outdir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(outdir, exist_ok=True)
    data = collect_results(SIZES)

    save_csv(data, f"{outdir}/resultados.csv")
    make_graphs(data, outdir)

    for key in ["bubble_unsorted", "insertion_unsorted", "bubble_sorted", "insertion_sorted"]:
        print(key, data[key])


if __name__ == "__main__":
    main()