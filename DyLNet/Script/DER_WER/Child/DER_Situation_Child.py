import matplotlib.pyplot as plt
import numpy as np
import json
from pyannote.core import Segment, Annotation
from pyannote.metrics.detection import DetectionErrorRate
"""
Ce script ne concerne que les enfants
DER pour toutes les situations
fichiers d'entrée : fichier reference converti par eaf2jsonDER et fichier hypothese converti par textgrid2json pour la partie DER           
sorties : DER par situation sans détails avec deux graphiques comparatives générées
"""
# Fonction pour charger les annotations depuis les fichiers JSON de référence et d'hypothèse
def load_annotation_from_json(ref_json_file, hyp_json_file):
    annotations_by_situation_file = {}

    with open(ref_json_file, 'r') as ref_file, open(hyp_json_file, 'r') as hyp_file:
        ref_data = json.load(ref_file)
        hyp_data = json.load(hyp_file)

        for ref_segment_data, hyp_segment_data in zip(ref_data, hyp_data):
            ref_start_time = ref_segment_data.get('start_time', 0)
            ref_end_time = ref_segment_data.get('end_time', 0)
            ref_segment = Segment(ref_start_time, ref_end_time)
            ref_label = str(ref_segment_data.get('file_id', ''))
            ref_speaker_id = ref_segment_data.get('speaker_id', '')

            # Skip if the speaker_id does not start with '0'
            if not ref_speaker_id.startswith('0'):
                continue

            ref_situation = ref_segment_data.get('situation', '')
            ref_class_id = ref_segment_data.get('class_id', '')  

            hyp_start_time = hyp_segment_data.get('start_time', 0)
            hyp_end_time = hyp_segment_data.get('end_time', 0)
            hyp_segment = Segment(hyp_start_time, hyp_end_time)
            hyp_label = str(hyp_segment_data.get('file_id', ''))

            # Créer et stocker l'annotation pour chaque situation, fichier et locuteur
            if ref_situation not in annotations_by_situation_file:
                annotations_by_situation_file[ref_situation] = {"speaker_ids": []}
            if ref_label not in annotations_by_situation_file[ref_situation]:
                annotations_by_situation_file[ref_situation][ref_label] = []

            annotations_by_situation_file[ref_situation][ref_label].append((ref_segment, hyp_segment))
            
            # Ajouter le speaker_id à la liste s'il n'est pas déjà présent
            if ref_speaker_id not in annotations_by_situation_file[ref_situation]["speaker_ids"]:
                annotations_by_situation_file[ref_situation]["speaker_ids"].append(ref_speaker_id)

    return annotations_by_situation_file

# Fonction pour calculer le DER entre le fichier hypothèse et le fichier de référence
def calculate_der(hypothesis_fileder, reference_fileder):
    reference_annotations = load_annotation_from_json(reference_fileder, hypothesis_fileder)

    der_results = {}  # Dictionnaire pour stocker les résultats DER pour chaque situation

    for situation, file_annotations in reference_annotations.items():
        der = DetectionErrorRate()
        total_miss = 0
        total_false_alarm = 0
        total_total = 0

        # Parcourir les fichiers et segments d'annotations de référence pour chaque situation
        for file_id, segments in file_annotations.items():
            if file_id == "speaker_ids":
                continue   # Ignorer ce file_id s'il ne correspond pas aux segments attendus

            reference_annotation = Annotation()
            hypothesis_annotation = Annotation()

            # Ajouter les segments à l'annotation de référence et d'hypothèse
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
            der_results[situation] = {"der": error_rate, "speaker_ids": file_annotations["speaker_ids"]}

    # Filtrer les situations dont les identifiants de locuteurs commencent par "0"
    der_results_filtered = {situation: values for situation, values in der_results.items() if any(speaker_id.startswith('0') for speaker_id in values["speaker_ids"])}
    return der_results_filtered

# Fonction principale pour exécuter le code
def main():
    # Chemins des fichiers d'hypothèse et de référence pour le DER
    hypothesis_fileder = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER\\hyp.json'
    reference_fileder = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER\\ref.json'

    # Utiliser la fonction pour calculer le DER
    der_results = calculate_der(hypothesis_fileder, reference_fileder)

    situations = list(der_results.keys())
    der_values = [der_results.get(st, {"der": 0})["der"] for st in situations]

    x = np.arange(len(situations))
    width = 0.35

    # Créer des sous-graphiques pour le barplot et le scatterplot
    fig, axs = plt.subplots(nrows=2, gridspec_kw={'height_ratios': [3, 1]})
    ax1, ax2 = axs

    # Barplot pour le DER
    rects1 = ax1.bar(x, der_values, width, label='DER')

    # Ajouter des étiquettes pour les axes, le titre et les étiquettes personnalisées de l'axe des x, etc.
    ax1.set_ylabel('Scores')
    ax1.set_title('Scores DER par situation pour les enfants')
    ax1.set_xticks(x)
    ax1.set_xticklabels(situations, rotation=45, ha='right')  # Définir les xticks et xticklabels pour ax1 ici
    ax1.legend()

    # Scatterplot
    scatter_x = []
    scatter_y = []

    for situation, values in der_results.items():
        if any(speaker_id.startswith('0') for speaker_id in values["speaker_ids"]):
            scatter_x.append(situation)
            scatter_y.append(values["der"])

    ax2.scatter(scatter_x, scatter_y, color='red', marker='o', label='DER pour les enfants')
    ax2.set_xlabel('Situation')
    ax2.set_ylabel('Scores')
    ax2.legend()

    fig.tight_layout()

    # Afficher le graphique
    plt.show()

# Exécuter la fonction principale si le script est exécuté en tant que programme principal
if __name__ == "__main__":
    main()
