"""
instancia.py
============
Representação de instâncias do Emparelhamento Tridimensional (3DM),
geradores de instâncias, leitura/gravação em arquivo e o VERIFICADOR
de certificado usado na prova de que 3DM pertence a NP.

Definição do problema (versão de decisão):
    Dados três conjuntos disjuntos X, Y e Z, cada um com q elementos, e um
    conjunto de triplas T ⊆ X × Y × Z, existe M ⊆ T com |M| = q tal que
    nenhum par de triplas de M compartilha uma coordenada?
    (Ou seja, M cobre cada elemento de X ∪ Y ∪ Z exatamente uma vez.)

Representação adotada:
    X = Y = Z = {0, 1, ..., q-1} como RÓTULOS. Os conjuntos continuam
    sendo disjuntos: o elemento "3" de X é diferente do elemento "3" de Y,
    pois a posição na tripla (x, y, z) indica a qual conjunto ele pertence.
"""

import random
from dataclasses import dataclass


@dataclass
class Instancia:
    """Uma instância do 3DM: q e a lista de triplas T (sem repetição)."""
    q: int
    triplas: list          # lista de tuplas (x, y, z)
    nome: str = ""

    @property
    def m(self):
        """Número de triplas |T|."""
        return len(self.triplas)


# ---------------------------------------------------------------------------
# Geradores de instâncias
# ---------------------------------------------------------------------------

def gerar_com_solucao(q, extras, semente=None):
    """
    Gera uma instância que TEM emparelhamento perfeito ("solução plantada").

    1. Sorteia duas permutações py e pz de {0..q-1};
       as triplas (x, py[x], pz[x]) formam um emparelhamento perfeito.
    2. Acrescenta 'extras' triplas aleatórias (ruído) para esconder a solução.
    3. Embaralha a lista para que a solução não apareça em ordem.
    """
    rng = random.Random(semente)
    py = list(range(q))
    pz = list(range(q))
    rng.shuffle(py)
    rng.shuffle(pz)

    T = {(x, py[x], pz[x]) for x in range(q)}
    total = min(q ** 3, q + extras)          # não pode passar de |X×Y×Z|
    while len(T) < total:
        T.add((rng.randrange(q), rng.randrange(q), rng.randrange(q)))

    T = list(T)
    rng.shuffle(T)
    return Instancia(q, T, f"plantada_q{q}_m{len(T)}")


def gerar_aleatoria(q, m, semente=None):
    """
    Gera uma instância aleatória com m triplas em que TODO elemento de
    X, Y e Z aparece em pelo menos uma tripla (para que a instância não seja
    rejeitada trivialmente). Nenhuma solução é plantada: pode ter ou não.
    """
    rng = random.Random(semente)
    m = min(max(m, 3 * q), q ** 3)
    T = set()
    for i in range(q):                     # garante cobertura de cada elemento
        T.add((i, rng.randrange(q), rng.randrange(q)))
        T.add((rng.randrange(q), i, rng.randrange(q)))
        T.add((rng.randrange(q), rng.randrange(q), i))
    while len(T) < m:
        T.add((rng.randrange(q), rng.randrange(q), rng.randrange(q)))
    T = list(T)
    rng.shuffle(T)
    return Instancia(q, T, f"aleatoria_q{q}_m{m}")


# ---------------------------------------------------------------------------
# Leitura e gravação em arquivo texto
#   Formato:  primeira linha "q m"; depois m linhas "x y z".
# ---------------------------------------------------------------------------

def ler_arquivo(caminho):
    with open(caminho, encoding="utf-8") as f:
        linhas = [l.split() for l in f if l.strip() and not l.startswith("#")]
    q, m = int(linhas[0][0]), int(linhas[0][1])
    T = [tuple(int(v) for v in l) for l in linhas[1:1 + m]]
    for (x, y, z) in T:
        if not (0 <= x < q and 0 <= y < q and 0 <= z < q):
            raise ValueError(f"tripla fora do intervalo: {(x, y, z)}")
    return Instancia(q, list(dict.fromkeys(T)), caminho)   # remove repetidas


def salvar_arquivo(inst, caminho):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"{inst.q} {inst.m}\n")
        for (x, y, z) in inst.triplas:
            f.write(f"{x} {y} {z}\n")


# ---------------------------------------------------------------------------
# Verificador de certificado  (base da prova de que 3DM ∈ NP)
# ---------------------------------------------------------------------------

def verificar_certificado(inst, M):
    """
    Verifica, em tempo polinomial, se M é um emparelhamento perfeito de inst.

    Passos e custo:
      (1) |M| == q                                   O(1)
      (2) monta conjunto de T para busca             O(m)
      (3) para cada tripla de M:                     q iterações
            - pertence a T?                          O(1) esperado (hash)
            - x, y ou z já usado?                    O(1)
    Total: O(m + q)  — polinomial no tamanho da entrada.
    """
    q = inst.q
    if len(M) != q:                                  # (1)
        return False
    conjunto_T = set(inst.triplas)                   # (2)
    usadoX = [False] * q
    usadoY = [False] * q
    usadoZ = [False] * q
    for (x, y, z) in M:                              # (3)
        if (x, y, z) not in conjunto_T:
            return False
        if usadoX[x] or usadoY[y] or usadoZ[z]:
            return False
        usadoX[x] = usadoY[y] = usadoZ[z] = True
    return True                                      # cobre tudo exatamente 1 vez


def eh_emparelhamento(inst, M):
    """Verifica se M é um emparelhamento VÁLIDO (não necessariamente perfeito):
    triplas de T, duas a duas disjuntas. Usado para checar guloso/aproximado."""
    conjunto_T = set(inst.triplas)
    vistos = set()
    for (x, y, z) in M:
        if (x, y, z) not in conjunto_T:
            return False
        for elem in (("X", x), ("Y", y), ("Z", z)):
            if elem in vistos:
                return False
            vistos.add(elem)
    return True
