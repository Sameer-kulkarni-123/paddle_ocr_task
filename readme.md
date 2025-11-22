# OCR Pipeline Instructions

## 1. Install PaddlePaddle
Download the appropriate PaddlePaddle version from:
https://www.paddlepaddle.org.cn/en/install/quick?docurl=/documentation/docs/en/develop/install/pip/linux-pip_en.html

------------------------------------------------------------

## 2. Pipeline Steps

### Step 1: Download test images from AWS
Run:
    ```python3 utils/download_pdfs_from_aws.py```

### Step 2: Convert downloaded PDFs to images (PaddleOCR accepts only images)
Run:
    ```python3 utils/pdf_to_img.py```

### Step 3: Run Paddle inference on test images
Run:
    ```python3 full_ocr_pipeline.py```

Outputs for this step are already available in:
    /full_output_pipeline_new_imgs_from_s3

Benchmark results saved as:
    benchmark_results.xlsx

### Step 4: Merge multiple Paddle JSON files for multi-page PDFs
(Paddle creates one JSON per image; Textract creates one JSON per PDF)
Run:
    ```python3 utils/merge_multiple_paddle_json.py```

### Step 5: Extract corresponding Textract output JSONs
Run:
    ```python3 utils/extract_json_from_combined_textract_jsonl.py```

### Step 6: Compare Paddle output with Textract output
Run:
    ```python3 utils/common_json.py```

------------------------------------------------------------

## 3. Folder Structure
Each folder inside /full_output_pipeline_new_imgs_from_s3 contains:

1) Layout detection output:
       *_layout_det_res.png

2) Table text detection output:
       *_ocr_res_img.png

3) Full pipeline outputs:
       *_res.json
       *_table_1.html
       *_table_1.xlsx

------------------------------------------------------------

## 4. Visualize Textract Output
Run:
    ```python3 utils/visualize_textract_outputs.py```

Results will be stored in:
    /viz_new_textract_json
as .html files.
