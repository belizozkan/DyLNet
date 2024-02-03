import matplotlib.pyplot as plt
import numpy as np
import json
from jiwer import compute_measures, process_words
import os
from pyannote.core import Segment, Annotation
from pyannote.metrics.detection import DetectionErrorRate
"""
Ce script ne concerne que les adultes
WER et DER pour toutes les classes
fichiers d'entrée : fichier reference converti par eaf2jsonWER et fichier hypothese converti par txt2json pour la partie WER
                  : fichier reference converti par eaf2jsonDER et fichier hypothese converti par textgrid2json pour la partie DER
sorties : WER et DER par classe sans détails avec deux graphiques comparatives générées
"""
# Fonction pour calculer le WER entre le fichier hypothèse et le fichier de référence
def calculate_wer(hypothesis_file, reference_file):
    with open(hypothesis_file, 'r') as f:
        hypothesis_data = json.load(f)

    with open(reference_file, 'r') as f:
        reference_data = json.load(f)

    measures_by_class = {}

    # Parcourir les segments dans les fichiers d'hypothèse et de référence
    for h_segment in hypothesis_data:
        for r_segment in reference_data:
            if h_segment['class_id'] == r_segment['class_id']:
                # Vérifier si les segments correspondent
                if (h_segment['file_id'] == r_segment['file_id'] and
                    (h_segment['start_time'] == r_segment['start_time'] or abs(h_segment['end_time'] - r_segment['end_time']) < 0.1)):
                        class_id = h_segment['class_id']
                        h_text = h_segment['hypothesis']
                        r_text = r_segment['transcript']
                        measures = compute_measures(r_text, h_text)

                        # Calculer et stocker les mesures pour chaque classe
                        if class_id not in measures_by_class:
                            measures_by_class[class_id] = {"total_errors": 0, "total_words": 0}
                        measures_by_class[class_id]["total_errors"] += measures["wer"] * len(h_text.split())
                        measures_by_class[class_id]["total_words"] += len(h_text.split())

    # Calculer le WER total par classe
    total_wer_by_class = {class_id: {"wer": measures["total_errors"] / measures["total_words"] if measures["total_words"] > 0 else 0} for class_id, measures in measures_by_class.items()}

    return total_wer_by_class

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

            # Créer et stocker l'annotation pour chaque classe et fichier
            if class_id not in annotations_by_class_file:
                annotations_by_class_file[class_id] = {}
            if label not in annotations_by_class_file[class_id]:
                annotations_by_class_file[class_id][label] = Annotation()

            annotations_by_class_file[class_id][label][segment] = label
    return annotations_by_class_file

# Fonction pour calculer le DER entre le fichier hypothèse et le fichier de référence
def calculate_der(hypothesis_fileder, reference_fileder):
    reference_annotations = load_annotation_from_json(reference_fileder)
    hypothesis_annotations = load_annotation_from_json(hypothesis_fileder)

    der_results = {}  

    # Parcourir les annotations de référence par classe
    for class_id, file_annotations in reference_annotations.items():
        der = DetectionErrorRate()
        total_miss = 0
        total_false_alarm = 0
        total_total = 0

        # Parcourir les fichiers et annotations de référence
        for file_id, reference_annotation in file_annotations.items():
            hypothesis_annotation = hypothesis_annotations.get(class_id, {}).get(file_id, Annotation())  
            components = der(reference_annotation, hypothesis_annotation, detailed=True)

            total_miss += components['miss']
            total_false_alarm += components['false alarm']
            total_total += components['total']

        # Calculer et stocker le taux d'erreur de détection (DER) pour chaque classe
        if total_total != 0:
            error_rate = (total_miss + total_false_alarm) / total_total
            der_results[class_id] = {"der": error_rate}

    return der_results

# Fonction principale pour exécuter le code
def main():
    # Chemins des fichiers d'hypothèse et de référence pour WER
    hypothesis_filewer = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_WER\\hyp.json'
    reference_filewer = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_WER\\ref.json'

    # Chemins des fichiers d'hypothèse et de référence pour DER
    hypothesis_fileder = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER\\hyp.json'
    reference_fileder = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER\\ref.json'

    # Calculer les résultats WER et DER
    wer_results = calculate_wer(hypothesis_filewer, reference_filewer)
    der_results = calculate_der(hypothesis_fileder, reference_fileder)

    # Récupérer les classes à partir des résultats WER
    classes = list(wer_results.keys())

    # Récupérer les valeurs WER et DER pour chaque classe
    wer_values = [wer_results.get(cl, {"wer": 0})["wer"] for cl in classes]
    der_values = [der_results.get(cl, {"der": 0})["der"] for cl in classes]

    # Créer le graphique à barres et le nuage de points
    x = np.arange(len(classes))
    width = 0.35
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    rects1 = ax1.bar(x - width/2, wer_values, width, label='WER')
    rects2 = ax1.bar(x + width/2, der_values, width, label='DER')
    ax1.set_ylabel('Scores')
    ax1.set_title('Scores par classe et métrique')
    ax1.set_xticks(x)
    ax1.set_xticklabels(classes)
    ax1.legend()

    ax2.scatter(wer_values, der_values, color='blue', label='WER vs. DER')
    ax2.set_xlabel('WER')
    ax2.set_ylabel('DER')
    ax2.set_title('WER vs. DER')
    ax2.legend()

    fig.tight_layout()

    # Afficher le graphique
    plt.show()

# Exécuter la fonction principale si le script est exécuté en tant que programme principal
if __name__ == "__main__":
    main()
