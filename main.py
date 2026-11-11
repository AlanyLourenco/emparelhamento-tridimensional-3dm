"""
main.py
=======
Executa um ou todos os algoritmos sobre uma instância lida de arquivo.

Uso:
    python main.py exemplo.txt               # todos os algoritmos
    python main.py exemplo.txt backtracking  # só um

Formato do arquivo: primeira linha "q m", depois m linhas "x y z".
"""

import sys
import time

from contador import Contador
from instancia import ler_arquivo, verificar_certificado
from forca_bruta import forca_bruta
from backtracking import backtracking
from divisao_conquista import divisao_conquista
from prog_dinamica import programacao_dinamica
from guloso import guloso
from aproximado import busca_local, emparelhamento_maximal

ALGORITMOS = {
    "forca_bruta": forca_bruta,
    "backtracking": backtracking,
    "divisao_conquista": divisao_conquista,
    "programacao_dinamica": programacao_dinamica,
    "maximal_simples": emparelhamento_maximal,
    "guloso": guloso,
    "busca_local": busca_local,
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    inst = ler_arquivo(sys.argv[1])
    nomes = sys.argv[2:] or list(ALGORITMOS)
    print(f"Instância: q = {inst.q}, |T| = {inst.m}\n")

    for nome in nomes:
        cont = Contador()
        t0 = time.perf_counter()
        M = ALGORITMOS[nome](inst, cont)
        dt = time.perf_counter() - t0

        if M is not None and len(M) == inst.q and verificar_certificado(inst, M):
            resp = "SIM"
        elif nome in ("maximal_simples", "guloso", "busca_local"):
            resp = f"não encontrou (achou {len(M)} de {inst.q})"
        else:
            resp = "NÃO"
        print(f"{nome:22s} {resp:30s} ops = {cont.ops:>10d}   tempo = {dt * 1000:9.3f} ms")
        if M and len(M) == inst.q:
            print(f"{'':22s} M = {sorted(M)}")


if __name__ == "__main__":
    main()
