import matplotlib.pyplot as plt
import numpy as np
import json
from jiwer import compute_measures, process_words
import os
from pyannote.core import Segment, Annotation
from pyannote.metrics.detection import DetectionErrorRate
"""
Ce script ne concerne que les adultes
WER et DER pour toutes les situations
fichiers d'entrée : fichier reference converti par eaf2jsonWER et fichier hypothese converti par txt2json pour la partie WER
                  : fichier reference converti par eaf2jsonDER et fichier hypothese converti par textgrid2json pour la partie DER
sorties : WER et DER par situation sans détails avec deux graphiques comparatives générées
"""
# Fonction pour calculer le WER entre le fichier hypothèse et le fichier de référence
def calculate_wer(hypothesis_file, reference_file):
    with open(hypothesis_file, 'r') as f:
        hypothesis_data = json.load(f)

    with open(reference_file, 'r') as f:
        reference_data = json.load(f)

    measures_by_situation = {}

    # Parcourir les segments dans les fichiers d'hypothèse et de référence
    for r_segment in reference_data:
        for h_segment in hypothesis_data:
            # Vérifier si les segments correspondent
            if (h_segment['file_id'] == r_segment['file_id'] and
                (h_segment['start_time'] == r_segment['start_time'] or abs(h_segment['end_time'] - r_segment['end_time']) < 0.1)):
                situation = r_segment['situation']
                h_text = h_segment['hypothesis']
                r_text = r_segment['transcript']
                measures = compute_measures(r_text, h_text)

                # Calculer et stocker les mesures pour chaque situation
                if situation not in measures_by_situation:
                    measures_by_situation[situation] = {"total_errors": 0, "total_words": 0}
                measures_by_situation[situation]["total_errors"] += measures["wer"] * len(h_text.split())
                measures_by_situation[situation]["total_words"] += len(h_text.split())

    # Calculer le WER total par situation
    total_wer_by_situation = {situation: {"wer": measures["total_errors"] / measures["total_words"] if measures["total_words"] > 0 else 0} for situation, measures in measures_by_situation.items()}

    return total_wer_by_situation

# Fonction pour charger les annotations depuis des fichiers JSON
def load_annotation_from_json(ref_json_file, hyp_json_file):
    annotations_by_situation_file = {}

    with open(ref_json_file, 'r') as ref_file, open(hyp_json_file, 'r') as hyp_file:
        ref_data = json.load(ref_file)
        hyp_data = json.load(hyp_file)

        # Parcourir les données de référence et d'hypothèse en parallèle
        for ref_segment_data, hyp_segment_data in zip(ref_data, hyp_data):
            ref_start_time = ref_segment_data.get('start_time', 0)
            ref_end_time = ref_segment_data.get('end_time', 0)
            ref_segment = Segment(ref_start_time, ref_end_time)
            ref_label = str(ref_segment_data.get('file_id', ''))
            ref_speaker_id = ref_segment_data.get('speaker_id', '')
            ref_situation = ref_segment_data.get('situation', '')
            ref_class_id = ref_segment_data.get('class_id', '')  

            hyp_start_time = hyp_segment_data.get('start_time', 0)
            hyp_end_time = hyp_segment_data.get('end_time', 0)
            hyp_segment = Segment(hyp_start_time, hyp_end_time)
            hyp_label = str(hyp_segment_data.get('file_id', ''))

            # Créer et stocker l'annotation pour chaque situation et fichier
            if ref_situation not in annotations_by_situation_file:
                annotations_by_situation_file[ref_situation] = {}
            if ref_label not in annotations_by_situation_file[ref_situation]:
                annotations_by_situation_file[ref_situation][ref_label] = []

            annotations_by_situation_file[ref_situation][ref_label].append((ref_segment, hyp_segment))

    return annotations_by_situation_file

# Fonction pour calculer le DER entre le fichier hypothèse et le fichier de référence
def calculate_der(hypothesis_fileder, reference_fileder):
    reference_annotations = load_annotation_from_json(reference_fileder, hypothesis_fileder)

    der_results = {}  # Dictionnaire pour stocker les résultats DER pour chaque situation

    # Parcourir les annotations de référence par situation
    for situation, file_annotations in reference_annotations.items():
        der = DetectionErrorRate()
        total_miss = 0
        total_false_alarm = 0
        total_total = 0

        # Parcourir les fichiers et segments d'annotations de référence
        for file_id, segments in file_annotations.items():
            reference_annotation = Annotation()
            hypothesis_annotation = Annotation()

            # Ajouter les segments d'annotations pour le fichier donné
            for ref_segment, hyp_segment in segments:
                reference_annotation[ref_segment] = situation
                hypothesis_annotation[hyp_segment] = situation

            components = der(reference_annotation, hypothesis_annotation, detailed=True)

            total_miss += components['miss']
            total_false_alarm += components['false alarm']
            total_total += components['total']
        
        # Calculer et stocker le taux d'erreur de détection (DER) pour chaque situation
        if total_total != 0:
            error_rate = (total_miss + total_false_alarm) / total_total
            der_results[situation] = {"der": error_rate}

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

    # Récupérer les situations à partir des résultats WER
    situations = list(wer_results.keys())

    # Récupérer les valeurs WER et DER pour chaque situation
    wer_values = [wer_results.get(st, {"wer": 0})["wer"] for st in situations]
    der_values = [der_results.get(st, {"der": 0})["der"] for st in situations]

    # Créer le graphique à barres et le nuage de points
    x = np.arange(len(situations))
    width = 0.35
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Graphique à barres pour WER et DER
    rects1 = ax1.bar(x - width/2, wer_values, width, label='WER')
    rects2 = ax1.bar(x + width/2, der_values, width, label='DER')
    ax1.set_ylabel('Scores')
    ax1.set_title('Scores par situation et métrique')
    ax1.set_xticks(x)
    ax1.set_xticklabels(situations)
    ax1.legend()

    # Nuage de points pour WER vs. DER
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
