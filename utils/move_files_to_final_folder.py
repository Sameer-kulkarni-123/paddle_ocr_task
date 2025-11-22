import os
import shutil
import re

# paths
input_root = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/full_output_pipeline_new_imgs_from_s3"
output_root = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/to_send"

os.makedirs(output_root, exist_ok=True)

# prefix pattern that matches image_x or image_x_y_z
prefix_pattern = re.compile(r"(image_\d+(?:_\d+_\d+)?)")

# loop folders
for folder in os.listdir(input_root):

    folder_path = os.path.join(input_root, folder)

    # skip non-folders
    if not os.path.isdir(folder_path):
        continue

    # skip broken folders
    if folder.startswith("(broken)"):
        continue

    # skip image_1 to image_10
    # if folder.startswith("image_"):
    #     try:
    #         num = int(folder.split("_")[1])
    #         if 1 <= num <= 10:
    #             continue
    #     except:
    #         continue

    print(f"\nProcessing: {folder}")

    # create destination folder
    dest_folder = os.path.join(output_root, folder)
    os.makedirs(dest_folder, exist_ok=True)

    for file in os.listdir(folder_path):

        file_path = os.path.join(folder_path, file)

        # match prefix image_x OR image_x_y_z
        m = prefix_pattern.match(file)
        if not m:
            continue

        prefix = m.group(1)

        # -------------------------
        # 1) JSON files → _paddle.json
        # -------------------------
        if file.endswith(".json"):
            new_name = f"{prefix}_paddle.json"
            shutil.copy(file_path, os.path.join(dest_folder, new_name))
            print(f"  ✓ JSON: {file} → {new_name}")
            continue

        # -------------------------
        # 2) OCR result images → _paddle.png/jpg
        # -------------------------
        if "ocr_res_img" in file:
            ext = os.path.splitext(file)[1]  # .png or .jpg
            new_name = f"{prefix}_paddle{ext}"
            shutil.copy(file_path, os.path.join(dest_folder, new_name))
            print(f"  ✓ OCR IMG: {file} → {new_name}")
            continue

        # -------------------------
        # Everything else is ignored
        # -------------------------

print("\n✨ Done! Only JSON + OCR IMG files copied into:", output_root)
