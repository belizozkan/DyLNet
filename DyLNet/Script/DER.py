import os
from pyannote.core import Segment, Annotation
from pyannote.metrics.diarization import DiarizationErrorRate
import json

def load_annotation_from_json(json_file):

    annotation = Annotation()
    with open(json_file, 'r') as file:
        data = json.load(file)
        for segment_data in data:
            start_time = segment_data.get('start_time', 0)
            end_time = segment_data.get('end_time', 0)
            segment = Segment(start_time, end_time)
            label = str(segment_data.get('orthographic_transcript', ''))
            annotation[segment] = label
    return annotation

def compare_diarization(reference_annotation, hypothesis_annotation):

    metric = DiarizationErrorRate()

    value = metric(reference_annotation, hypothesis_annotation)

    components = metric(reference_annotation, hypothesis_annotation, detailed=True)

    accumulated_components = metric[:]

    return value, components, accumulated_components

def main(folder_path):

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):

            file_identifier = filename.split('-')[-1].split('.')[0]

            if file_identifier == "R_VD_LEXC":

                reference_file = os.path.join(folder_path, filename)

                system_identifier = "M"
                system_file = os.path.join(folder_path, filename.replace("R_VD_LEXC", system_identifier))

                print(f"Reference File: {reference_file}")
                print(f"System File: {system_file}")

                print(f"Directory content after attempting to construct system file path: {os.listdir(folder_path)}")

                if os.path.exists(system_file):
                    reference_annotation = load_annotation_from_json(reference_file)
                    system_annotation = load_annotation_from_json(system_file)

                    value, components, accumulated_components = compare_diarization(reference_annotation, system_annotation)
                    print(f"Comparison between {reference_file} and {system_file}:")
                    print(f"Diarization Error Rate: {value}")
                    print("Detailed Components:", components)
                    print("Accumulated Components:", accumulated_components)
                    print("===========================================")
                else:
                    print(f"System file not found for reference file: {reference_file}")

if __name__ == "__main__":
    folder_path = "C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Output"
    main(folder_path)
