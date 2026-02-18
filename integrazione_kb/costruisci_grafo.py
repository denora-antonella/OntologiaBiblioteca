def costruisci_grafo(ontologia):
    """
    Costruisce un grafo a partire dall'ontologia.
    Ogni individuo diventa un nodo e ogni object property genera un arco tra due nodi.
    """

    grafo = {}

    # Recupero tutte le object property definite nell'ontologia.
    # Saranno le relazioni che collegano i nodi del grafo.
    proprieta = list(ontologia.object_properties())

    # Funzione interna per aggiungere un arco al grafo.
    # Se l'arco esiste già, mantiene il costo più basso.
    def aggiungi_arco(sorgente, destinazione, costo):
        if sorgente not in grafo:
            grafo[sorgente] = {}
        if destinazione not in grafo:
            grafo[destinazione] = {}

        costo_vecchio = grafo[sorgente].get(destinazione)

        if costo_vecchio is None or costo < costo_vecchio:
            grafo[sorgente][destinazione] = float(costo)

    # Per ogni individuo dell'ontologia cerco le relazioni
    # che lo collegano ad altri individui.
    for individuo in ontologia.individuals():
        nome_sorgente = individuo.name

        for prop in proprieta:
            nome_prop = prop.name

            # Provo a leggere i valori associati alla property.
            # Se qualcosa va storto, ignoro e continuo.
            try:
                valori = getattr(individuo, nome_prop)
            except Exception:
                valori = []

            if not valori:
                continue

            for valore in valori:
                if valore is None:
                    continue

                nome_dest = valore.name

                # Costo base per ogni relazione.
                costo = 1.0

                # La relazione "sottoCategoriaDi" viene resa leggermente
                # più leggera per favorire percorsi tra categorie.
                if nome_prop == "sottoCategoriaDi":
                    costo = 0.5

                # Aggiungo l'arco in entrambe le direzioni
                # per garantire connettività nel grafo.
                aggiungi_arco(nome_sorgente, nome_dest, costo)
                aggiungi_arco(nome_dest, nome_sorgente, costo)

    return grafo
