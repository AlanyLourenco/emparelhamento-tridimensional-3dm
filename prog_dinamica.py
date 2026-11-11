"""
prog_dinamica.py
================
Estratégia: PROGRAMAÇÃO DINÂMICA (sobre subconjuntos / bitmask).

Subproblema:
    D[i][(A, B)] = "é possível cobrir os elementos x_0, ..., x_{i-1} de X
                    usando exatamente os elementos A ⊆ Y e B ⊆ Z?"
    (A e B são representados como máscaras de bits; |A| = |B| = i.)

Recorrência:
    D[0][(∅, ∅)] = verdadeiro
    D[i+1][(A ∪ {y}, B ∪ {z})] = verdadeiro  se  D[i][(A, B)]  e
                                 (x_i, y, z) ∈ T  e  y ∉ A  e  z ∉ B

Resposta: D[q][(Y, Z)].

Por que é PD (e não força bruta): muitas escolhas parciais diferentes
levam ao MESMO estado (A, B) — subproblemas sobrepostos. A tabela guarda
cada estado UMA vez, eliminando a repetição.

Complexidade:
    - nº de estados na camada i: ≤ C(q, i)^2;  soma de todas: C(2q, q) ≈ 4^q / √(πq)
    - cada estado tenta as d_x triplas do próximo x
    - tempo: O(C(2q, q) · m/q) no pior caso   (exponencial, mas sem repetição)
    - espaço: O(C(2q, q)) — guarda as camadas para reconstruir a solução
    Só armazenamos os estados ALCANÇÁVEIS (dicionário), o que em instâncias
    esparsas é muito menos que o limite.
"""


def programacao_dinamica(inst, cont):
    """Retorna uma lista com q triplas formando emparelhamento perfeito, ou None."""
    q = inst.q

    opcoes = [[] for _ in range(q)]
    for (x, y, z) in inst.triplas:
        opcoes[x].append((y, z))
    if any(len(o) == 0 for o in opcoes):
        return None

    # camada[(A, B)] = (estado_anterior, tripla_usada)  -> permite reconstruir
    camada = {(0, 0): None}
    camadas = []

    for x in range(q):                          # i = x: processa x_0, x_1, ...
        nova = {}
        for (A, B) in camada:                   # cada estado alcançável
            for (y, z) in opcoes[x]:            # cada tripla de x
                cont.ops += 1                   # operação básica
                by, bz = 1 << y, 1 << z
                if not (A & by) and not (B & bz):
                    estado = (A | by, B | bz)
                    if estado not in nova:      # estado já resolvido? reaproveita
                        nova[estado] = ((A, B), (x, y, z))
        if not nova:                            # nenhum estado alcançável: NÃO
            return None
        camadas.append(nova)
        camada = nova

    cheio = (1 << q) - 1
    estado = (cheio, cheio)
    if q > 0 and estado not in camada:
        return None

    # Reconstrução da solução seguindo os ponteiros de trás para frente
    M = []
    for i in range(q - 1, -1, -1):
        anterior, tripla = camadas[i][estado]
        M.append(tripla)
        estado = anterior
    M.reverse()
    return M
