from bs4 import BeautifulSoup
import os
import json
import unicodedata  
import spacy
import string
"""
Ce script ne concerne que les adultes
fichiers d'entrée : .eaf (fichier reference)         
sorties : .json avec annotation tokenisé et normalisé
"""

# Charger le modèle spaCy pour le français
nlp = spacy.load('fr_core_news_sm')

# Fonction pour normaliser l'unicode
def unicode_normalisation(text):
    try:
        return unicode(text, "utf-8")
    except NameError:  
        return str(text)

# Fonction pour supprimer les accents d'une chaîne de caractères
def strip_accents(text):
    text = (
        unicodedata.normalize("NFD", text)
        .encode("ascii", "ignore")
        .decode("utf-8")
    )
    return str(text)

# Fonction pour normaliser le texte en français (mise en minuscules, suppression de la ponctuation)
def normalize_french(text):
    doc = nlp(text.lower())  # Convertir le texte en minuscules
    # Créer une table de traduction qui mappe chaque caractère de ponctuation à None, sauf '<' et '>'
    translator = str.maketrans('', '', string.punctuation.replace('<', '').replace('>', ''))
    # Utiliser la table de traduction pour supprimer la ponctuation de chaque jeton
    return " ".join([token.text.translate(translator) for token in doc])

# Fonction pour convertir le format EAF en format JSON
def eaf2json(file_path, all_results):
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    results = process_eaf_content(xml_content, os.path.splitext(os.path.basename(file_path))[0])
    all_results.extend(results)

# Fonction pour rechercher les fichiers EAF dans un répertoire
def recherche_fichiers_eaf(repertoire):
    fichiers_eaf = []
    
    fichiers = os.listdir(repertoire)
    
    for fichier in fichiers:
        if fichier.endswith('.eaf'):
            parties = fichier.split('-')

            if len(parties) >= 4 and parties[3].startswith('1'):
                fichiers_eaf.append(fichier)

    return fichiers_eaf

# Fonction pour traiter un répertoire EAF
def process_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    fichiers_a_traiter = recherche_fichiers_eaf(input_directory)

    all_results = []  

    for filename in fichiers_a_traiter:
        file_path = os.path.join(input_directory, filename)
        eaf2json(file_path, all_results)

    output_filename = "reference.json"
    output_path = os.path.join(output_directory, output_filename)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(all_results, output_file, indent=2)

# Fonction pour traiter le contenu EAF et extraire les segments
def process_eaf_content(xml_content, file_name):
    soup = BeautifulSoup(xml_content, 'xml')
    
    # Extraire les informations sur les emplacements temporels
    time_slots = {slot['TIME_SLOT_ID']: int(slot['TIME_VALUE']) for slot in soup.find_all('TIME_SLOT')}

    # Extraire les tiers d'annotations et de situations
    annotations_tier = soup.find('TIER', {'TIER_ID': lambda x: x.startswith('*') and x.endswith('_nettoye')})
    situation_tier = soup.find('TIER', {'TIER_ID': 'Activité en cours'})
    
    results = []

    if annotations_tier and situation_tier:
        for annotation, situation_annotation in zip(annotations_tier.find_all('ALIGNABLE_ANNOTATION'), situation_tier.find_all('ALIGNABLE_ANNOTATION')):
            # Extraire les informations spécifiques au segment
            start_time = round(time_slots[annotation['TIME_SLOT_REF1']] / 1000, 2)
            end_time = round(time_slots[annotation['TIME_SLOT_REF2']] / 1000, 2)
            orthographic_transcript = strip_accents(annotation.find('ANNOTATION_VALUE').text)
            orthographic_transcript = normalize_french(orthographic_transcript)
            situation = strip_accents(situation_annotation.find('ANNOTATION_VALUE').text)  
            file_id_parts = file_name.split('-')
            file_id = '-'.join(file_id_parts[:7])
            parts_speaker = file_id.split('-')
            speaker_id = parts_speaker[3].strip()
            class_parts = file_name.split('-')
            class_id = class_parts[0].strip()

            # Créer un dictionnaire pour le segment
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
    input_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Input_eaf2jsonWER'
    output_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Comparaison_WER'

    process_directory(input_directory, output_directory)
