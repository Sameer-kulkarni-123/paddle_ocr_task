import json
import base64
import os
from PIL import Image
import io
from html2image import Html2Image
from pdf2image import convert_from_path


def convert_pdf_to_image(pdf_path, output_folder):
    """Converts first page of PDF to an image (JPG) and returns path."""
    pages = convert_from_path(pdf_path, dpi=300)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    out_path = os.path.join(output_folder, f"{base}_page_1.jpg")
    pages[0].save(out_path, "JPEG")
    print(f"✓ PDF converted to image: {out_path}")
    return out_path


def textract_to_html(json_path, image_path, output_html_path):
    # Load Textract JSON
    with open(json_path, "r") as f:
        data = json.load(f)

    # Load image as base64
    with open(image_path, "rb") as img_f:
        img_bytes = img_f.read()
        img_b64 = base64.b64encode(img_bytes).decode()

    # Get image size
    img = Image.open(io.BytesIO(img_bytes))
    W, H = img.size

    # Extract line-level blocks
    lines = [b for b in data if b.get("BlockType") == "LINE"]

    # Build HTML
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
.box:hover {{
    border-color: yellow;
    background-color: rgba(255, 255, 0, 0.15);
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
        </div>
        """

    html += """
</div>
</body>
</html>
"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✓ Generated HTML: {output_html_path}")


def html_to_png(html_path, output_png_path):
    hti = Html2Image(output_path=os.path.dirname(output_png_path))

    hti.screenshot(
        html_file=html_path,
        save_as=os.path.basename(output_png_path)
    )

    print(f"✓ Converted HTML → PNG: {output_png_path}")


# ---------------------------------------------------
# AUTOMATIC FOLDER SCANNING + PDF HANDLING
# ---------------------------------------------------
textract_folder = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/new_textract_outputs"
images_folder = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/pdfs_and_imgs_from_s3"
viz_output = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/viz_new_textract_json"

os.makedirs(viz_output, exist_ok=True)

# List JSONs and media files
json_files = sorted(f for f in os.listdir(textract_folder) if f.endswith(".json"))
media_files = sorted(f for f in os.listdir(images_folder) if f.lower().endswith((".jpg", ".jpeg", ".png", ".pdf")))

# Helper: extract base "image_XX"
def get_key(filename):
    return filename.split(".")[0]  # image_12_page_1


# Pair images to JSON
media_map = {}

for f in media_files:
    original_path = os.path.join(images_folder, f)

    if f.lower().endswith(".pdf"):
        # Convert PDF → JPEG only once
        jpg_path = convert_pdf_to_image(original_path, images_folder)
        media_map[jpg_path.split("/")[-1].split(".")[0]] = jpg_path
    else:
        media_map[get_key(f)] = original_path


# Process Textract JSONs
for json_file in json_files:
    json_key = get_key(json_file)
    json_path = os.path.join(textract_folder, json_file)

    # Try to find matching image (starts with same prefix)
    matched_image_path = None
    for k, v in media_map.items():
        if k.startswith(json_key):
            matched_image_path = v
            break

    if not matched_image_path:
        print(f"[WARN] No media found for {json_file}")
        continue

    base = os.path.splitext(os.path.basename(matched_image_path))[0]

    html_out = os.path.join(viz_output, f"{base}_textract_visualized.html")
    png_out  = os.path.join(viz_output, f"{base}_textract_visualized.png")

    textract_to_html(json_path, matched_image_path, html_out)
    html_to_png(html_out, png_out)








