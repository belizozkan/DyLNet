import matplotlib.pyplot as plt
import numpy as np
import json
from pyannote.core import Segment, Annotation
from pyannote.metrics.detection import DetectionErrorRate
"""
Ce script ne concerne que les enfants
DER pour tous les locuteurs
fichiers d'entrée : fichier reference converti par eaf2jsonDER et fichier hypothese converti par textgrid2json pour la partie DER           
sorties : DER par locuteur sans détails avec deux graphiques comparatives générées
"""
# Fonction pour charger les annotations depuis le fichier JSON
def load_annotation_from_json(json_file):
    annotations_by_speaker_file = {}

    with open(json_file, 'r') as file:
        data = json.load(file)
        for segment_data in data:
            start_time = segment_data.get('start_time', 0)
            end_time = segment_data.get('end_time', 0)
            segment = Segment(start_time, end_time)
            label = str(segment_data.get('file_id', ''))
            speaker_id = segment_data.get('speaker_id', '')
            situation = segment_data.get('situation', '')
            class_id = segment_data.get('class_id', '')

            # Créer une structure pour stocker les annotations par locuteur, fichier et segment
            if speaker_id not in annotations_by_speaker_file:
                annotations_by_speaker_file[speaker_id] = {}
            if label not in annotations_by_speaker_file[speaker_id]:
                annotations_by_speaker_file[speaker_id][label] = Annotation()

            annotations_by_speaker_file[speaker_id][label][segment] = label

    return annotations_by_speaker_file

# Fonction pour calculer le DER entre les fichiers hypothèse et de référence
def calculate_der(hypothesis_fileder, reference_fileder):
    reference_annotations = load_annotation_from_json(reference_fileder)
    hypothesis_annotations = load_annotation_from_json(hypothesis_fileder)

    der_results = {}  # Dictionnaire pour stocker les résultats DER pour chaque locuteur

    for speaker_id, file_annotations in reference_annotations.items():
        der = DetectionErrorRate()
        total_miss = 0
        total_false_alarm = 0
        total_total = 0

        # Parcourir les fichiers et annotations de référence pour chaque locuteur
        for file_id, reference_annotation in file_annotations.items():
            hypothesis_annotation = hypothesis_annotations.get(speaker_id, {}).get(file_id, Annotation())
            components = der(reference_annotation, hypothesis_annotation, detailed=True)

            total_miss += components['miss']
            total_false_alarm += components['false alarm']
            total_total += components['total']

        # Calculer et stocker le taux d'erreur de détection (DER) pour chaque locuteur
        if total_total != 0:
            error_rate = (total_miss + total_false_alarm) / total_total
            der_results[speaker_id] = {"der": error_rate}

    # Filtrer les locuteurs dont l'identifiant commence par "0"
    der_results_filtered = {speaker_id: values for speaker_id, values in der_results.items() if speaker_id.startswith('0')}

    return der_results_filtered

# Fonction principale pour exécuter le code
def main():
    # Chemins des fichiers d'hypothèse et de référence pour le DER
    hypothesis_fileder = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER\\hyp.json'
    reference_fileder = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER\\ref.json'

    # Utiliser la fonction pour calculer le DER
    der_results = calculate_der(hypothesis_fileder, reference_fileder)

    # Extraire les locuteurs et les valeurs DER
    speakers = list(der_results.keys())
    der_values = [der_results[speaker]["der"] for speaker in speakers]

    x = np.arange(len(speakers))  # Les emplacements des étiquettes
    width = 0.35  # La largeur des barres

    # Créer des sous-graphiques pour le barplot et le scatterplot
    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, gridspec_kw={'height_ratios': [3, 1]})

    # Barplot pour le DER
    rects1 = ax1.bar(x, der_values, width, label='DER')

    # Ajouter des étiquettes pour les axes, le titre et les étiquettes personnalisées de l'axe des x, etc.
    ax1.set_ylabel('Scores')
    ax1.set_title('Scores DER par locuteur pour les enfants')
    ax1.set_xticks(x)
    ax1.set_xticklabels(speakers)
    ax1.legend()

    # Scatterplot
    scatter_x = []
    scatter_y = []

    for speaker_id, values in der_results.items():
        if speaker_id.startswith('0'):
            scatter_x.append(speaker_id)
            scatter_y.append(values["der"])

    ax2.scatter(scatter_x, scatter_y, color='red', marker='o', label='DER pour les enfants')
    ax2.set_xlabel('Identifiant du locuteur')
    ax2.set_ylabel('Scores')
    ax2.legend()

    fig.tight_layout()

    # Afficher le graphique
    plt.show()

# Exécuter la fonction principale si le script est exécuté en tant que programme principal
if __name__ == "__main__":
    main()
