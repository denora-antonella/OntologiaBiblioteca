import heapq
from ricerca_percorsi.nodo_ricerca import NodoRicerca


def a_stella(problema, euristica):
    """
    Implementazione dell'algoritmo A*.

    Restituisce sempre una terna:
      (percorso, costo_totale, nodi_espansi)

    - percorso: lista di stati trovati (oppure None se non esiste soluzione)
    - costo_totale: costo del percorso (oppure None)
    - nodi_espansi: numero di nodi realmente esplorati
    """

    # Stato di partenza del problema
    stato_iniziale = problema.stato_iniziale()
    nodo_iniziale = NodoRicerca(
        stato=stato_iniziale,
        padre=None,
        azione=None,
        costo_g=0.0
    )

    # Frontiera gestita come coda di priorità (min-heap)
    frontiera = []
    contatore = 0  # serve solo a evitare conflitti tra nodi con stesso f

    f_iniziale = nodo_iniziale.costo_g + float(euristica(nodo_iniziale.stato))
    heapq.heappush(frontiera, (f_iniziale, contatore, nodo_iniziale))

    # Tiene traccia del miglior costo noto per ogni stato
    migliori_costi = {stato_iniziale: 0.0}

    nodi_espansi = 0

    while frontiera:
        _, _, nodo = heapq.heappop(frontiera)

        # Se ho già trovato un modo migliore per arrivare qui, ignoro questo nodo
        costo_conosciuto = migliori_costi.get(nodo.stato)
        if costo_conosciuto is not None and nodo.costo_g > costo_conosciuto:
            continue

        # Se ho raggiunto l'obiettivo, ricostruisco il percorso
        if problema.e_goal(nodo.stato):
            percorso = nodo.ricostruisci_percorso()
            return percorso, float(nodo.costo_g), nodi_espansi

        nodi_espansi += 1

        # Espando i successori
        for stato_successore, costo_arco in problema.successori(nodo.stato):

            nuovo_costo = nodo.costo_g + float(costo_arco)
            costo_migliore = migliori_costi.get(stato_successore)

            # Aggiorno solo se trovo un percorso migliore
            if costo_migliore is None or nuovo_costo < costo_migliore:
                migliori_costi[stato_successore] = nuovo_costo

                nuovo_nodo = NodoRicerca(
                    stato=stato_successore,
                    padre=nodo,
                    azione=None,
                    costo_g=nuovo_costo
                )

                contatore += 1
                f = nuovo_costo + float(euristica(stato_successore))

                heapq.heappush(frontiera, (f, contatore, nuovo_nodo))

    # Se esco dal ciclo, non esiste un percorso
    return None, None, nodi_espansi
