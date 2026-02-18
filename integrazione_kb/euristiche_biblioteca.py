from collections import deque


def _bfs_distanze(grafo, sorgenti, max_passi=25, filtro_nodo=None):
    """
    Esegue una BFS multi-sorgente e calcola la distanza minima
    (in numero di archi) dai nodi sorgente.

    Se viene fornito un filtro_nodo, la visita considera solo
    i nodi per cui filtro_nodo(nodo) restituisce True.
    """
    dist = {}
    coda = deque()

    for s in sorgenti:
        if s is None:
            continue
        if filtro_nodo is not None and not filtro_nodo(s):
            continue
        dist[s] = 0
        coda.append(s)

    while coda:
        corrente = coda.popleft()
        passi = dist[corrente]

        if passi >= max_passi:
            continue

        vicini = grafo.get(corrente, {})
        for v in vicini.keys():
            if filtro_nodo is not None and not filtro_nodo(v):
                continue
            if v not in dist:
                dist[v] = passi + 1
                coda.append(v)

    return dist


# Funzioni di supporto per riconoscere il tipo di nodo
def _e_categoria(nome):
    return isinstance(nome, str) and nome.lower().startswith("cat_")


def _e_libro(nome):
    return isinstance(nome, str) and nome.lower().startswith("libro")


def _e_prestito(nome):
    return isinstance(nome, str) and nome.lower().startswith("prestito")


def _e_persona(nome):
    if not isinstance(nome, str):
        return False
    basso = nome.lower()
    return (
        not basso.startswith("cat_")
        and not basso.startswith("libro")
        and not basso.startswith("prestito")
    )


def euristica_informata_tassonomia(grafo, stato_corrente, obiettivo):
    """
    Euristica pensata per quando l'obiettivo è una categoria

    Per stimare la distanza sfruttando la struttura della KB:
    - Libro -> Categoria
    - Categoria -> Categoria (tassonomia)
    - Prestito -> Libro -> Categoria
    - Persona -> Prestito -> Libro -> Categoria

    Se non è possibile stimare in modo sensato, viene restituito
    un valore costante di fallback.
    """

    # Se siamo già al goal, la distanza stimata è zero.
    if stato_corrente == obiettivo:
        return 0.0

    # Se l'obiettivo non è una categoria,
    # questa euristica non è adatta: uso stima semplice.
    if not _e_categoria(obiettivo):
        return 1.0

    # Caso 1: siamo già su una categoria.
    # Cerco la distanza nella tassonomia.
    if _e_categoria(stato_corrente):
        dist = _bfs_distanze(
            grafo,
            [stato_corrente],
            max_passi=30,
            filtro_nodo=_e_categoria
        )

        if obiettivo in dist:
            return float(dist[obiettivo])

        return 2.0

    # Caso 2: siamo su un libro.
    # Provo a raggiungere una categoria e poi salire nella tassonomia.
    if _e_libro(stato_corrente):
        dist_libro = _bfs_distanze(
            grafo,
            [stato_corrente],
            max_passi=3,
            filtro_nodo=lambda x: _e_categoria(x) or _e_libro(x)
        )

        categorie = [n for n in dist_libro.keys() if _e_categoria(n)]
        if not categorie:
            return 2.0

        best = None
        for c in categorie:
            dist_cat = _bfs_distanze(
                grafo,
                [c],
                max_passi=30,
                filtro_nodo=_e_categoria
            )

            if obiettivo in dist_cat:
                valore = dist_libro[c] + dist_cat[obiettivo]
                if best is None or valore < best:
                    best = valore

        return float(best) if best is not None else 2.0

    # Caso 3: siamo su un prestito.
    # Passo prima al libro, poi applico la stessa logica.
    if _e_prestito(stato_corrente):
        dist_prestito = _bfs_distanze(
            grafo,
            [stato_corrente],
            max_passi=4,
            filtro_nodo=lambda x: _e_libro(x) or _e_categoria(x) or _e_prestito(x)
        )

        libri = [n for n in dist_prestito.keys() if _e_libro(n)]

        best = None
        for libro in libri:
            h_libro = euristica_informata_tassonomia(grafo, libro, obiettivo)
            valore = dist_prestito[libro] + h_libro

            if best is None or valore < best:
                best = valore

        return float(best) if best is not None else 3.0

    # Caso 4: siamo su una persona.
    # Passo ai prestiti, poi ai libri e infine alle categorie.
    if _e_persona(stato_corrente):
        dist_persona = _bfs_distanze(
            grafo,
            [stato_corrente],
            max_passi=3,
            filtro_nodo=lambda x: _e_prestito(x) or _e_persona(x)
        )

        prestiti = [n for n in dist_persona.keys() if _e_prestito(n)]

        best = None
        for p in prestiti:
            h_p = euristica_informata_tassonomia(grafo, p, obiettivo)
            valore = dist_persona[p] + h_p

            if best is None or valore < best:
                best = valore

        return float(best) if best is not None else 4.0

    # Fallback finale se il nodo non rientra nei casi previsti.
    return 1.0
