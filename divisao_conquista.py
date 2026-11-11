"""
divisao_conquista.py
====================
Estratégia: DIVISÃO E CONQUISTA (variante "meet-in-the-middle").

O 3DM não se divide naturalmente em subproblemas INDEPENDENTES: o que
uma metade escolhe restringe a outra (compartilham Y e Z). Por isso não há
um D&C polinomial (se houvesse, P = NP). A forma possível é:

    DIVIDIR   : separa X em duas metades  X_esq = [lo, meio)  e  X_dir = [meio, hi).
    CONQUISTAR: para cada metade, calcula recursivamente TODOS os
                "perfis" possíveis: pares (máscaraY, máscaraZ) indicando quais
                elementos de Y e Z ficam usados ao cobrir aquela metade de X.
    COMBINAR  : junta um perfil da esquerda com um da direita quando as
                máscaras são disjuntas (nenhum y ou z repetido).

Na raiz, a combinação é feita por busca do COMPLEMENTO:
    para cada perfil (a, b) da esquerda, procura (~a, ~b) na direita
    (tabela hash) em O(1), em vez de testar todos os pares.

Complexidade (D = maior nº de triplas que contém um mesmo x):
    - Seja P(k) o nº de perfis de um bloco com k elementos de X:
      P(k) ≤ D^k  e também  P(k) ≤ C(q, k)^2.
    - Nó interno de tamanho k: combina P(k/2) · P(k/2) ≤ D^k pares.
    - Raiz: só P(q/2) ≤ D^(q/2) buscas O(1) do complemento.
    - Os dois filhos da raiz dominam:  T(q) = O(q · D^(q/2))
      (a raiz quadrada de D^q, o custo da busca exaustiva: "meet-in-the-middle").
    - Espaço: O(q · D^(q/2)) — perfis guardados com suas triplas.
"""


def divisao_conquista(inst, cont):
    """Retorna uma lista com q triplas formando emparelhamento perfeito, ou None."""
    q = inst.q
    if q == 0:
        return []

    opcoes = [[] for _ in range(q)]
    for (x, y, z) in inst.triplas:
        opcoes[x].append((y, z))
    if any(len(o) == 0 for o in opcoes):
        return None

    def resolver(lo, hi):
        """
        Retorna dict {(mascY, mascZ): lista_de_triplas} com um emparelhamento
        para cada perfil possível que cobre exatamente os x em [lo, hi).
        """
        # Caso base: um único x -> cada tripla dele é um perfil
        if hi - lo == 1:
            perfis = {}
            for (y, z) in opcoes[lo]:
                cont.ops += 1
                perfis[(1 << y, 1 << z)] = [(lo, y, z)]
            return perfis

        meio = (lo + hi) // 2
        esq = resolver(lo, meio)           # conquista metade esquerda
        if not esq:
            return {}
        dir_ = resolver(meio, hi)          # conquista metade direita
        if not dir_:
            return {}

        # Combinação: todos os pares de perfis compatíveis
        combinados = {}
        for (ay, az), m_esq in esq.items():
            for (by, bz), m_dir in dir_.items():
                cont.ops += 1                                  # operação básica
                if not (ay & by) and not (az & bz):            # disjuntos?
                    chave = (ay | by, az | bz)
                    if chave not in combinados:
                        combinados[chave] = m_esq + m_dir
        return combinados

    if q == 1:
        perfis = resolver(0, 1)
        return perfis.get((1, 1))

    # Raiz: divide e combina por busca do complemento (O(1) por perfil)
    meio = q // 2
    esq = resolver(0, meio)
    if not esq:
        return None
    dir_ = resolver(meio, q)
    cheio = (1 << q) - 1
    for (ay, az), m_esq in esq.items():
        cont.ops += 1
        m_dir = dir_.get((cheio ^ ay, cheio ^ az))
        if m_dir is not None:
            return m_esq + m_dir
    return None
