import json
import glob
import os
from rapidfuzz import fuzz

# ---------------------------------------------------
# Input folders
# ---------------------------------------------------
paddle_folder = "/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/merged_paddle_json_outputs/"
textract_folder = "/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/new_textract_outputs/"
output_folder = "/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/common_json_output/"

os.makedirs(output_folder, exist_ok=True)

# Get all merged paddle files (image_x.json)
paddle_files = sorted(glob.glob(os.path.join(paddle_folder, "image_*.json")))

print(f"Found {len(paddle_files)} merged paddle OCR outputs.")

for paddle_path in paddle_files:

    file_name = os.path.basename(paddle_path)  # e.g., "image_11.json"
    textract_path = os.path.join(textract_folder, file_name)

    if not os.path.exists(textract_path):
        print(f"⚠ Textract output missing for {file_name}, skipping.")
        continue

    print(f"\nProcessing {file_name} ...")

    # ---------------------------------------------------
    # 1. Load merged PaddleOCR output
    # ---------------------------------------------------
    with open(paddle_path, "r", encoding="utf-8") as f:
        paddle = json.load(f)

    paddle_polys = paddle["dt_polys"]
    paddle_texts = paddle["rec_texts"]

    paddle_lines = []
    max_len = min(len(paddle_polys), len(paddle_texts))

    for i in range(max_len):
        poly = paddle_polys[i]
        text = paddle_texts[i].strip()

        xs = [pt[0] for pt in poly]
        ys = [pt[1] for pt in poly]
        bbox = [min(xs), min(ys), max(xs), max(ys)]

        paddle_lines.append({
            "id": f"paddle_{i}",
            "text": text,
            "bbox": bbox,
            "confidence": None
        })

    # ---------------------------------------------------
    # 2. Load Textract output
    # ---------------------------------------------------
    with open(textract_path, "r", encoding="utf-8") as f:
        textract = json.load(f)

    textract_lines = []
    for block in textract:
        if block.get("BlockType") == "LINE":
            bb = block["Geometry"]["BoundingBox"]

            bbox = [
                bb["Left"],
                bb["Top"],
                bb["Left"] + bb["Width"],
                bb["Top"] + bb["Height"]
            ]

            textract_lines.append({
                "id": block["Id"],
                "text": block["Text"].strip(),
                "bbox": bbox,
                "confidence": block.get("Confidence")
            })

    # ---------------------------------------------------
    # 3. Matching Function
    # ---------------------------------------------------
    def find_best_match(paddle_text):
        best = None
        best_score = -1
        for t in textract_lines:
            score = fuzz.ratio(paddle_text, t["text"])
            if score > best_score:
                best_score = score
                best = t
        return best, best_score

    # ---------------------------------------------------
    # 4. Build Comparison JSON
    # ---------------------------------------------------
    paired = []
    only_paddle = []
    used_textract_ids = set()

    MATCH_THRESHOLD = 50  # you can tune this

    for p in paddle_lines:
        best_match, score = find_best_match(p["text"])

        if score >= MATCH_THRESHOLD:
            paired.append({
                "paddle": p,
                "textract": best_match,
                "match_score": score / 100
            })
            used_textract_ids.add(best_match["id"])
        else:
            only_paddle.append({
                "paddle": p,
                "reason": "no matching textract line >= threshold"
            })

    # Textract-only items
    only_textract = [t for t in textract_lines if t["id"] not in used_textract_ids]

    # ---------------------------------------------------
    # 5. Save Output JSON
    # ---------------------------------------------------
    out_path = os.path.join(output_folder, f"{file_name.replace('.json', '')}_comparison_output.json")

    final_json = {
        "image_name": file_name.replace(".json", ""),
        "paired": paired,
        "only_paddle": only_paddle,
        "only_textract": only_textract
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=2)

    print(f"✓ Saved comparison JSON → {out_path}")
