from bs4 import BeautifulSoup
import os
import json

def eaf2json(file_path, output_directory):
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    
    results = process_eaf_content(xml_content)

    
    filename = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = f"{filename}.json"
    output_path = os.path.join(output_directory, output_filename)

    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(results, output_file, indent=2)

def process_directory(input_directory, output_directory):
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    
    for filename in os.listdir(input_directory):
        if filename.endswith(".eaf"):
            file_path = os.path.join(input_directory, filename)
            eaf2json(file_path, output_directory)

def process_eaf_content(xml_content):
    soup = BeautifulSoup(xml_content, 'xml')

    
    file_id = os.path.splitext(soup.find('HEADER').find('MEDIA_DESCRIPTOR')['RELATIVE_MEDIA_URL'].split('/')[-1])[0]

    time_slots = {slot['TIME_SLOT_ID']: int(slot['TIME_VALUE']) for slot in soup.find_all('TIME_SLOT')}
    
    
    annotations_nettoye = soup.find('TIER', {'TIER_ID': lambda x: x.endswith('_nettoye')})

    
    results = []

    for annotation_nettoye in annotations_nettoye.find_all('ALIGNABLE_ANNOTATION'):
        start_time_nettoye = round(time_slots[annotation_nettoye['TIME_SLOT_REF1']] / 1000, 2)
        end_time_nettoye = round(time_slots[annotation_nettoye['TIME_SLOT_REF2']] / 1000, 2)
        orthographic_transcript_nettoye = annotation_nettoye.find('ANNOTATION_VALUE').text

        
        segment_dict = {
            "file_id": file_id,
            "start_time": start_time_nettoye,
            "end_time": end_time_nettoye,
            "duration": end_time_nettoye - start_time_nettoye,
            "orthographic_transcript": orthographic_transcript_nettoye
        }

        
        results.append(segment_dict)

    return results

if __name__ == "__main__":
    input_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Test'
    output_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\reference'

    process_directory(input_directory, output_directory)
