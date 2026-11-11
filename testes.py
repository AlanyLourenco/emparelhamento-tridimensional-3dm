"""
testes.py
=========
Testes de corretude: os quatro algoritmos EXATOS precisam concordar entre
si (SIM/NÃO) e toda solução devolvida precisa passar no verificador.
Greedy e busca local precisam devolver emparelhamentos válidos, e nunca
maiores que q.

Uso:  python testes.py
"""

from contador import Contador
from instancia import (Instancia, gerar_com_solucao, gerar_aleatoria,
                       verificar_certificado, eh_emparelhamento)
from forca_bruta import forca_bruta
from backtracking import backtracking, maior_emparelhamento
from divisao_conquista import divisao_conquista
from prog_dinamica import programacao_dinamica
from greedy import greedy
from aproximado import busca_local, emparelhamento_maximal

EXATOS = [forca_bruta, backtracking, divisao_conquista, programacao_dinamica]
HEURISTICOS = [emparelhamento_maximal, greedy, busca_local]


def checa(inst):
    respostas = {}
    for alg in EXATOS:
        M = alg(inst, Contador())
        if M is not None:
            assert verificar_certificado(inst, M), (alg.__name__, inst, M)
        respostas[alg.__name__] = M is not None
    assert len(set(respostas.values())) == 1, (inst, respostas)
    tem_solucao = next(iter(respostas.values()))

    opt = maior_emparelhamento(inst)
    assert (opt == inst.q) == tem_solucao, (inst, opt)

    for alg in HEURISTICOS:
        M = alg(inst, Contador())
        assert eh_emparelhamento(inst, M), (alg.__name__, inst, M)
        assert len(M) <= opt                  # nunca passa do ótimo
        assert 3 * len(M) >= opt              # garantia de 1/3 (maximal)
        if alg is busca_local:
            assert 2 * len(M) >= opt          # garantia de 1/2 (busca local)
        if len(M) == inst.q:                 # se achou perfeito, existe solução
            assert tem_solucao
    return tem_solucao


def main():
    # Casos feitos à mão
    sim = Instancia(2, [(0, 0, 0), (1, 1, 1), (0, 1, 0)])
    nao = Instancia(2, [(0, 0, 0), (1, 0, 1), (0, 1, 1)])   # y=1 e z=0 só juntos com x=0
    assert checa(sim) is True
    assert checa(nao) is False
    assert checa(Instancia(1, [(0, 0, 0)])) is True
    assert checa(Instancia(3, [(0, 0, 0)])) is False

    # Casos aleatórios
    sims = naos = 0
    for semente in range(400):
        q = 1 + semente % 6
        if semente % 2:
            inst = gerar_com_solucao(q, extras=2 * q, semente=semente)
        else:
            inst = gerar_aleatoria(q, m=3 * q, semente=semente)
        if checa(inst):
            sims += 1
        else:
            naos += 1
    print(f"OK: 404 instâncias testadas ({sims + 2} SIM, {naos + 2} NÃO)")


if __name__ == "__main__":
    main()
