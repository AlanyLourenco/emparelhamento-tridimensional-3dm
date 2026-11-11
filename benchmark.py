"""
benchmark.py
============
Experimentos para a Análise de Resultados:
  - tempo de execução (time.perf_counter) e
  - número de operações básicas (Contador)
para cada algoritmo, variando q.

Experimento 1 (exatos): q pequeno, instâncias com e sem solução.
Experimento 2 (guloso e busca local): q grande, mede tempo, operações e
              a QUALIDADE  |M| / q  (1.0 = achou emparelhamento perfeito).
Experimento 3 (razão de aproximação): instâncias aleatórias (sem solução
              plantada), q pequeno; compara |M| de cada heurística com o
              ótimo OPT calculado por branch-and-bound.

Um algoritmo deixa de ser testado em tamanhos maiores quando a média do
tempo passa de LIMITE_S segundos (crescimento exponencial).

Saída: resultados/exatos.csv, resultados/heuristicos.csv e gráficos .png

Uso:  python benchmark.py            (completo)
      python benchmark.py --rapido   (teste rápido)
"""

import csv
import os
import statistics
import sys
import time

from contador import Contador
from instancia import gerar_com_solucao, gerar_aleatoria, verificar_certificado
from forca_bruta import forca_bruta
from backtracking import backtracking, maior_emparelhamento
from divisao_conquista import divisao_conquista
from prog_dinamica import programacao_dinamica
from guloso import guloso
from aproximado import busca_local, emparelhamento_maximal

RAPIDO = "--rapido" in sys.argv
LIMITE_S = 0.5 if RAPIDO else 5.0
REPETICOES = 3 if RAPIDO else 5
FATOR_TRIPLAS = 5          # |T| ≈ 5q: região de transição de fase (instâncias mais difíceis)

EXATOS = [forca_bruta, backtracking, divisao_conquista, programacao_dinamica]
HEURISTICOS = [emparelhamento_maximal, guloso, busca_local]

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


def mede(alg, inst):
    cont = Contador()
    t0 = time.perf_counter()
    M = alg(inst, cont)
    return M, time.perf_counter() - t0, cont.ops


def experimento_exatos():
    linhas = []
    qs = range(2, 13 if RAPIDO else 25)
    for tipo in ("com_solucao", "aleatoria"):
        ativos = {a.__name__ for a in EXATOS}
        for q in qs:
            insts = []
            for r in range(REPETICOES):
                sem = 1000 * q + r
                if tipo == "com_solucao":
                    insts.append(gerar_com_solucao(q, (FATOR_TRIPLAS - 1) * q, sem))
                else:
                    insts.append(gerar_aleatoria(q, FATOR_TRIPLAS * q, sem))
            for alg in EXATOS:
                if alg.__name__ not in ativos:
                    continue
                tempos, ops, sims = [], [], 0
                for inst in insts:
                    M, dt, n = mede(alg, inst)
                    if M is not None:
                        assert verificar_certificado(inst, M)
                        sims += 1
                    tempos.append(dt)
                    ops.append(n)
                media = statistics.mean(tempos)
                linhas.append({
                    "tipo": tipo, "algoritmo": alg.__name__, "q": q,
                    "m": FATOR_TRIPLAS * q,
                    "tempo_medio_s": media,
                    "tempo_desvio_s": statistics.pstdev(tempos),
                    "ops_media": statistics.mean(ops),
                    "respostas_sim": sims, "repeticoes": len(insts),
                })
                print(f"[{tipo:11s}] {alg.__name__:22s} q={q:3d}  "
                      f"t={media:10.5f}s  ops={statistics.mean(ops):14.1f}  SIM={sims}")
                if media > LIMITE_S:
                    ativos.discard(alg.__name__)   # passou do limite: para de crescer
            if not ativos:
                break
    return linhas


def experimento_heuristicos():
    linhas = []
    qs = [10, 20, 50, 100] if RAPIDO else [10, 20, 50, 100, 200, 400, 700, 1000]
    for q in qs:
        insts = [gerar_com_solucao(q, (FATOR_TRIPLAS - 1) * q, 7000 * q + r)
                 for r in range(REPETICOES)]
        for alg in HEURISTICOS:
            tempos, ops, qual = [], [], []
            for inst in insts:
                M, dt, n = mede(alg, inst)
                tempos.append(dt)
                ops.append(n)
                qual.append(len(M) / q)
            linhas.append({
                "algoritmo": alg.__name__, "q": q, "m": FATOR_TRIPLAS * q,
                "tempo_medio_s": statistics.mean(tempos),
                "ops_media": statistics.mean(ops),
                "qualidade_media": statistics.mean(qual),
                "qualidade_min": min(qual),
                "perfeitos": sum(1 for v in qual if v == 1.0),
                "repeticoes": len(insts),
            })
            print(f"[heurística] {alg.__name__:22s} q={q:5d}  "
                  f"t={statistics.mean(tempos):9.5f}s  qualidade={statistics.mean(qual):.3f}")
    return linhas


