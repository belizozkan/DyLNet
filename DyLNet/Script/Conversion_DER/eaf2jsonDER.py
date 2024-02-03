from bs4 import BeautifulSoup
import os
import json
import unicodedata  
"""
Ce script concerne les enfants et les adultes
fichiers d'entrée : .eaf (fichier reference)         
sorties : .json 
"""
def unicode_normalisation(text):
    try:
        return unicode(text, "utf-8")
    except NameError:  
        return str(text)

def strip_accents(text):
    # Normalise les caractères accentués
    text = (
        unicodedata.normalize("NFD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )
    return str(text)

def eaf2json(file_path, all_results):
    # Lit le contenu du fichier EAF et le transforme en JSON
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    results = process_eaf_content(xml_content, os.path.splitext(os.path.basename(file_path))[0])
    all_results.extend(results)

def recherche_fichiers_eaf(repertoire):
    fichiers_eaf = []
    
    fichiers = os.listdir(repertoire)
    
    # Filtre les fichiers avec l'extension .eaf
    for fichier in fichiers:
        if fichier.endswith('.eaf'):
            fichiers_eaf.append(fichier)
    
    return fichiers_eaf

def process_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    fichiers_a_traiter = recherche_fichiers_eaf(input_directory)

    all_results = []  

    # Traite chaque fichier EAF dans le répertoire d'entrée
    for filename in fichiers_a_traiter:
        file_path = os.path.join(input_directory, filename)
        eaf2json(file_path, all_results)

    output_filename = "reference.json"
    output_path = os.path.join(output_directory, output_filename)

    # Écrit la liste de résultats au format JSON dans le fichier de sortie
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(all_results, output_file, indent=2)
    
def process_eaf_content(xml_content, file_name):
    soup = BeautifulSoup(xml_content, 'xml')
    
    # Obtient les informations sur les emplacements temporels
    time_slots = {slot['TIME_SLOT_ID']: int(slot['TIME_VALUE']) for slot in soup.find_all('TIME_SLOT')}

    # Récupère les annotations et les annotations de situation depuis le fichier EAF
    annotations_tier = soup.find('TIER', {'TIER_ID': lambda x: x.startswith('*') and x.endswith('_nettoye')})
    situation_tier = soup.find('TIER', {'TIER_ID': 'Activité en cours'})
    
    results = []

    # Vérifie que les tiers d'annotations et de situations existent
    if annotations_tier and situation_tier:
        # Associe chaque annotation avec son annotation de situation respective
        for annotation, situation_annotation in zip(annotations_tier.find_all('ALIGNABLE_ANNOTATION'), situation_tier.find_all('ALIGNABLE_ANNOTATION')):
            start_time = round(time_slots[annotation['TIME_SLOT_REF1']] / 1000, 2)
            end_time = round(time_slots[annotation['TIME_SLOT_REF2']] / 1000, 2)
            orthographic_transcript = strip_accents(annotation.find('ANNOTATION_VALUE').text)  
            situation = strip_accents(situation_annotation.find('ANNOTATION_VALUE').text)  
            file_id_parts = file_name.split('-')
            file_id = '-'.join(file_id_parts[:7])
            parts_speaker = file_id.split('-')
            speaker_id = parts_speaker[3].strip()
            class_parts = file_name.split('-')
            class_id = class_parts[0].strip()

            # Crée un dictionnaire pour chaque segment et l'ajoute à la liste de résultats
            segment_dict = {
                "file_id": file_id,
                "speaker_id": speaker_id,
                "class_id": class_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "transcript": orthographic_transcript,
                "situation": situation
            }

            results.append(segment_dict)

    return results

# Programme principal
if __name__ == "__main__":
    input_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Input_eaf2jsonDER'
    output_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_DER'

    # Appelle la fonction pour traiter le répertoire d'entrée et générer le fichier JSON de sortie
    process_directory(input_directory, output_directory)
