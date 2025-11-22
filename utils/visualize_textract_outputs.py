import json
import base64
import os
from PIL import Image
import io
from pdf2image import convert_from_path


def convert_pdf_to_images(pdf_path, temp_folder):
    """Converts ALL pages of a PDF to JPGs."""
    pages = convert_from_path(pdf_path, dpi=300)
    base = os.path.splitext(os.path.basename(pdf_path))[0]

    image_paths = []

    for page_num, page in enumerate(pages, start=1):
        out_path = os.path.join(temp_folder, f"{base}_page_{page_num}.jpg")
        page.save(out_path, "JPEG")
        image_paths.append(out_path)
        print(f"✓ PDF page {page_num} → {out_path}")

    return image_paths  # return list of all pages!


def textract_to_html(json_data, image_path, output_html_path):
    """Generate the HTML visualization overlay using Textract JSON + ONE image."""

    # Load original image as base64
    with open(image_path, "rb") as img_f:
        img_bytes = img_f.read()
        img_b64 = base64.b64encode(img_bytes).decode()

    # Measure image size
    img = Image.open(io.BytesIO(img_bytes))
    W, H = img.size

    # Extract line blocks
    lines = [b for b in json_data if b.get("BlockType") == "LINE"]

    # HTML template
    html = f"""
<html>
<head>
<title>Textract Visualization</title>
<style>
body {{
    background: #111;
    font-family: Arial, sans-serif;
}}
.container {{
    position: relative;
    width: {W}px;
    margin: 20px auto;
}}
img {{
    width: {W}px;
    display: block;
}}
.box {{
    position: absolute;
    border: 2px solid #00eaff;
    background-color: rgba(0, 200, 255, 0.1);
    color: #fff;
    font-size: 12px;
    padding: 1px;
}}
</style>
</head>
<body>
<div class="container">
<img src="data:image/jpeg;base64,{img_b64}">
"""

    # Add bounding boxes
    for line in lines:
        bb = line["Geometry"]["BoundingBox"]
        left = bb["Left"] * W
        top = bb["Top"] * H
        w = bb["Width"] * W
        h = bb["Height"] * H

        text = line["Text"].replace("&", "&amp;").replace("<", "&lt;")

        html += f"""
<div class="box" style="left:{left}px; top:{top}px; width:{w}px; height:{h}px;">
{text}
</div>"""

    html += """
</div>
</body>
</html>
"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Saved HTML: {output_html_path}")


# ---------------------------------------------------
# AUTOMATIC SCANNING + OUTPUT STRUCTURE
# ---------------------------------------------------
textract_folder = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/new_textract_outputs"
media_folder = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/pdfs_and_imgs_from_s3"
output_root = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/viz_new_textract_json"

os.makedirs(output_root, exist_ok=True)

json_files = sorted(f for f in os.listdir(textract_folder) if f.endswith(".json"))
media_files = sorted(f for f in os.listdir(media_folder)
                     if f.lower().endswith((".jpg", ".jpeg", ".png", ".pdf")))


# Create temp folder for PDF page images
temp_img_folder = os.path.join(output_root, "_temp_images")
os.makedirs(temp_img_folder, exist_ok=True)


# Map: image_name → list of image paths (handles multipage)
media_map = {}

for f in media_files:
    path = os.path.join(media_folder, f)
    key = f.split(".")[0]  # e.g. image_12

    if f.lower().endswith(".pdf"):
        image_list = convert_pdf_to_images(path, temp_img_folder)
        media_map[key] = image_list  # multiple pages
    else:
        media_map[key] = [path]      # single page wrapped in list for consistency


# MAIN LOOP
for json_file in json_files:

    key = json_file.replace(".json", "")  # image_12
    json_path = os.path.join(textract_folder, json_file)

    if key not in media_map:
        print(f"[WARN] No media found for {json_file}")
        continue

    # Load textract JSON only once
    with open(json_path, "r") as f:
        json_data = json.load(f)

    # Create output folder for this document
    out_folder = os.path.join(output_root, key)
    os.makedirs(out_folder, exist_ok=True)

    page_images = media_map[key]

    # Generate 1 HTML file per image page
    for page_num, img_path in enumerate(page_images, start=1):
        html_out = os.path.join(out_folder, f"{key}_page_{page_num}.html")
        textract_to_html(json_data, img_path, html_out)
