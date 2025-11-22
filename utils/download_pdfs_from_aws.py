import os
import json
import requests

def download_file(url, output_folder, index):
    os.makedirs(output_folder, exist_ok=True)

    # Detect file extension from URL
    if "." in url.split("/")[-1]:
        ext = url.split("/")[-1].split(".")[-1]
    else:
        ext = "bin"  # fallback

    file_path = os.path.join(output_folder, f"image_{index}.{ext}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)
            print(f"[OK] Downloaded → {file_path}")
        else:
            print(f"[ERROR] Failed {url} → Status {response.status_code}")

    except Exception as e:
        print(f"[ERROR] Exception while downloading {url}: {e}")


# --------------------------------------------------
# MAIN SCRIPT (JSONL iterator)
# --------------------------------------------------

jsonl_file = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/combined_textract.jsonl"          # path to your jsonl file
output_folder = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/pdfs_and_imgs_from_s3"  # where to save
index = 1

with open(jsonl_file, "r") as f:
    for line in f:
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            url = obj.get("filename")

            if url:
                download_file(url, output_folder, index)
                index += 1
            else:
                print("[WARN] No filename found in:", obj)

        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON:", line)
