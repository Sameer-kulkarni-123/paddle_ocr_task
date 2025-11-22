import os
import json

input_jsonl = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/combined_textract.jsonl"          # your jsonl file
output_folder = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/new_textract_outputs"         # where to save
os.makedirs(output_folder, exist_ok=True)

index = 1

with open(input_jsonl, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        
        try:
            obj = json.loads(line)

            # Get the "json" field
            data = obj.get("json")

            if data is None:
                print(f"[WARN] No 'json' key in line {index}")
                index += 1
                continue

            # Save as image_X.json
            out_path = os.path.join(output_folder, f"image_{index}.json")

            with open(out_path, "w", encoding="utf-8") as out:
                json.dump(data, out, indent=4, ensure_ascii=False)

            print(f"[OK] Saved → {out_path}")

            index += 1

        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON line, skipping...")
