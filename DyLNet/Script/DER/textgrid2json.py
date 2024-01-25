import os
import json
from praatio import tgio

def textgrid2json(file_path, output_directory):
    tg = tgio.openTextgrid(file_path)


    tier_name = "silences"  
    tier = tg.tierDict[tier_name]


    file_id = os.path.splitext(os.path.basename(file_path))[0]


    json_entries = []

    for entry in tier.entryList:
        start_time = round(entry[0], 2)  
        end_time = round(entry[1], 2)    
        orthographic_transcript = entry[2]
        duration = end_time - start_time

        
        segment_dict = {
            "file_id": file_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
            "orthographic_transcript": orthographic_transcript
        }

        
        json_entries.append(segment_dict)

    
    output_filename = f"{file_id}.json"
    output_path = os.path.join(output_directory, output_filename)

    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(json_entries, output_file, indent=2)

if __name__ == "__main__":
    input_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Test'
    output_directory = 'C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\generated'

    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    
    for filename in os.listdir(input_directory):
        if filename.endswith(".TextGrid"):
            file_path = os.path.join(input_directory, filename)
            textgrid2json(file_path, output_directory)
