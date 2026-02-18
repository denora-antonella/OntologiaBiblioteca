from __future__ import annotations
from typing import Dict, Iterable, Set, Tuple


class ProblemaBiblioteca:
    """
    Incapsula il problema di ricerca sulla biblioteca.

    Il grafo rappresenta la knowledge base già trasformata.
    Gli stati sono semplicemente stringhe (nomi degli individui).
    """

    def __init__(
        self,
        grafo: Dict[str, Dict[str, float]],
        nodo_iniziale: str,
        obiettivi: Set[str]
    ):

        # Salvo il grafo costruito a partire dall'ontologia
        self.grafo = grafo

        # Stato iniziale della ricerca
        self.nodo_iniziale = str(nodo_iniziale)

        # Insieme degli stati obiettivo
        self.obiettivi = set(str(o) for o in obiettivi)

    def stato_iniziale(self) -> str:
        """
        Restituisce lo stato di partenza.
        """
        return self.nodo_iniziale

    def e_goal(self, stato: str) -> bool:
        """
        Verifica se lo stato corrente è uno degli obiettivi.
        """
        return str(stato) in self.obiettivi

    def successori(self, stato: str) -> Iterable[Tuple[str, float]]:
        """
        Restituisce i successori di uno stato insieme al costo dell'arco.
        """

        vicini = self.grafo.get(str(stato), {})

        for vicino, costo in vicini.items():
            yield str(vicino), float(costo)
