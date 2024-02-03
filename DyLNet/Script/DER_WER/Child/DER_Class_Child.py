import matplotlib.pyplot as plt
import numpy as np
import json
from pyannote.core import Segment, Annotation
from pyannote.metrics.detection import DetectionErrorRate
"""
Ce script ne concerne que les enfants
DER pour toutes les classes
fichiers d'entrée : fichier reference converti par eaf2jsonDER et fichier hypothese converti par textgrid2json pour la partie DER           
sorties : DER par classe sans détails avec deux graphiques comparatives générées
"""
# Fonction pour charger les annotations depuis un fichier JSON
def load_annotation_from_json(json_file):
    annotations_by_class_file = {}

    with open(json_file, 'r') as file:
        data = json.load(file)
        for segment_data in data:
            start_time = segment_data.get('start_time', 0)
            end_time = segment_data.get('end_time', 0)
            segment = Segment(start_time, end_time)
            label = str(segment_data.get('file_id', ''))
            class_id = segment_data.get('class_id', '')
            situation = segment_data.get('situation', '')
            speaker_id = segment_data.get('speaker_id', '')

            # Créer et stocker l'annotation pour chaque classe, fichier et locuteur
            if class_id not in annotations_by_class_file:
                annotations_by_class_file[class_id] = {"annotations": {}, "speaker_ids": []}
            if label not in annotations_by_class_file[class_id]["annotations"]:
                annotations_by_class_file[class_id]["annotations"][label] = Annotation()

            annotations_by_class_file[class_id]["annotations"][label][segment] = label
            if speaker_id not in annotations_by_class_file[class_id]["speaker_ids"]:
                annotations_by_class_file[class_id]["speaker_ids"].append(speaker_id)

    return annotations_by_class_file

# Fonction pour calculer le DER entre le fichier hypothèse et le fichier de référence
def calculate_der(hypothesis_fileder, reference_fileder):
    reference_annotations = load_annotation_from_json(reference_fileder)
    hypothesis_annotations = load_annotation_from_json(hypothesis_fileder)

    der_results = {} 

    # Parcourir les classes d'annotations de référence
    for class_id, class_data in reference_annotations.items():
        der = DetectionErrorRate()
        total_miss = 0
        total_false_alarm = 0
        total_total = 0

        # Parcourir les fichiers et segments d'annotations de référence pour chaque classe
        for file_id, reference_annotation in class_data["annotations"].items():
            hypothesis_annotation = hypothesis_annotations.get(class_id, {}).get("annotations", {}).get(file_id, Annotation())
            components = der(reference_annotation, hypothesis_annotation, detailed=True)

            total_miss += components['miss']
            total_false_alarm += components['false alarm']
            total_total += components['total']

        # Calculer et stocker le taux d'erreur de détection (DER) pour chaque classe
        if total_total != 0:
            error_rate = (total_miss + total_false_alarm) / total_total
            der_results[class_id] = {"der": error_rate, "speaker_ids": class_data["speaker_ids"]}

    # Filtrer les classes dont les identifiants de locuteurs commencent par "0"
    der_results_filtered = {class_id: values for class_id, values in der_results.items() if any(speaker_id.startswith('0') for speaker_id in values["speaker_ids"])}

    return der_results_filtered

# Fonction principale pour exécuter le code
def main():
    # Chemins des fichiers d'hypothèse et de référence pour le DER
    hypothesis_fileder = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER\\hyp.json'
    reference_fileder = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER\\ref.json'

    # Utiliser la fonction pour calculer le DER
    der_results = calculate_der(hypothesis_fileder, reference_fileder)
    print(der_results)

    # Boxplot
    classes = list(der_results.keys())
    der_values = [der_results[class_id]["der"] for class_id in classes]

    x = np.arange(len(classes))  # Les emplacements des étiquettes
    width = 0.35  # La largeur des barres

    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    rects1 = ax1.bar(x, der_values, width, label='DER')

    # Ajouter des étiquettes pour les axes, le titre et les étiquettes personnalisées de l'axe des x, etc.
    ax1.set_ylabel('Scores')
    ax1.set_title('Scores DER par classe pour les enfants')
    ax1.set_xticks(x)
    ax1.set_xticklabels(classes)
    ax1.legend()

    # Nuage de points
    scatter_x = []
    scatter_y = []

    for class_id, values in der_results.items():
        if any(speaker_id.startswith('0') for speaker_id in values["speaker_ids"]):
            scatter_x.append(class_id)
            scatter_y.append(values["der"])

    ax2.scatter(scatter_x, scatter_y, color='red', marker='o', label='DER pour les enfants')
    ax2.set_xlabel('ID de la classe')
    ax2.set_ylabel('Scores')
    ax2.legend()

    fig.tight_layout()

    # Afficher le graphique
    plt.show()

# Exécuter la fonction principale si le script est exécuté en tant que programme principal
if __name__ == "__main__":
    main()
