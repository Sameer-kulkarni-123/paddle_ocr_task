# import os
# import shutil

# # Paths
# textract_root = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/new_textract_outputs"
# to_send_root  = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/to_send"

# # Make sure output exists
# os.makedirs(to_send_root, exist_ok=True)

# for file in os.listdir(textract_root):

#     if not file.endswith(".json"):
#         continue

#     # Example: image_1.json → prefix = image_1
#     prefix = file.replace(".json", "")

#     src_path = os.path.join(textract_root, file)
#     dest_folder = os.path.join(to_send_root, prefix)

#     # Only move if corresponding folder exists
#     if not os.path.isdir(dest_folder):
#         print(f"[SKIP] No folder for {prefix}")
#         continue

#     # Rename to image_x_textract.json
#     new_name = f"{prefix}_textract.json"
#     dest_path = os.path.join(dest_folder, new_name)

#     shutil.copy(src_path, dest_path)
#     print(f"✓ {file} → {dest_path}")

# print("\n✨ Done! Textract JSON files placed into to_send folders.")

# import os
# import shutil

# viz_root = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/viz_new_textract_json"
# to_send_root = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/to_send"

# # ensure destination exists
# os.makedirs(to_send_root, exist_ok=True)

# # loop over each "image_x" folder in viz_new_textract_json
# for folder in os.listdir(viz_root):

#     folder_path = os.path.join(viz_root, folder)

#     # skip the temp image folder
#     if folder == "_temp_images":
#         continue

#     if not os.path.isdir(folder_path):
#         continue

#     if not folder.startswith("image_"):
#         continue

#     print(f"\nProcessing {folder} ...")

#     # destination folder
#     dest_folder = os.path.join(to_send_root, folder)
#     os.makedirs(dest_folder, exist_ok=True)

#     # process each HTML inside this folder
#     for file in os.listdir(folder_path):

#         if not file.endswith(".html"):
#             continue

#         src = os.path.join(folder_path, file)

#         # remove .html → add _textract.html
#         base = file.replace(".html", "_textract.html")

#         dst = os.path.join(dest_folder, base)

#         shutil.copy(src, dst)

#         print(f"  ✓ {file} → {base}")
#     # breakpoint()

# print("\n✨ Done! All HTMLs moved & renamed into to_send.")

import os
import shutil

media_root = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/pdfs_and_imgs_from_s3"
to_send_root = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/to_send"

# ensure output exists
os.makedirs(to_send_root, exist_ok=True)

for file in os.listdir(media_root):

    file_path = os.path.join(media_root, file)

    # skip folders
    if os.path.isdir(file_path):
        continue

    # skip page images
    if "page" in file.lower():     # catches _page_1, page2, etc
        continue

    # skip invalid filenames
    if not file.startswith("image_"):
        continue

    # extract prefix e.g. image_1 from "image_1.pdf" or "image_1.jpg"
    prefix = file.split(".")[0]     # image_1

    dest_folder = os.path.join(to_send_root, prefix)
    if not os.path.isdir(dest_folder):
        print(f"[SKIP] No destination folder for {prefix}")
        continue

    # copy the file as-is
    dest_path = os.path.join(dest_folder, file)
    shutil.copy(file_path, dest_path)

    print(f"✓ Copied: {file} → {dest_folder}")
    # breakpoint()

print("\n✨ Done! All non-page images and PDFs copied into to_send.")

