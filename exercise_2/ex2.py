"""
Experimento do Relatório (Aula 2).
Métricas: TempoGerar, TempoOrdenar, TempoPrimos, TempoTotal,
comparações na ordenação e quantidade de primos.
Cenários por n: C[Des] (aleatório) e C[Ord] (mesmo vetor já ordenado).
"""

from __future__ import annotations

import csv
import random
import time
from pathlib import Path

VALOR_MIN = 0
VALOR_MAX = 15000
TAMANHOS = [1000, 5000, 10000, 50000, 100000]
SEED = 42

comparacoes = 0


def gerar_vetor(n: int) -> list[int]:
    return [random.randint(VALOR_MIN, VALOR_MAX) for _ in range(n)]


def trocar(lista: list[int], i: int, j: int) -> None:
    lista[i], lista[j] = lista[j], lista[i]


def particionar(lista: list[int], inicio: int, fim: int) -> int:
    """Particionamento de Lomuto (pivô = último elemento), com contagem de comparações."""
    global comparacoes
    pivo = lista[fim]
    i = inicio - 1
    for j in range(inicio, fim):
        comparacoes += 1
        if lista[j] <= pivo:
            i += 1
            trocar(lista, i, j)
    trocar(lista, i + 1, fim)
    return i + 1


def quicksort(lista: list[int]) -> None:
    """
    QuickSort equivalente ao de main.py (Lomuto, pivô no fim).
    Versão iterativa com pilha explícita para evitar estouro de recursão
    no pior caso (vetor já ordenado), mantendo as mesmas comparações/trocas.
    """
    if len(lista) < 2:
        return
    pilha = [(0, len(lista) - 1)]
    while pilha:
        inicio, fim = pilha.pop()
        if inicio < fim:
            pos = particionar(lista, inicio, fim)
            # Empilha o maior lado primeiro para limitar a profundidade da pilha.
            esq = (inicio, pos - 1)
            dir_ = (pos + 1, fim)
            if pos - inicio > fim - pos:
                pilha.append(esq)
                pilha.append(dir_)
            else:
                pilha.append(dir_)
                pilha.append(esq)


def eh_primo(n: int) -> bool:
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


def filtrar_primos(lista: list[int]) -> list[int]:
    return [v for v in lista if eh_primo(v)]


def ms(segundos: float) -> float:
    return round(segundos * 1000, 3)


def executar_cenario(n: int, cenario_idx: int) -> list[dict]:
    """
    Para cada n:
      C[Des] - gera, ordena vetor desordenado, filtra primos
      C[Ord] - reutiliza o mesmo TempoGerar e o vetor já ordenado
    """
    random.seed(SEED + n)

    t0 = time.perf_counter()
    vetor = gerar_vetor(n)
    tempo_gerar = time.perf_counter() - t0

    resultados = []

    # --- C[Des]: ordenação sobre vetor aleatório ---
    global comparacoes
    desordenado = vetor[:]
    comparacoes = 0
    t0 = time.perf_counter()
    quicksort(desordenado)
    tempo_ordenar_des = time.perf_counter() - t0
    comps_des = comparacoes

    t0 = time.perf_counter()
    primos_des = filtrar_primos(desordenado)
    tempo_primos_des = time.perf_counter() - t0

    tempo_total_des = tempo_gerar + tempo_ordenar_des + tempo_primos_des
    resultados.append(
        {
            "cenario": f"C{cenario_idx} [Des]",
            "tipo": "Desordenado",
            "n": n,
            "TempoGerar_ms": ms(tempo_gerar),
            "TempoOrdenar_ms": ms(tempo_ordenar_des),
            "TempoPrimos_ms": ms(tempo_primos_des),
            "TempoTotal_ms": ms(tempo_total_des),
            "comparacoes": comps_des,
            "qtd_primos": len(primos_des),
            "amostra_primos": primos_des[:15],
        }
    )

    # --- C[Ord]: mesmo vetor já ordenado; TempoGerar idêntico ---
    ordenado = desordenado[:]  # cópia do resultado já ordenado
    comparacoes = 0
    t0 = time.perf_counter()
    quicksort(ordenado)
    tempo_ordenar_ord = time.perf_counter() - t0
    comps_ord = comparacoes

    t0 = time.perf_counter()
    primos_ord = filtrar_primos(ordenado)
    tempo_primos_ord = time.perf_counter() - t0

    tempo_total_ord = tempo_gerar + tempo_ordenar_ord + tempo_primos_ord
    resultados.append(
        {
            "cenario": f"C{cenario_idx + 1} [Ord]",
            "tipo": "Ordenado",
            "n": n,
            "TempoGerar_ms": ms(tempo_gerar),  # mesmo valor do Des
            "TempoOrdenar_ms": ms(tempo_ordenar_ord),
            "TempoPrimos_ms": ms(tempo_primos_ord),
            "TempoTotal_ms": ms(tempo_total_ord),
            "comparacoes": comps_ord,
            "qtd_primos": len(primos_ord),
            "amostra_primos": primos_ord[:15],
        }
    )

    return resultados


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    campos = [
        "cenario",
        "tipo",
        "n",
        "TempoGerar_ms",
        "TempoOrdenar_ms",
        "TempoPrimos_ms",
        "TempoTotal_ms",
        "comparacoes",
        "qtd_primos",
        "amostra_primos",
    ]
    with caminho.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for row in linhas:
            out = dict(row)
            out["amostra_primos"] = " ".join(map(str, row["amostra_primos"]))
            w.writerow(out)


