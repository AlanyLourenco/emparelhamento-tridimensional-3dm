"""
guloso.py
=========
Estratégia: ALGORITMO GULOSO.

Critério guloso: a cada passo escolhe a tripla cujos elementos são os
MAIS RESTRITOS, isto é, a de menor  grau(x) + grau(y) + grau(z), onde grau
é o nº de triplas ainda disponíveis que contêm o elemento. Intuição:
elemento com poucas opções precisa ser atendido logo, senão fica sem par.

Depois de escolher, remove todas as triplas que conflitam com a escolhida
e atualiza os graus. Repete até não sobrar tripla.

Propriedades:
    - Sempre devolve um emparelhamento MAXIMAL (não dá para acrescentar
      nenhuma tripla). Todo emparelhamento maximal tem tamanho ≥ ótimo/3,
      então o guloso é uma 3-aproximação para o 3DM de otimização.
    - Para a versão de decisão ele é INCOMPLETO: se devolve q triplas a
      resposta é SIM com certeza; se devolve menos, a resposta real pode
      ainda ser SIM (falso negativo).

Complexidade:
    - cada rodada: O(m) para achar o mínimo + O(m) para filtrar
    - no máximo q rodadas
    - tempo: O(q · m);  espaço: O(m + q)
"""


def guloso(inst, cont):
    """Retorna um emparelhamento maximal (lista de triplas, tamanho ≤ q)."""
    q = inst.q
    restantes = list(dict.fromkeys(inst.triplas))

    grauX, grauY, grauZ = [0] * q, [0] * q, [0] * q
    for (x, y, z) in restantes:
        grauX[x] += 1
        grauY[y] += 1
        grauZ[z] += 1

    M = []
    while restantes:
        # 1) escolha gulosa: tripla de menor soma de graus
        melhor, melhor_valor = None, None
        for t in restantes:
            cont.ops += 1                                 # operação básica
            v = grauX[t[0]] + grauY[t[1]] + grauZ[t[2]]
            if melhor_valor is None or v < melhor_valor:
                melhor, melhor_valor = t, v
        M.append(melhor)

        # 2) remove triplas em conflito e atualiza os graus
        bx, by, bz = melhor
        novas = []
        for t in restantes:
            cont.ops += 1                                 # operação básica
            if t[0] == bx or t[1] == by or t[2] == bz:
                grauX[t[0]] -= 1
                grauY[t[1]] -= 1
                grauZ[t[2]] -= 1
            else:
                novas.append(t)
        restantes = novas
    return M
