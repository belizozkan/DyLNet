import os
import json
from praatio import tgio
"""
Ce script concerne les enfants et les adultes
fichiers d'entrée : .textgrid (fichier hypothese)         
sorties : .json 
"""
def textgrid2json(file_path, json_entries):
    # Ouvre le fichier TextGrid avec la bibliothèque praatio
    tg = tgio.openTextgrid(file_path)

    # Nom du tier à extraire du TextGrid
    tier_name = "silences"
    
    # Récupère le tier spécifié du TextGrid
    tier = tg.tierDict[tier_name]

    # Obtient le nom du fichier sans extension
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # Extraire les parties du file_id
    file_id_parts = file_name.split('-')[:7]
    
    # Construit le file_id en rejoignant les parties
    file_id = '-'.join(file_id_parts)
    
    # Obtient le speaker_id à partir du file_id
    parts_speaker = file_id.split('-')
    speaker_id = parts_speaker[3].strip()
    
    # Obtient le class_id à partir du file_id
    class_parts = file_name.split('-')
    class_id = class_parts[0].strip()

    # Parcours chaque entrée dans le tier et la convertit en format JSON
    for entry in tier.entryList:
        start_time = round(entry[0], 2)
        end_time = round(entry[1], 2)
        orthographic_transcript = entry[2]
        duration = end_time - start_time

        # Crée un dictionnaire pour chaque segment et l'ajoute à la liste de résultats
        segment_dict = {
            "file_id": file_id,
            "speaker_id": speaker_id,
            "class_id": class_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "transcript": orthographic_transcript
        }

        json_entries.append(segment_dict)

if __name__ == "__main__":
    input_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Input_txtgrid2jsonDER'
    output_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER'

    json_entries = []

    # Parcours tous les fichiers dans le répertoire d'entrée
    for filename in os.listdir(input_directory):
        if filename.endswith(".TextGrid"):
            file_path = os.path.join(input_directory, filename)
            
            # Appelle la fonction pour convertir le fichier TextGrid en format JSON
            textgrid2json(file_path, json_entries)

    output_filename = "hypothesis.json"
    output_path = os.path.join(output_directory, output_filename)

    # Écrit la liste de résultats au format JSON dans le fichier de sortie
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(json_entries, output_file, indent=2)