def gerar_graficos(linhas: list[dict], pasta: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não disponível — pulando gráficos.")
        return

    des = [r for r in linhas if r["tipo"] == "Desordenado"]
    ord_ = [r for r in linhas if r["tipo"] == "Ordenado"]
    ns = [r["n"] for r in des]

    # Gráfico por tamanho (barras Des vs Ord)
    for i, n in enumerate(ns):
        d, o = des[i], ord_[i]
        labels = ["Gerar", "Ordenar", "Primos", "Total"]
        vals_d = [
            d["TempoGerar_ms"],
            d["TempoOrdenar_ms"],
            d["TempoPrimos_ms"],
            d["TempoTotal_ms"],
        ]
        vals_o = [
            o["TempoGerar_ms"],
            o["TempoOrdenar_ms"],
            o["TempoPrimos_ms"],
            o["TempoTotal_ms"],
        ]
        x = range(len(labels))
        width = 0.35
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.bar([xi - width / 2 for xi in x], vals_d, width, label="C[Des]")
        ax.bar([xi + width / 2 for xi in x], vals_o, width, label="C[Ord]")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels)
        ax.set_ylabel("Tempo (ms)")
        ax.set_title(f"Tempos por fase — n = {n}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pasta / f"grafico_n_{n}.png", dpi=140)
        plt.close(fig)

    # Gráfico final: TempoOrdenar e TempoTotal vs n
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].plot(ns, [r["TempoOrdenar_ms"] for r in des], "o-", label="C[Des]")
    axes[0].plot(ns, [r["TempoOrdenar_ms"] for r in ord_], "s-", label="C[Ord]")
    axes[0].set_xlabel("n")
    axes[0].set_ylabel("TempoOrdenar (ms)")
    axes[0].set_title("Tempo de ordenação × tamanho")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(ns, [r["TempoTotal_ms"] for r in des], "o-", label="C[Des]")
    axes[1].plot(ns, [r["TempoTotal_ms"] for r in ord_], "s-", label="C[Ord]")
    axes[1].set_xlabel("n")
    axes[1].set_ylabel("TempoTotal (ms)")
    axes[1].set_title("Tempo total × tamanho")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(pasta / "grafico_final_todos.png", dpi=140)
    plt.close(fig)

    # Comparações
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(ns, [r["comparacoes"] for r in des], "o-", label="C[Des]")
    ax.plot(ns, [r["comparacoes"] for r in ord_], "s-", label="C[Ord]")
    ax.set_xlabel("n")
    ax.set_ylabel("Comparações")
    ax.set_title("Comparações na ordenação × tamanho")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(pasta / "grafico_comparacoes.png", dpi=140)
    plt.close(fig)


def main() -> None:
    pasta = Path(__file__).resolve().parent / "resultados"
    pasta.mkdir(exist_ok=True)

    print("Iniciando experimento...")
    print(f"Tamanhos: {TAMANHOS}")
    print(f"Intervalo dos valores: [{VALOR_MIN}, {VALOR_MAX}]")
    print(f"Seed base: {SEED}")
    print("-" * 72)

    todas: list[dict] = []
    cenario_idx = 1
    for n in TAMANHOS:
        print(f"\n>>> n = {n} ...")
        t_ini = time.perf_counter()
        res = executar_cenario(n, cenario_idx)
        elapsed = time.perf_counter() - t_ini
        for r in res:
            todas.append(r)
            print(
                f"  {r['cenario']:12} | Gerar={r['TempoGerar_ms']:10.3f} ms | "
                f"Ordenar={r['TempoOrdenar_ms']:12.3f} ms | "
                f"Primos={r['TempoPrimos_ms']:10.3f} ms | "
                f"Total={r['TempoTotal_ms']:12.3f} ms | "
                f"comps={r['comparacoes']:,} | primos={r['qtd_primos']}"
            )
        print(f"  (bloco n={n} concluiu em {elapsed:.1f}s)")
        cenario_idx += 2

    csv_path = pasta / "tabela_execucao.csv"
    salvar_csv(todas, csv_path)
    print(f"\nCSV salvo em: {csv_path}")

    gerar_graficos(todas, pasta)
    print(f"Gráficos em: {pasta}")
    print("Concluído.")


if __name__ == "__main__":
    main()