def experimento_razao():
    linhas = []
    qs = [6, 8, 10] if RAPIDO else [6, 8, 10, 12, 14, 16]
    n = 10 if RAPIDO else 30
    for q in qs:
        for fator in (2, 3, 5):
            razoes = {a.__name__: [] for a in HEURISTICOS}
            for r in range(n):
                inst = gerar_aleatoria(q, fator * q, 9000 * q + 100 * fator + r)
                opt = maior_emparelhamento(inst)
                for alg in HEURISTICOS:
                    M = alg(inst, Contador())
                    razoes[alg.__name__].append(len(M) / opt)
            for alg in HEURISTICOS:
                v = razoes[alg.__name__]
                linhas.append({
                    "algoritmo": alg.__name__, "q": q, "m": fator * q,
                    "razao_media": statistics.mean(v), "razao_min": min(v),
                    "otimos": sum(1 for x in v if x == 1.0), "instancias": n,
                })
                print(f"[razão] {alg.__name__:22s} q={q:3d} m={fator*q:3d}  "
                      f"média={statistics.mean(v):.3f}  mín={min(v):.3f}")
    return linhas


def salva_csv(nome, linhas):
    caminho = os.path.join(PASTA, nome)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    print("salvo:", caminho)


NOMES = {
    "forca_bruta": "Força bruta", "backtracking": "Backtracking",
    "divisao_conquista": "Divisão e conquista",
    "programacao_dinamica": "Programação dinâmica",
    "emparelhamento_maximal": "Maximal simples", "guloso": "Guloso",
    "busca_local": "Busca local",
}
CORES = {
    "forca_bruta": "#b2182b", "backtracking": "#2166ac",
    "divisao_conquista": "#1b7837", "programacao_dinamica": "#762a83",
    "emparelhamento_maximal": "#8c510a", "guloso": "#01665e",
    "busca_local": "#c51b7d",
}


def graficos(exatos, heur, razao):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib não instalado: gráficos não gerados")
        return
    plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False})

    for tipo, titulo in (("com_solucao", "com solução plantada"),
                         ("aleatoria", "aleatórias")):
        for medida, rotulo, arq in (("tempo_medio_s", "Tempo médio (s)", "tempo"),
                                    ("ops_media", "Operações básicas", "ops")):
            plt.figure(figsize=(6.4, 4))
            for alg in EXATOS:
                pts = [(l["q"], l[medida]) for l in exatos
                       if l["tipo"] == tipo and l["algoritmo"] == alg.__name__]
                if pts:
                    xs, ys = zip(*pts)
                    plt.plot(xs, [max(y, 1e-7) for y in ys], marker="o", ms=4,
                             color=CORES[alg.__name__], label=NOMES[alg.__name__])
            plt.yscale("log")
            plt.xlabel("q (número de elementos de cada conjunto)")
            plt.ylabel(rotulo + " – escala log")
            plt.title(f"Algoritmos exatos – instâncias {titulo}, |T| = {FATOR_TRIPLAS}q")
            plt.grid(True, which="major", alpha=0.3)
            plt.legend(frameon=False)
            plt.tight_layout()
            plt.savefig(os.path.join(PASTA, f"exatos_{arq}_{tipo}.png"), dpi=200)
            plt.close()

    fig, eixos = plt.subplots(1, 2, figsize=(9, 3.8))
    for alg in HEURISTICOS:
        n = alg.__name__
        pts = [l for l in heur if l["algoritmo"] == n]
        kw = dict(marker="o", ms=4, color=CORES[n], label=NOMES[n])
        eixos[0].plot([l["q"] for l in pts], [l["tempo_medio_s"] for l in pts], **kw)
        eixos[1].plot([l["q"] for l in pts], [l["qualidade_media"] for l in pts], **kw)
    eixos[0].set_xlabel("q"); eixos[0].set_ylabel("Tempo médio (s)")
    eixos[0].set_title("(a) Tempo de execução")
    eixos[1].set_xlabel("q"); eixos[1].set_ylabel("|M| / q")
    eixos[1].set_title("(b) Qualidade (1 = emparelhamento perfeito)")
    eixos[1].set_ylim(0.5, 1.02)
    for e in eixos:
        e.grid(True, alpha=0.3); e.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA, "heuristicos.png"), dpi=200)
    plt.close()

    fig, eixos = plt.subplots(1, 3, figsize=(10, 3.4), sharey=True)
    for e, fator in zip(eixos, (2, 3, 5)):
        for alg in HEURISTICOS:
            n = alg.__name__
            pts = [l for l in razao if l["algoritmo"] == n and l["m"] == fator * l["q"]]
            e.plot([l["q"] for l in pts], [l["razao_media"] for l in pts],
                   marker="o", ms=4, color=CORES[n], label=NOMES[n])
        e.axhline(1 / 3, ls=":", color="gray"); e.axhline(1 / 2, ls="--", color="gray")
        e.set_title(f"|T| = {fator}q"); e.set_xlabel("q"); e.grid(True, alpha=0.3)
    eixos[0].set_ylabel("|M| / OPT (média)")
    eixos[0].set_ylim(0.3, 1.02)
    eixos[0].legend(frameon=False, loc="lower left")
    plt.tight_layout()
    plt.savefig(os.path.join(PASTA, "razao_aproximacao.png"), dpi=200)
    plt.close()
    print("gráficos salvos em", PASTA)


def main():
    os.makedirs(PASTA, exist_ok=True)
    exatos = experimento_exatos()
    salva_csv("exatos.csv", exatos)
    heur = experimento_heuristicos()
    salva_csv("heuristicos.csv", heur)
    razao = experimento_razao()
    salva_csv("razao_aproximacao.csv", razao)
    graficos(exatos, heur, razao)


if __name__ == "__main__":
    main()
