from unidecode import unidecode
from jiwer import compute_measures
import json

def process_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    lines = [line.strip() for line in lines]
    segment_list = []
    speaker_wer_dict = {}

    for i in range(12, len(lines), 5):
        file_id_full = lines[i]  
        file_id_parts = file_id_full.split("_")
        file_id = "_".join(file_id_parts[:-2]).strip()

        line_parts = file_id.split("-")
        if len(line_parts) > 3:
            speaker_id = line_parts[3].strip()
        else:
            continue

        hypothesis = lines[i + 3]  
        processed_hypothesis = ' '.join(hypothesis.split(';')).lower().strip()
        processed_hypothesis = unidecode(processed_hypothesis)

        references = lines[i + 1]
        processed_reference = ' '.join(references.split(';')).lower().strip()
        processed_reference = unidecode(processed_reference)

        segment_dict = {
            "file_id": file_id,
            "hypothesis": processed_hypothesis,
            "reference": processed_reference
        }

        segment_list.append(segment_dict)

        if speaker_id not in speaker_wer_dict:
            speaker_wer_dict[speaker_id] = {"total_errors": 0, "total_words": 0, "deletions": 0, "insertions": 0, "substitutions": 0}

        measures = compute_measures(processed_reference, processed_hypothesis)
        error_rate = measures['wer']
        speaker_wer_dict[speaker_id]["total_errors"] += error_rate
        speaker_wer_dict[speaker_id]["total_words"] += len(processed_reference.split())
        speaker_wer_dict[speaker_id]["deletions"] += measures['deletions']
        speaker_wer_dict[speaker_id]["insertions"] += measures['insertions']
        speaker_wer_dict[speaker_id]["substitutions"] += measures['substitutions']

    return segment_list, speaker_wer_dict


file_path = "C:\\Users\\beliz\\Documents\\Cours\\IDL\\IDL M2\\DyLNet\\Data\\Test\\Test.txt"

segment_list, speaker_wer_dict = process_text_file(file_path)

for speaker_id, metrics in speaker_wer_dict.items():
    total_words = metrics["total_words"]
    global_wer = metrics["total_errors"] / total_words * 100
    deletions = metrics["deletions"]
    insertions = metrics["insertions"]
    substitutions = metrics["substitutions"]

    print(f"Speaker {speaker_id}: Global WER = {global_wer:.2f}%, Total Words = {total_words}, Deletions = {deletions}, Insertions = {insertions}, Substitutions = {substitutions}")


