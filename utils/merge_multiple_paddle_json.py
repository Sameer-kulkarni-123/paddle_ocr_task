import json
import glob
import os

# Input root folder where image_x folders exist
input_root = "/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/full_output_pipeline_new_imgs_from_s3/"

# Output folder to store merged JSON files
output_root = "/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/merged_paddle_json_outputs/"
os.makedirs(output_root, exist_ok=True)

# Get all image folders
image_folders = sorted(glob.glob(os.path.join(input_root, "image_*")))

print("Found folders:", image_folders)

for folder in image_folders:

    image_id = os.path.basename(folder)  # e.g., "image_11"
    print(f"\nProcessing {image_id}...")

    # Find all page-wise jsons e.g., *_page_1_res.json
    page_jsons = sorted(glob.glob(os.path.join(folder, "*_res.json")))

    if not page_jsons:
        print(f"⚠ No PaddleOCR res.json files found in {folder}")
        continue

    merged_polys = []
    merged_texts = []

    for jfile in page_jsons:
        print(f"  - Merging: {jfile}")

        with open(jfile, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Append polys and texts
        merged_polys.extend(data["overall_ocr_res"]["dt_polys"])
        merged_texts.extend(data["overall_ocr_res"]["rec_texts"])

    # Build merged output structure
    merged_output = {
        "image_name": image_id,
        "dt_polys": merged_polys,
        "rec_texts": merged_texts
    }

    # Save merged JSON
    out_path = os.path.join(output_root, f"{image_id}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(merged_output, f, indent=2)

    print(f"✓ Saved merged JSON: {out_path}")
