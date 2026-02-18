from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def main():

    print("\nGenero la tabella riassuntiva e i grafici aggregati...\n")

    cartella_progetto = Path(__file__).resolve().parent.parent
    cartella_risultati = cartella_progetto / "valutazione_sperimentale" / "risultati"
    csv_path = cartella_risultati / "risultati.csv"

    if not csv_path.exists():
        print("Non trovo risultati.csv.")
        print("Prima esegui il runner degli esperimenti.\n")
        return

    df = pd.read_csv(csv_path)
    df["trovato"] = df["trovato"].astype(bool)

    gruppi = df.groupby(["nodo_iniziale", "nodo_obiettivo", "euristica"], dropna=False)

    tabella = gruppi.agg(
        n_run=("id_esperimento", "count"),
        successo_pct=("trovato", lambda x: 100.0 * x.mean()),
        tempo_medio_ms=("tempo_ms", "mean"),
        tempo_std_ms=("tempo_ms", "std"),
        espansi_medio=("nodi_espansi", "mean"),
        espansi_std=("nodi_espansi", "std"),
        costo_medio=("costo", "mean"),
        costo_std=("costo", "std"),
    ).reset_index()

    for c in ["tempo_std_ms", "espansi_std", "costo_std"]:
        tabella[c] = tabella[c].fillna(0.0)

    out_tabella = cartella_risultati / "tabella_riassuntiva.csv"
    tabella.to_csv(out_tabella, index=False)

    tabella["caso"] = (
        tabella["nodo_iniziale"]
        + " → "
        + tabella["nodo_obiettivo"]
        + " ("
        + tabella["euristica"]
        + ")"
    )

    # --- Grafico tempo medio con deviazione standard ---
    plt.figure()
    plt.bar(tabella["caso"], tabella["tempo_medio_ms"], yerr=tabella["tempo_std_ms"], capsize=4)
    plt.ylabel("Tempo medio (ms)")
    plt.title("Tempo medio A* (media ± dev. std)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out_tempo = cartella_risultati / "tempo_medio_con_std.png"
    plt.savefig(out_tempo)
    plt.close()

    # --- Grafico nodi espansi ---
    plt.figure()
    plt.bar(tabella["caso"], tabella["espansi_medio"], yerr=tabella["espansi_std"], capsize=4)
    plt.ylabel("Nodi espansi (media)")
    plt.title("Nodi espansi A* (media ± dev. std)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out_espansi = cartella_risultati / "nodi_espansi_con_std.png"
    plt.savefig(out_espansi)
    plt.close()

    # --- Grafico successo ---
    plt.figure()
    plt.bar(tabella["caso"], tabella["successo_pct"])
    plt.ylabel("Successo (%)")
    plt.title("Tasso di successo")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 100)
    plt.tight_layout()
    out_succ = cartella_risultati / "successo_pct.png"
    plt.savefig(out_succ)
    plt.close()

    print("Tabella riassuntiva salvata in:")
    print(" -", out_tabella)

    print("\nGrafici aggregati salvati in:")
    print(" -", out_tempo)
    print(" -", out_espansi)
    print(" -", out_succ)

    print("\nPuoi aprire la cartella 'risultati' per consultarli.\n")


if __name__ == "__main__":
    main()
