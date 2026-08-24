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


def shell_sort(array: list[int]) -> list[int]:
    n = len(array)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            key = array[i]
            j = i
            while j >= gap and array[j - gap] > key:
                array[j] = array[j - gap]
                j -= gap
            array[j] = key
        gap //= 2
    return array


def _partition(array: list[int], low: int, high: int) -> int:
    # Pivô no meio evita o pior caso O(n^2) em vetores já ordenados.
    mid = (low + high) // 2
    swap(array, mid, high)
    pivot = array[high]
    i = low - 1
    for j in range(low, high):
        if array[j] <= pivot:
            i += 1
            swap(array, i, j)
    swap(array, i + 1, high)
    return i + 1


def _quick_sort(array: list[int], low: int, high: int) -> None:
    if low < high:
        pivot = _partition(array, low, high)
        _quick_sort(array, low, pivot - 1)
        _quick_sort(array, pivot + 1, high)


def quick_sort(array: list[int]) -> list[int]:
    if array:
        _quick_sort(array, 0, len(array) - 1)
    return array


def _merge(array: list[int], left: int, mid: int, right: int) -> None:
    left_part = array[left:mid + 1]
    right_part = array[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            array[k] = left_part[i]
            i += 1
        else:
            array[k] = right_part[j]
            j += 1
        k += 1
    while i < len(left_part):
        array[k] = left_part[i]
        i += 1
        k += 1
    while j < len(right_part):
        array[k] = right_part[j]
        j += 1
        k += 1


def _merge_sort(array: list[int], left: int, right: int) -> None:
    if left < right:
        mid = (left + right) // 2
        _merge_sort(array, left, mid)
        _merge_sort(array, mid + 1, right)
        _merge(array, left, mid, right)


def merge_sort(array: list[int]) -> list[int]:
    if array:
        _merge_sort(array, 0, len(array) - 1)
    return array


ALGORITHMS: list[tuple[str, Callable[[list[int]], list[int]], str]] = [
    ("bubble", bubble_sort, "Bubble Sort"),
    ("insertion", insertion_sort, "Insertion Sort"),
    ("shell", shell_sort, "Shell Sort"),
    ("quick", quick_sort, "Quick Sort"),
    ("merge", merge_sort, "Merge Sort"),
]


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
    """Roda todos os algoritmos sobre os MESMOS conjuntos de dados (para
    comparação justa) e devolve um dicionário único com tudo."""
    unsorted_arrays = [generate_array(n) for n in sizes]
    results = {}
    for key, func, _ in ALGORITHMS:
        measured = exec_sort(func, unsorted_arrays)
        results[f"{key}_unsorted"] = measured["unsorted"]
        results[f"{key}_sorted"] = measured["sorted"]
    return results


def result_keys() -> list[str]:
    keys = []
    for key, _, _ in ALGORITHMS:
        keys.append(f"{key}_unsorted")
        keys.append(f"{key}_sorted")
    return keys


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
        for key, func, _ in ALGORITHMS:
            for cenario_key, cenario in [("unsorted", "sem_ordenacao"), ("sorted", "ja_ordenado")]:
                ns, times = to_series(data, f"{key}_{cenario_key}")
                for n, t in zip(ns, times):
                    writer.writerow([func.__name__, cenario, n, f"{t:.4f}"])


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
    unsorted_keys = [f"{key}_unsorted" for key, _, _ in ALGORITHMS]
    sorted_keys = [f"{key}_sorted" for key, _, _ in ALGORITHMS]
    labels = [label for _, _, label in ALGORITHMS]
    combined_keys = unsorted_keys + sorted_keys
    combined_labels = (
        [f"{label} - sem ordenação" for label in labels]
        + [f"{label} - já ordenado" for label in labels]
    )

    # 1) Todos os algoritmos - dados SEM ordenação
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_pair(
        ax, data,
        keys=unsorted_keys,
        labels=labels,
        title="Tempo de execução - dados sem ordenação",
        log_y=True,
    )
    fig.tight_layout()
    fig.savefig(f"{outdir}/1_sem_ordenacao.png", dpi=150)
    plt.close(fig)

    # 2) Todos os algoritmos - dados JÁ ordenados (reordenação)
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_pair(
        ax, data,
        keys=sorted_keys,
        labels=labels,
        title="Tempo de execução - dados já ordenados",
        log_y=True,
    )
    fig.tight_layout()
    fig.savefig(f"{outdir}/2_ja_ordenado.png", dpi=150)
    plt.close(fig)

    # 3) Todos os algoritmos, sem ordenação + já ordenados
    fig, ax = plt.subplots(figsize=(12, 6))
    plot_pair(
        ax, data,
        keys=combined_keys,
        labels=combined_labels,
        title="Comparação combinada - sem ordenação x já ordenado",
        log_y=True,
    )
    fig.tight_layout()
    fig.savefig(f"{outdir}/3_combinado.png", dpi=150)
    plt.close(fig)

    # 4) Compilação de todos os gráficos anteriores em um painel único
    fig, axes = plt.subplots(1, 3, figsize=(20, 5))
    plot_pair(
        axes[0], data,
        keys=unsorted_keys,
        labels=labels,
        title="Sem ordenação",
        log_y=True,
    )
    plot_pair(
        axes[1], data,
        keys=sorted_keys,
        labels=labels,
        title="Já ordenado (reordenação)",
        log_y=True,
    )
    plot_pair(
        axes[2], data,
        keys=combined_keys,
        labels=combined_labels,
        title="Todos os cenários",
        log_y=True,
    )
    fig.suptitle("Compilação - algoritmos de ordenação")
    fig.tight_layout()
    fig.savefig(f"{outdir}/4_compilacao.png", dpi=150)
    plt.close(fig)


def main() -> None:
    outdir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(outdir, exist_ok=True)
    data = collect_results(SIZES)

    save_csv(data, f"{outdir}/resultados.csv")
    make_graphs(data, outdir)

    for key in result_keys():
        print(key, data[key])


if __name__ == "__main__":
    main()
