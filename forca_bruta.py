"""
forca_bruta.py
==============
Estratégia: FORÇA BRUTA.

Ideia: um emparelhamento perfeito tem exatamente q triplas. Então basta
enumerar TODOS os subconjuntos de T com q triplas e testar cada um.

Complexidade (m = |T|):
    - número de candidatos: C(m, q)
    - teste de cada candidato: O(q)
    - tempo no pior caso: O(C(m, q) · q)   -> exponencial
    - espaço: O(q) (uma combinação por vez + marcadores de uso)
"""

from itertools import combinations


def forca_bruta(inst, cont):
    """Retorna uma lista com q triplas formando emparelhamento perfeito, ou None."""
    q = inst.q

    for candidato in combinations(inst.triplas, q):    # C(m, q) candidatos
        usadoX, usadoY, usadoZ = set(), set(), set()
        valido = True
        for (x, y, z) in candidato:                     # até q testes
            cont.ops += 1                               # operação básica
            if x in usadoX or y in usadoY or z in usadoZ:
                valido = False                          # conflito: descarta
                break
            usadoX.add(x)
            usadoY.add(y)
            usadoZ.add(z)
        if valido:
            return list(candidato)                      # achou: q triplas disjuntas
    return None                                         # nenhum candidato serviu
