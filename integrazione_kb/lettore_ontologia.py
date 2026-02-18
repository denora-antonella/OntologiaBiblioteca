from owlready2 import get_ontology, sync_reasoner_pellet


def carica_ontologia(percorso_file_owl, usa_reasoner=False):
    """
    Carica un file OWL e restituisce l'ontologia.

    Se usa_reasoner=True, viene eseguito il reasoner
    per inferire nuove relazioni e proprietà.
    """

    ontologia = get_ontology(percorso_file_owl).load()

    if usa_reasoner:
        with ontologia:
            sync_reasoner_pellet(
                infer_property_values=True,
                infer_data_property_values=True
            )

    return ontologia
