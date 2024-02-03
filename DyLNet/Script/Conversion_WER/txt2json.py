import os
import json
from unidecode import unidecode
"""
Ce script ne concerne que les adultes
fichiers d'entrée : .txt (fichier hypothese)         
sorties : .json 
"""
def txt2json(input_dir, output_file):
    all_segments = []

    # Parcourir tous les fichiers du répertoire d'entrée
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(input_dir, filename)

            # Lire le contenu du fichier texte
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            lines = [line.strip() for line in lines]

            # Parcourir les lignes du fichier texte et extraire les segments
            for i in range(12, len(lines), 5):
                file_id_full = lines[i]
                file_id_parts = file_id_full.split("_")
                file_part = "_".join(file_id_parts[:-3]).strip()
                file_id = file_part[:-2]

                line_parts = file_id.split("-")
                speaker_id = line_parts[3].strip()
                class_id = line_parts[0].strip()

                file_id_nower = lines[i]
                file_id_parts2 = file_id_nower.split(",")
                nower = file_id_parts2[0]
                nofile = nower.split("-")
                rvb = nofile[-1] 
                times = rvb.split("_")
                start_time = times[2]
                end_time = times[3]

                hypothesis = lines[i + 3]  
                processed_hypothesis = ' '.join(hypothesis.split(';')).lower().strip()
                processed_hypothesis = unidecode(processed_hypothesis)

                # Créer un dictionnaire pour chaque segment et l'ajouter à la liste
                segment_dict = {
                    "file_id": file_id,
                    "speaker_id": speaker_id,
                    "class_id" : class_id,
                    "start_time": int(start_time) / 1000,
                    "end_time": int(end_time) / 1000,
                    "duration": int(end_time) - int(start_time),
                    "hypothesis": processed_hypothesis,
                }

                all_segments.append(segment_dict)

    # Écrire la liste de segments au format JSON dans le fichier de sortie
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(all_segments, json_file, indent=2)

# Programme principal
if __name__ == "__main__":
    input_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Input_txt2jsonWER'
    output_file = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_WER\\hypothesis.json'

    # Appeler la fonction pour convertir les fichiers texte en JSON
    txt2json(input_directory, output_file)
