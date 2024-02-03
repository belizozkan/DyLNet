from jiwer import compute_measures, process_words, visualize_alignment
import json
"""
Ce script ne concerne que les adultes
WER pour tous les locuteurs
fichiers d'entrée : fichier reference converti par eaf2jsonWER et fichier hypothese converti par txt2json
sorties : WER par locuteur avec détails (détails: total sub, total insertion, total deletion) et segments hypotheses, segments references avec les insetions, deletions et les subs
"""
# Fonction pour calculer le taux d'erreur de mot (WER) en fonction des locuteurs
def calculate_wer(hypothesis_file, reference_file):
    # Charger les données d'hypothèse depuis le fichier JSON
    with open(hypothesis_file, 'r') as f:
        hypothesis_data = json.load(f)

    # Charger les données de référence depuis le fichier JSON
    with open(reference_file, 'r') as f:
        reference_data = json.load(f)

    # Initialiser des structures pour stocker les mesures par locuteur et les détails par locuteur
    measures_by_speaker = {}
    details_by_speaker = {}

    # Parcourir les segments d'hypothèse
    for h_segment in hypothesis_data:
        # Parcourir les segments de référence
        for r_segment in reference_data:
            # Vérifier si les segments appartiennent au même locuteur et correspondent en termes de fichier et de temps (tolérance de 0.1 seconde)
            if h_segment['speaker_id'] == r_segment['speaker_id']:
                if h_segment['speaker_id'].startswith('1') and r_segment['speaker_id'].startswith('1'):
                    if (h_segment['file_id'] == r_segment['file_id'] and
                        (h_segment['start_time'] == r_segment['start_time'] or abs(h_segment['end_time'] - r_segment['end_time']) < 0.1)):
                            # Extraire des informations spécifiques au segment
                            speaker_id = h_segment['speaker_id']
                            h_text = h_segment['hypothesis']
                            r_text = r_segment['transcript']

                            # Calculer les mesures WER et obtenir l'alignement des mots
                            measures = compute_measures(r_text, h_text)
                            alignment = process_words([r_text], [h_text])
                            details = "{}\nSegment WER: {}, Total Deletions: {}, Total Insertions: {}, Total Substitutions: {}\n{}".format(
                                h_segment['file_id'],
                                measures['wer'],
                                measures['deletions'],
                                measures['insertions'],
                                measures['substitutions'],
                                visualize_alignment(alignment, show_measures=False, skip_correct=False).replace('sentence 1\n', '')
                            )

                            # Stocker les mesures par locuteur
                            if speaker_id not in measures_by_speaker:
                                measures_by_speaker[speaker_id] = {"total_errors": 0, "total_words": 0, "deletions": 0, "insertions": 0, "substitutions": 0}
                                details_by_speaker[speaker_id] = []
                            measures_by_speaker[speaker_id]["total_errors"] += measures["wer"] * len(h_text.split())
                            measures_by_speaker[speaker_id]["total_words"] += len(h_text.split())
                            measures_by_speaker[speaker_id]["deletions"] += measures["deletions"]
                            measures_by_speaker[speaker_id]["insertions"] += measures["insertions"]
                            measures_by_speaker[speaker_id]["substitutions"] += measures["substitutions"]
                            details_by_speaker[speaker_id].append(details)

    # Calculer le WER total pour chaque locuteur
    total_wer_by_speaker = {speaker: {"wer": measures["total_errors"] / measures["total_words"] if measures["total_words"] > 0 else 0, "deletions": measures["deletions"], "insertions": measures["insertions"], "substitutions": measures["substitutions"]} for speaker, measures in measures_by_speaker.items()}

    return total_wer_by_speaker, details_by_speaker

# Fonction principale
def main():
    hypothesis_file = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_WER\\hyp.json'
    reference_file = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_WER\\ref.json'
    # Utiliser la fonction pour calculer le WER en fonction des locuteurs
    measures_results, details_results = calculate_wer(hypothesis_file, reference_file)
    
    # Afficher les résultats
    for speaker, measures in measures_results.items():
        print(f'Speaker: {speaker}, WER: {measures["wer"]}, Total Deletions: {measures["deletions"]}, Total Insertions: {measures["insertions"]}, Total Substitutions: {measures["substitutions"]}')
        for details in details_results[speaker]:
            print(details)

# Exécuter la fonction principale si le script est exécuté en tant que programme principal
if __name__ == "__main__":
    main()
