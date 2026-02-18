from pathlib import Path
from collections import deque
from owlready2 import get_ontology

from integrazione_kb.costruisci_grafo import costruisci_grafo
from integrazione_kb.euristiche_biblioteca import euristica_informata_tassonomia

from ricerca_percorsi.problema_biblioteca import ProblemaBiblioteca
from ricerca_percorsi.algoritmo_a_stella import a_stella


# Carica il file OWL dell'ontologia.
# Restituisce l'ontologia oppure None se il file non esiste.
def carica_ontologia(percorso_file):
    percorso_file = Path(percorso_file)

    if not percorso_file.exists():
        print(f"Non riesco a trovare il file dell'ontologia in: {percorso_file}")
        print("Controlla che 'biblioteca.owl' sia presente nella cartella 'ontologia'.")
        return None

    ontologia = get_ontology(str(percorso_file.resolve())).load()
    return ontologia


# Euristica sempre nulla: A* si comporta come Dijkstra.
def euristica_nulla(_stato_corrente, _obiettivo):
    return 0.0


# Euristica semplice: 0 se siamo al goal, 1 altrimenti.
def euristica_base(stato_corrente, obiettivo):
    return 0.0 if stato_corrente == obiettivo else 1.0


# Normalizza l'output dell'algoritmo A*.
# Ci aspettiamo una tupla: (percorso, costo, nodi_espansi)
def normalizza_output_a_stella(risultato):
    if risultato is None:
        return None, None, None

    if isinstance(risultato, tuple):
        percorso = risultato[0] if len(risultato) > 0 else None
        costo = risultato[1] if len(risultato) > 1 else None
        espansi = risultato[2] if len(risultato) > 2 else None
        return percorso, costo, espansi

    return None, None, None


# Divide gli individui dell'ontologia in gruppi leggibili.
def raggruppa_nodi_per_tipo(ontologia):
    persone, libri, categorie, prestiti, altro = [], [], [], [], []

    for ind in ontologia.individuals():
        nome = ind.name
        basso = nome.lower()

        if basso.startswith("cat_"):
            categorie.append(nome)
        elif basso.startswith("prestito"):
            prestiti.append(nome)
        elif basso.startswith("libro"):
            libri.append(nome)
        else:
            persone.append(nome)

    persone.sort()
    libri.sort()
    categorie.sort()
    prestiti.sort()
    altro.sort()

    return {
        "Persone": persone,
        "Libri": libri,
        "Categorie": categorie,
        "Prestiti": prestiti,
        "Altro": altro
    }


# Costruisce il menu numerato per permettere la scelta dei nodi.
def costruisci_menu(ontologia):
    gruppi = raggruppa_nodi_per_tipo(ontologia)

    elenco = []
    for nome_gruppo in ["Persone", "Libri", "Categorie", "Prestiti", "Altro"]:
        for nodo in gruppi[nome_gruppo]:
            elenco.append((nome_gruppo, nodo))

    mappa = {}
    indice = 1
    righe = []
    ultimo_gruppo = None

    for gruppo, nodo in elenco:
        if gruppo != ultimo_gruppo:
            righe.append(f"\n{gruppo}:")
            ultimo_gruppo = gruppo

        righe.append(f"  {indice}. {nodo}")
        mappa[indice] = nodo
        indice += 1

    testo = "\n".join(righe).lstrip("\n")
    return testo, mappa


# Mostra il menu e gestisce l'input dell'utente.
def scegli_da_menu(titolo, testo_menu, mappa_scelte):
    print()
    print(titolo)
    print(testo_menu)

    while True:
        scelta = input("\nInserisci il numero corrispondente: ").strip()

        if not scelta.isdigit():
            print("Per favore inserisci un numero valido (es. 6).")
            continue

        numero = int(scelta)
        if numero not in mappa_scelte:
            print("Numero non presente nell'elenco. Riprova.")
            continue

        return mappa_scelte[numero]


# Restituisce alcuni nodi raggiungibili dalla partenza.
def calcola_raggiungibili(grafo, nodo_iniziale, limite=15):
    visitati = set([nodo_iniziale])
    coda = deque([nodo_iniziale])

    while coda and len(visitati) < limite:
        corrente = coda.popleft()

        for v in grafo.get(corrente, {}).keys():
            if v not in visitati:
                visitati.add(v)
                coda.append(v)

            if len(visitati) >= limite:
                break

    visitati.discard(nodo_iniziale)
    return sorted(list(visitati))


