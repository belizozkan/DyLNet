from jiwer import compute_measures, process_words, visualize_alignment
import json
"""
Ce script ne concerne que les adultes
WER pour toutes les situations
fichiers d'entrée : fichier reference converti par eaf2jsonWER et fichier hypothese converti par txt2json
sorties : WER par situation avec détails (détails: total sub, total insertion, total deletion) et segments hypotheses, segments references avec les insetions, deletions et les subs
"""
# Fonction pour calculer le taux d'erreur de mot (WER) en fonction des situations
def calculate_wer(hypothesis_file, reference_file):
    # Charger les données d'hypothèse depuis le fichier JSON
    with open(hypothesis_file, 'r') as f:
        hypothesis_data = json.load(f)

    # Charger les données de référence depuis le fichier JSON
    with open(reference_file, 'r') as f:
        reference_data = json.load(f)

    # Initialiser des structures pour stocker les mesures par situation et les détails par situation
    measures_by_situation = {}
    details_by_situation = {}

    # Parcourir les segments de référence
    for r_segment in reference_data:
        # Parcourir les segments d'hypothèse
        for h_segment in hypothesis_data:
            # Vérifier si les segments appartiennent au même locuteur et correspondent en termes de fichier et de temps (tolérance de 0.1 seconde)
            if h_segment['speaker_id'].startswith('1') and r_segment['speaker_id'].startswith('1'):
                if (h_segment['file_id'] == r_segment['file_id'] and
                    (h_segment['start_time'] == r_segment['start_time'] or abs(h_segment['end_time'] - r_segment['end_time']) < 0.1)):
                    # Extraire des informations spécifiques au segment
                    situation = r_segment['situation']
                    h_text = h_segment['hypothesis']
                    r_text = r_segment['transcript']

                    # Calculer les mesures WER et obtenir l'alignement des mots
                    measures = compute_measures(r_text, h_text)
                    alignment = process_words([r_text], [h_text])

                    # Formater les détails pour l'affichage
                    details = h_segment['file_id'] + "\nSegment WER: " + str(measures['wer']) + ", Total Deletions: " + str(measures['deletions']) + ", Total Insertions: " + str(measures['insertions']) + ", Total Substitutions: " + str(measures['substitutions']) + "\n" + visualize_alignment(alignment, show_measures=False, skip_correct=False).replace('sentence 1\n', '')

                    # Stocker les mesures par situation
                    if situation not in measures_by_situation:
                        measures_by_situation[situation] = {"total_errors": 0, "total_words": 0, "deletions": 0, "insertions": 0, "substitutions": 0}
                        details_by_situation[situation] = []
                    measures_by_situation[situation]["total_errors"] += measures["wer"] * len(h_text.split())
                    measures_by_situation[situation]["total_words"] += len(h_text.split())
                    measures_by_situation[situation]["deletions"] += measures["deletions"]
                    measures_by_situation[situation]["insertions"] += measures["insertions"]
                    measures_by_situation[situation]["substitutions"] += measures["substitutions"]
                    details_by_situation[situation].append(details)

    # Calculer le WER total pour chaque situation
    total_wer_by_situation = {situation: {"wer": measures["total_errors"] / measures["total_words"] if measures["total_words"] > 0 else 0, "deletions": measures["deletions"], "insertions": measures["insertions"], "substitutions": measures["substitutions"]} for situation, measures in measures_by_situation.items()}

    return total_wer_by_situation, details_by_situation

# Fonction principale
def main():
    hypothesis_file = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_WER\\hyp.json'
    reference_file = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_WER\\ref.json'
    # Utiliser la fonction pour calculer le WER en fonction des situations
    measures_results, details_results = calculate_wer(hypothesis_file, reference_file)
    
    # Afficher les résultats
    for situation, measures in measures_results.items():
        print(f'Situation: {situation}, WER: {measures["wer"]}, Total Deletions: {measures["deletions"]}, Total Insertions: {measures["insertions"]}, Total Substitutions: {measures["substitutions"]}')
        for details in details_results[situation]:
            print(details)

# Exécuter la fonction principale si le script est exécuté en tant que programme principal
if __name__ == "__main__":
    main()
