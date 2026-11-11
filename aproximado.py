"""
aproximado.py
=============
Estratégia: ALGORITMO APROXIMADO / HEURÍSTICA DE BUSCA LOCAL.

Versão de otimização associada: encontrar um emparelhamento de tamanho
MÁXIMO. Se o máximo tiver tamanho q, a resposta da decisão é SIM.

Algoritmo em duas fases:

  Fase 1 — Solução inicial MAXIMAL (garantia: 3-aproximação):
      Qualquer emparelhamento maximal tem |M| ≥ OPT / 3: toda tripla do
      ótimo conflita com alguma escolhida, e cada escolhida bloqueia no
      máximo 3 triplas do ótimo (uma por coordenada).
      - emparelhamento_maximal(): versão mais simples, ordem arbitrária, O(m).
      - busca_local() usa a solução do GULOSO (também maximal, e em geral
        melhor), de modo que o resultado final é sempre ≥ o do guloso.

  Fase 2 — Busca local com trocas "1 sai, 2 entram"
  (ideia de Hurkens & Schrijver, 1989, para k-set packing):
      (a) se existe tripla livre (sem conflito com M), adiciona;
      (b) senão, para cada s ∈ M procura duas triplas t1, t2, disjuntas
          entre si, que só conflitam com s. Troca s por {t1, t2}: |M| + 1.
      Repete até não haver melhoria. No ótimo local dessa vizinhança
      vale |M| ≥ OPT / 2 para k = 3  (razão (k+1)/2).

Complexidade:
    - Fase 1: O(m) (maximal simples) ou O(q · m) (guloso)
    - Cada melhoria aumenta |M| em 1  =>  no máximo q melhorias.
    - Cada busca por melhoria: O(m) para classificar as triplas pelos
      conflitos + O(Σ c_s²) para procurar pares (c_s = candidatas de s).
    - Tempo: O(q · (m + Σ c_s²)) ≤ O(q · m²);  espaço: O(m + q).
"""

from guloso import guloso


def emparelhamento_maximal(inst, cont):
    """3-aproximação simples: aceita cada tripla que não conflita com as anteriores."""
    q = inst.q
    usadoX, usadoY, usadoZ = [False] * q, [False] * q, [False] * q
    M = []
    for (x, y, z) in inst.triplas:
        cont.ops += 1
        if not usadoX[x] and not usadoY[y] and not usadoZ[z]:
            usadoX[x] = usadoY[y] = usadoZ[z] = True
            M.append((x, y, z))
    return M


def _procura_melhoria(T, M, q, cont):
    """
    Procura uma melhoria local em M. Retorna o novo M (com uma tripla a mais)
    ou None se M é um ótimo local.
    """
    # dono[*][e] = índice em M da tripla que cobre o elemento e (ou -1)
    donoX, donoY, donoZ = [-1] * q, [-1] * q, [-1] * q
    for i, (x, y, z) in enumerate(M):
        donoX[x] = donoY[y] = donoZ[z] = i
    em_M = set(M)

    candidatas = [[] for _ in range(len(M))]   # triplas que só conflitam com M[i]
    for t in T:
        cont.ops += 1                          # operação básica
        if t in em_M:
            continue
        conflitos = {donoX[t[0]], donoY[t[1]], donoZ[t[2]]} - {-1}
        if not conflitos:                      # (a) tripla livre: adiciona
            return M + [t]
        if len(conflitos) == 1:
            candidatas[conflitos.pop()].append(t)

    # (b) troca 1 -> 2
    for i, cands in enumerate(candidatas):
        for a in range(len(cands)):
            t1 = cands[a]
            for b in range(a + 1, len(cands)):
                t2 = cands[b]
                cont.ops += 1                  # operação básica
                if t1[0] != t2[0] and t1[1] != t2[1] and t1[2] != t2[2]:
                    return M[:i] + M[i + 1:] + [t1, t2]
    return None


def busca_local(inst, cont):
    """Retorna um emparelhamento (lista de triplas) de tamanho ≥ OPT/2."""
    q = inst.q
    T = list(dict.fromkeys(inst.triplas))
    M = guloso(inst, cont)                       # Fase 1 (solução maximal)
    while len(M) < q:                            # Fase 2
        novo = _procura_melhoria(T, M, q, cont)
        if novo is None:
            break                                # ótimo local
        M = novo
    return M
