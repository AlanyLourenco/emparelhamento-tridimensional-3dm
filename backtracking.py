"""
backtracking.py
===============
Estratégia: BACKTRACKING.

Ideia: todo elemento de X ∪ Y ∪ Z precisa estar em exatamente uma tripla.
A cada nível da recursão escolhemos UM elemento ainda descoberto e
ramificamos sobre as triplas compatíveis que o cobrem. Quando uma escolha
leva a um beco sem saída, ela é desfeita (backtrack) e tenta-se a próxima.

Podas/heurísticas usadas:
    1. Pré-teste: se algum elemento de X, Y ou Z não aparece em nenhuma
       tripla, a resposta é NÃO imediatamente.
    2. Ordem MRV DINÂMICA ("minimum remaining values"): em cada nó escolhe,
       entre os elementos descobertos de X, Y e Z, aquele com MENOS triplas
       ainda compatíveis. Conflitos aparecem cedo e a árvore fica menor.
    3. Verificação adiante (forward checking): se algum elemento descoberto
       ficou com zero triplas compatíveis, o ramo é podado na hora.

Complexidade:
    - a árvore tem altura q; no nível k (k elementos já cobertos) ramifica
      sobre o elemento de menor grau, e esse grau é ≤ m/(q-k) (média dos
      graus dos q-k elementos descobertos de X). Logo o nº de nós é
      ≤ ∏ m/(q-k) = m^q / q!, e cada nó custa O(m) para recalcular graus.
    - pior caso: O(m^(q+1) / q!)  -> exponencial
    - na prática muito menor que a força bruta por causa das podas
    - espaço: O(q · m)  (cada um dos ≤ q níveis da recursão guarda a sua
      lista de triplas livres, O(m), e os graus, O(q))

Este arquivo também traz  maior_emparelhamento(), um branch-and-bound que
calcula o TAMANHO MÁXIMO de um emparelhamento (versão de otimização). Ele é
usado apenas no benchmark, para medir a razão de aproximação real das
heurísticas (|M| / OPT).
"""

import sys


def backtracking(inst, cont):
    """Retorna uma lista com q triplas formando emparelhamento perfeito, ou None."""
    q = inst.q
    sys.setrecursionlimit(max(1000, 4 * q + 100))
    T = list(dict.fromkeys(inst.triplas))

    # Poda 1: algum elemento que não aparece em nenhuma tripla => impossível
    for c in range(3):
        if len({t[c] for t in T}) < q:
            return None

    usado = [[False] * q for _ in range(3)]      # usado[c][e]: e da coordenada c coberto
    escolha = []

    def tenta(cobertos):
        if cobertos == q:                         # X, Y e Z inteiramente cobertos
            return True

        # Triplas ainda compatíveis com o que já foi escolhido
        livres = []
        grau = [[0] * q for _ in range(3)]
        for t in T:
            cont.ops += 1                         # operação básica
            if not usado[0][t[0]] and not usado[1][t[1]] and not usado[2][t[2]]:
                livres.append(t)
                grau[0][t[0]] += 1
                grau[1][t[1]] += 1
                grau[2][t[2]] += 1

        # Poda 2 + 3: elemento descoberto mais restrito (MRV); grau 0 => poda
        melhor_c, melhor_e, melhor_g = -1, -1, None
        for c in range(3):
            for e in range(q):
                if not usado[c][e]:
                    g = grau[c][e]
                    if g == 0:
                        return False              # forward checking: ramo morto
                    if melhor_g is None or g < melhor_g:
                        melhor_c, melhor_e, melhor_g = c, e, g

        for t in livres:
            if t[melhor_c] != melhor_e:
                continue
            usado[0][t[0]] = usado[1][t[1]] = usado[2][t[2]] = True   # escolhe
            escolha.append(t)
            if tenta(cobertos + 1):
                return True
            escolha.pop()                                              # desfaz
            usado[0][t[0]] = usado[1][t[1]] = usado[2][t[2]] = False
        return False

    return list(escolha) if tenta(0) else None


def maior_emparelhamento(inst):
    """
    Branch-and-bound para a versão de OTIMIZAÇÃO: devolve o tamanho máximo
    de um emparelhamento (triplas duas a duas disjuntas). Para cada x de X,
    decide entre "x fica descoberto" ou "x é coberto pela tripla t".
    Limitante: |M atual| + (nº de x restantes) ≤ melhor  =>  poda.
    Uso: só no benchmark (q pequeno), para calcular OPT.
    """
    q = inst.q
    opcoes = [[] for _ in range(q)]
    for (x, y, z) in dict.fromkeys(inst.triplas):
        opcoes[x].append((y, z))
    ordem = sorted(range(q), key=lambda x: len(opcoes[x]))
    usadoY, usadoZ = [False] * q, [False] * q
    melhor = [0]

    def rec(i, tam):
        if tam + (q - i) <= melhor[0]:
            return
        if i == q:
            melhor[0] = tam
            return
        x = ordem[i]
        for (y, z) in opcoes[x]:
            if not usadoY[y] and not usadoZ[z]:
                usadoY[y] = usadoZ[z] = True
                rec(i + 1, tam + 1)
                usadoY[y] = usadoZ[z] = False
                if melhor[0] == q:
                    return
        rec(i + 1, tam)                           # x fica descoberto

    rec(0, 0)
    return melhor[0]