# Presenta il risultato della ricerca in modo chiaro.
def stampa_risultato(percorso, costo, nodi_espansi, nodo_iniziale, nodo_obiettivo, grafo):
    if not percorso:
        print("\nNon sono riuscito a trovare un collegamento tra i due nodi.")
        print(f"Nodo di partenza: {nodo_iniziale}")
        print(f"Nodo obiettivo:   {nodo_obiettivo}")

        suggeriti = calcola_raggiungibili(grafo, nodo_iniziale, limite=15)
        if suggeriti:
            print("\nAlcuni nodi raggiungibili dalla partenza sono:")
            for s in suggeriti:
                print(f"  - {s}")
        return

    print("\nHo trovato un possibile percorso tra i due nodi.")
    print(f"Partenza:  {nodo_iniziale}")
    print(f"Obiettivo: {nodo_obiettivo}")

    print("\nPassaggi individuati:")
    for i, nodo in enumerate(percorso, start=1):
        print(f"  {i}. {nodo}")

    print("\nPercorso completo:")
    print("  " + " → ".join(percorso))

    if costo is not None:
        print(f"\nCosto totale del percorso: {float(costo)}")

    if nodi_espansi is not None:
        print(f"Nodi esplorati durante la ricerca: {int(nodi_espansi)}")

    print("\nIl percorso segue le relazioni definite nell'ontologia (prestiti, libri e categorie).")


def main():
    print("Benvenuto nel sistema di esplorazione della Biblioteca.\n")
    print("Sto caricando l'ontologia e preparando la struttura per la ricerca...\n")

    percorso_owl = Path("ontologia") / "biblioteca.owl"
    ontologia = carica_ontologia(percorso_owl)
    if ontologia is None:
        return

    print("Ontologia caricata correttamente.")
    print("Costruisco il grafo delle relazioni...\n")

    grafo = costruisci_grafo(ontologia)

    testo_menu, mappa_scelte = costruisci_menu(ontologia)

    nodo_iniziale = scegli_da_menu("Scegli il nodo di partenza:", testo_menu, mappa_scelte)
    print(f"\nHai scelto come punto di partenza: {nodo_iniziale}")

    nodo_obiettivo = scegli_da_menu("Scegli il nodo obiettivo:", testo_menu, mappa_scelte)
    print(f"Hai scelto come obiettivo: {nodo_obiettivo}")

    print("\nScegli la strategia di ricerca:")
    print("  1) nulla (A* = Dijkstra)")
    print("  2) base (0 se goal, 1 altrimenti)")
    print("  3) informata (usa tassonomia sottoCategoriaDi)")

    scelta_h = input("Inserisci 1, 2 oppure 3: ").strip()

    goal_e_categoria = nodo_obiettivo.startswith("cat_")

    if scelta_h == "1":
        nome_h = "nessuna"
        funzione_h = lambda s: euristica_nulla(s, nodo_obiettivo)

    elif scelta_h == "2":
        nome_h = "base"
        funzione_h = lambda s: euristica_base(s, nodo_obiettivo)

    else:
        if not goal_e_categoria:
            print("\nL'euristica informata è applicabile solo se l'obiettivo è una categoria.")
            print("In questo caso utilizzo automaticamente l'euristica base.")
            nome_h = "base"
            funzione_h = lambda s: euristica_base(s, nodo_obiettivo)
        else:
            nome_h = "informata"
            funzione_h = lambda s: euristica_informata_tassonomia(grafo, s, nodo_obiettivo)

    print(f"\nCerco un percorso da '{nodo_iniziale}' a '{nodo_obiettivo}'.")
    print(f"Euristica selezionata: {nome_h}")
    print("Avvio la ricerca...\n")

    problema = ProblemaBiblioteca(grafo, nodo_iniziale, {nodo_obiettivo})
    risultato = a_stella(problema, funzione_h)

    percorso, costo, nodi_espansi = normalizza_output_a_stella(risultato)
    stampa_risultato(percorso, costo, nodi_espansi, nodo_iniziale, nodo_obiettivo, grafo)


if __name__ == "__main__":
    main()
