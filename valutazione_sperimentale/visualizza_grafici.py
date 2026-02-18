from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# Carica il file risultati.csv dalla cartella "risultati".
# Se non lo trova, avvisa e si ferma.
def carica_risultati():
    base = Path(__file__).resolve().parent
    csv_path = base / "risultati" / "risultati.csv"

    if not csv_path.exists():
        print("Non trovo risultati.csv.")
        print("Prima esegui: python -m valutazione_sperimentale.runner_esperimenti")
        return None, None

    df = pd.read_csv(csv_path)

    # Se la colonna 'trovato' è stata letta come stringa, la sistemiamo
    if df["trovato"].dtype == object:
        df["trovato"] = df["trovato"].astype(str).str.lower().isin(["true", "1"])

    return df, csv_path.parent


# Grafico 1
# Confronto globale: quante espansioni in media fa ogni euristica.
# Serve per vedere chi esplora meno nodi in generale.
def grafico_nodi_medi_per_euristica(df, out):
    grp = df.groupby("euristica").agg(
        nodi_medi=("nodi_espansi", "mean")
    ).reset_index()

    grp = grp.sort_values("nodi_medi")

    plt.figure(figsize=(6, 4))
    plt.plot(grp["euristica"], grp["nodi_medi"], marker="o")
    plt.title("Nodi espansi medi per euristica")
    plt.xlabel("Euristica")
    plt.ylabel("Nodi espansi medi")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "01_nodi_medi_per_euristica.png")
    plt.close()


# Grafico 2
# Tempo medio di esecuzione per ciascuna euristica.
# Qui guardiamo la velocità, non la qualità della ricerca.
def grafico_tempo_medio(df, out):
    grp = df.groupby("euristica").agg(
        tempo_medio=("tempo_ms", "mean")
    ).reset_index()

    plt.figure(figsize=(6, 4))
    plt.bar(grp["euristica"], grp["tempo_medio"])
    plt.title("Tempo medio per euristica")
    plt.xlabel("Euristica")
    plt.ylabel("Tempo medio (ms)")
    plt.tight_layout()
    plt.savefig(out / "02_tempo_medio_per_euristica.png")
    plt.close()


# Grafico 3 (COME PRIMA)
# Confronto delle euristiche caso per caso.
# I casi vengono ordinati per difficoltà media
# così il grafico è più leggibile e progressivo.
def grafico_nodi_per_caso(df, out):
    grp = df.groupby(
        ["nodo_iniziale", "nodo_obiettivo", "euristica"]
    ).agg(
        nodi_medi=("nodi_espansi", "mean")
    ).reset_index()

    # Creo etichetta leggibile per ogni caso
    grp["caso"] = grp["nodo_iniziale"] + " → " + grp["nodo_obiettivo"]

    pivot = grp.pivot(index="caso", columns="euristica", values="nodi_medi")

    # Ordiniamo i casi per difficoltà media (come faceva la versione chiara)
    pivot["media"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("media")
    pivot = pivot.drop(columns=["media"])

    plt.figure(figsize=(8, 4))

    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col], marker="o", label=col)

    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Nodi espansi medi")
    plt.title("Nodi espansi per caso (confronto euristiche)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "03_nodi_per_caso.png")
    plt.close()


# Grafico 4
# Visualizziamo un percorso reale (il più lungo trovato).
# Serve solo a mostrare concretamente un esempio di risultato.
def grafico_percorso_esempio(df, out):
    df_ok = df[df["trovato"] == True].copy()

    if df_ok.empty:
        return

    df_ok["lung"] = df_ok["lunghezza_percorso"]
    esempio = df_ok.sort_values("lung", ascending=False).iloc[0]

    nodi = [x.strip() for x in esempio["percorso"].split("->")]

    plt.figure(figsize=(len(nodi) * 1.2, 2.5))

    for i, nodo in enumerate(nodi):
        plt.scatter(i, 0)
        plt.text(i, 0.02, nodo, ha="center", rotation=45)

        if i < len(nodi) - 1:
            plt.plot([i, i + 1], [0, 0])

    plt.yticks([])
    plt.xticks([])
    titolo = f"Percorso esempio: {esempio['nodo_iniziale']} → {esempio['nodo_obiettivo']}"
    plt.title(titolo)
    plt.tight_layout()
    plt.savefig(out / "04_percorso_esempio.png")
    plt.close()


# Punto di ingresso del modulo.
# Carica i dati e genera tutti i grafici.
def main():
    df, out = carica_risultati()
    if df is None:
        return

    grafico_nodi_medi_per_euristica(df, out)
    grafico_tempo_medio(df, out)
    grafico_nodi_per_caso(df, out)
    grafico_percorso_esempio(df, out)

    print("Grafici generati correttamente.")


if __name__ == "__main__":
    main()
