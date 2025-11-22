import json
import os
import glob
import re
from difflib import SequenceMatcher
from jiwer import wer, cer
from fuzzywuzzy import fuzz

# ---------------------------------------------------------
# INPUT FOLDERS
# ---------------------------------------------------------
paddle_folder = "/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/merged_paddle_json_outputs/"
textract_folder = "/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/new_textract_outputs/"

output_csv = "comparison_output.csv"

# ---------------------------------------------------------
# Write CSV Header
# ---------------------------------------------------------
with open(output_csv, "w") as f:
    f.write("file_name,similarity(%),word_error_rate,character_error_rate,average_line_similarity(using fuzzywuzzy)\n")

# ---------------------------------------------------------
# Get all merged Paddle files (image_x.json)
# ---------------------------------------------------------
paddle_files = sorted(glob.glob(os.path.join(paddle_folder, "image_*.json")))

print(f"Found {len(paddle_files)} Paddle merged OCR JSONs.")

for paddle_path in paddle_files:

    file_name = os.path.basename(paddle_path)      # image_11.json
    base = file_name.replace(".json", "")          # image_11

    textract_path = os.path.join(textract_folder, file_name)

    if not os.path.exists(textract_path):
        print(f"⚠ Missing textract file for {file_name}, skipping.")
        continue

    print(f"\nProcessing {file_name}")

    # ---------------------------------------------------------
    # Load merged Paddle JSON
    # ---------------------------------------------------------
    with open(paddle_path, "r", encoding="utf-8") as f:
        paddle = json.load(f)

    paddle_lines = paddle["rec_texts"]   # merged paddles use rec_texts + dt_polys

    # ---------------------------------------------------------
    # Load Textract JSON
    # ---------------------------------------------------------
    with open(textract_path, "r", encoding="utf-8") as f:
        textract = json.load(f)

    textract_lines = [b["Text"] for b in textract if b.get("BlockType") == "LINE"]

    # Convert to strings for overall metrics
    paddle_text = " ".join(paddle_lines)
    textract_text = " ".join(textract_lines)

    # ---------------------------------------------------------
    # Compute Metrics
    # ---------------------------------------------------------

    # Overall text similarity
    similarity = SequenceMatcher(None, paddle_text, textract_text).ratio() * 100

    # Word / character error rate
    word_error = wer(textract_text, paddle_text)
    char_error = cer(textract_text, paddle_text)

    # Average fuzzy line similarity
    scores = []
    for t in textract_lines:
        best = max([fuzz.ratio(t, p) for p in paddle_lines]) if paddle_lines else 0
        scores.append(best)

    avg_line_similarity = sum(scores) / len(scores) if scores else 0

    print("Similarity:", similarity)
    print("WER:", word_error)
    print("CER:", char_error)
    print("Average Line Similarity:", avg_line_similarity)

    # ---------------------------------------------------------
    # Write CSV row
    # ---------------------------------------------------------
    row = f"{base},{similarity},{word_error},{char_error},{avg_line_similarity}\n"

    with open(output_csv, "a") as f:
        f.write(row)

print("\n✓ Metrics saved to", output_csv)
