from paddleocr import TableRecognitionPipelineV2
import os
import time
import psutil
import pynvml
import openpyxl
from openpyxl import Workbook

temp_start = time.time() #temp

# ---------------------------
# Initialize GPU Monitoring (NVIDIA)
# ---------------------------
pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)  # GPU 0

def get_gpu_stats():
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    return mem.used / 1024**2, util.gpu  # MB, %

# ---------------------------
# Initialize Data Logging
# ---------------------------
wb = Workbook()
ws = wb.active
ws.title = "Benchmark"

ws.append([
    "Image Name",
    "Processing Time (sec)",
    "GPU VRAM Before (MB)",
    "GPU VRAM After (MB)",
    "GPU VRAM Used Delta (MB)",
    "GPU Load (%)",
    "CPU Load (%)",
    "RAM Usage (%)",
])

# ---------------------------
# Initialize OCR Pipeline
# ---------------------------
pipeline = TableRecognitionPipelineV2(device="gpu")

# Folder paths
input_folder = "pdfs_and_imgs_from_s3"
output_root = "full_output_pipeline_new_imgs_from_s3"
os.makedirs(output_root, exist_ok=True)

# Extensions allowed
valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"}

temp_end = time.time()
print(f"The time taken to load the model: {temp_end - temp_start}")

# Global timing
global_start = time.time()
num_images = 0
total_gpu = []
total_cpu = []

# ---------------------------
# Process Each Image
# ---------------------------
for filename in os.listdir(input_folder):
    try:
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in valid_exts:
            continue

        num_images += 1
        img_path = os.path.join(input_folder, filename)
        base_name = os.path.splitext(filename)[0]

        print(f"\n🔄 Processing: {filename}")

        output_dir = os.path.join(output_root, base_name)
        os.makedirs(output_dir, exist_ok=True)

        # System stats BEFORE
        gpu_before, _ = get_gpu_stats()
        cpu_before = psutil.cpu_percent(interval=None)
        ram_before = psutil.virtual_memory().percent

        # Measure time
        start_time = time.time()

        # Run OCR
        output = pipeline.predict(img_path)

        # Measure end time
        end_time = time.time()
        process_time = end_time - start_time

        # System stats AFTER
        gpu_after, gpu_load = get_gpu_stats()
        cpu_after = psutil.cpu_percent(interval=None)
        ram_after = psutil.virtual_memory().percent

        # Save OCR outputs
        for res in output:
            res.save_to_img(output_dir)
            res.save_to_xlsx(output_dir)
            res.save_to_html(output_dir)
            res.save_to_json(output_dir)

        # Logging
        gpu_delta = gpu_after - gpu_before
        avg_cpu = (cpu_before + cpu_after) / 2
        avg_ram = (ram_before + ram_after) / 2

        ws.append([
            filename,
            process_time,
            gpu_before,
            gpu_after,
            gpu_delta,
            gpu_load,
            avg_cpu,
            avg_ram,
        ])

        total_gpu.append(gpu_load)
        total_cpu.append(avg_cpu)
    except Exception as e:
        print("Error : ", e)

# ---------------------------
# GLOBAL METRICS
# ---------------------------
global_end = time.time()
total_time = global_end - global_start
throughput = num_images / total_time if total_time > 0 else 0

ws.append([])
ws.append(["=== Summary ==="])
ws.append(["Total Images", num_images])
ws.append(["Total Time (sec)", total_time])
ws.append(["Images/sec", throughput])
ws.append(["Avg GPU Load (%)", sum(total_gpu)/len(total_gpu)])
ws.append(["Avg CPU Load (%)", sum(total_cpu)/len(total_cpu)])

# ---------------------------
# Save Excel
# ---------------------------
excel_path = "benchmark_results.xlsx"
wb.save(excel_path)

print(f"\n✅ Benchmark complete!")
print(f"📊 Excel saved at: {excel_path}")
