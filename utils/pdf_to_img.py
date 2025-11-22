from pdf2image import convert_from_path

# Path to PDF
pdf_path = r"/mnt/c/Users/Sameer/MyProjects/pharmacy1/paddleOCR/images/pdf2.pdf"

# Convert PDF to a list of PIL images (one per page)
images = convert_from_path(pdf_path, dpi=300)
print("hi")

# Save each page as JPG
for i, img in enumerate(images):
    img.save(f"image_12_page_{i+1}.jpg", "JPEG")
