import csv
import json
import time
from collections import deque
from pathlib import Path

from owlready2 import get_ontology

from integrazione_kb.costruisci_grafo import costruisci_grafo
from ricerca_percorsi.problema_biblioteca import ProblemaBiblioteca
from ricerca_percorsi.algoritmo_a_stella import a_stella


def carica_ontologia(percorso_owl: Path):
    """
    Carica l'ontologia OWL dal percorso indicato.
    """
    return get_ontology(str(percorso_owl.resolve())).load()


def euristica_nulla(_stato, _obiettivo, _distanze=None):
    return 0.0


def euristica_base(stato, obiettivo, _distanze=None):
    return 0.0 if stato == obiettivo else 1.0


def costruisci_distanze_bfs(grafo, nodi_interesse):
    """
    Precalcola le distanze minime tra alcuni nodi,
    usando una semplice BFS a costo uniforme.
    """

    distanze = {}

    for sorgente in nodi_interesse:
        dist_sorg = {sorgente: 0}
        coda = deque([sorgente])

        while coda:
            corrente = coda.popleft()
            passi = dist_sorg[corrente]

            for vicino in grafo.get(corrente, {}).keys():
                if vicino not in dist_sorg:
                    dist_sorg[vicino] = passi + 1
                    coda.append(vicino)

        distanze[sorgente] = dist_sorg

    return distanze


def euristica_informata(stato, obiettivo, distanze_bfs):
    """
    Euristica informata basata sulle distanze minime BFS.
    Se non abbiamo informazioni sufficienti, usa una stima prudente.
    """

    if stato == obiettivo:
        return 0.0

    d = distanze_bfs.get(stato, {}).get(obiettivo)
    return float(d) if d is not None else 1.0


def scegli_funzione_euristica(nome, obiettivo, distanze_bfs):

    if nome == "nulla":
        return lambda s: euristica_nulla(s, obiettivo, distanze_bfs)

    if nome == "base":
        return lambda s: euristica_base(s, obiettivo, distanze_bfs)

    if nome == "informata":
        return lambda s: euristica_informata(s, obiettivo, distanze_bfs)

    return lambda s: euristica_base(s, obiettivo, distanze_bfs)


def esegui_singolo_test(grafo, nodo_iniziale, nodo_obiettivo, nome_euristica, distanze_bfs):

    funzione_h = scegli_funzione_euristica(nome_euristica, nodo_obiettivo, distanze_bfs)
    problema = ProblemaBiblioteca(grafo, nodo_iniziale, {nodo_obiettivo})

    t0 = time.perf_counter()
    percorso, costo, nodi_espansi = a_stella(problema, funzione_h)
    t1 = time.perf_counter()

    trovato = percorso is not None
    lunghezza = len(percorso) if trovato else None
    tempo_ms = (t1 - t0) * 1000.0
    percorso_str = " -> ".join(percorso) if trovato else None

    return {
        "nodo_iniziale": nodo_iniziale,
        "nodo_obiettivo": nodo_obiettivo,
        "euristica": nome_euristica,
        "trovato": bool(trovato),
        "costo": float(costo) if costo is not None else None,
        "lunghezza_percorso": int(lunghezza) if lunghezza is not None else None,
        "tempo_ms": float(tempo_ms),
        "nodi_espansi": int(nodi_espansi),
        "percorso": percorso_str
    }


def main():

    print("\nAvvio la fase di valutazione sperimentale...\n")

    cartella_progetto = Path(__file__).resolve().parent.parent
    percorso_owl = cartella_progetto / "ontologia" / "biblioteca.owl"

    ontologia = carica_ontologia(percorso_owl)
    grafo = costruisci_grafo(ontologia)

    # Casi scelti per testare situazioni diverse
    casi = [
        ("Anna", "LibroGaribaldi"),
        ("Marco", "LibroAI"),
        ("Marco", "cat_AlgebraLineare"),
        ("ProfRossi", "cat_StoriaItalia"),
        ("LibroAI", "cat_Biblioteca"),
        ("LibroAI", "cat_Fiabe"),
    ]

    euristiche = ["nulla", "base", "informata"]
    ripetizioni = 6

    nodi_interesse = {n for caso in casi for n in caso}
    distanze_bfs = costruisci_distanze_bfs(grafo, nodi_interesse)

    risultati = []
    id_esperimento = 1

    for start, goal in casi:
        for eur in euristiche:
            for _ in range(ripetizioni):
                r = esegui_singolo_test(grafo, start, goal, eur, distanze_bfs)
                r["id_esperimento"] = id_esperimento
                id_esperimento += 1
                risultati.append(r)

    cartella_out = cartella_progetto / "valutazione_sperimentale" / "risultati"
    cartella_out.mkdir(parents=True, exist_ok=True)

    csv_path = cartella_out / "risultati.csv"
    json_path = cartella_out / "risultati.json"

    colonne = list(risultati[0].keys())

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colonne)
        w.writeheader()
        for r in risultati:
            w.writerow(r)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(risultati, f, indent=2, ensure_ascii=False)

    print(f"Ho completato {len(risultati)} esecuzioni.")
    print("Risultati salvati in:")
    print(" -", csv_path)
    print(" -", json_path)
    print("\nOra puoi generare grafici e report.\n")


if __name__ == "__main__":
    main()
