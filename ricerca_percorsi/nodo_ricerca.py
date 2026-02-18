class NodoRicerca:
    """
    Rappresenta un nodo dell'albero di ricerca.

    Contiene:
    - stato: il valore associato al nodo (nel nostro caso, una stringa)
    - padre: riferimento al nodo precedente nel percorso
    - azione: non usata qui, ma mantenuta per generalità
    - costo_g: costo accumulato dalla radice fino a questo nodo
    """

    def __init__(self, stato, padre=None, azione=None, costo_g=0.0):
        self.stato = stato
        self.padre = padre
        self.azione = azione
        self.costo_g = costo_g

    def ricostruisci_percorso(self):
        """
        Ricostruisce il percorso dalla radice fino a questo nodo.
        """

        percorso = []
        nodo_corrente = self

        while nodo_corrente is not None:
            percorso.append(nodo_corrente.stato)
            nodo_corrente = nodo_corrente.padre

        percorso.reverse()
        return percorso
