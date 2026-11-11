"""
contador.py
===========
Contador de operações elementares para a análise de complexidade
POR CONTAGEM DE INSTRUÇÕES.

Convenção adotada (a mesma em todos os algoritmos, para que as contagens
sejam comparáveis):
    operação básica = examinar UMA tripla (ou par de estados) e testar se
    ela é compatível (disjunta) com o que já foi escolhido.

Cada algoritmo faz  cont.ops += 1  exatamente no ponto onde essa operação
básica acontece (o laço mais interno, que domina o custo).
"""


class Contador:
    __slots__ = ("ops",)

    def __init__(self):
        self.ops = 0

    def __repr__(self):
        return f"Contador(ops={self.ops})"
