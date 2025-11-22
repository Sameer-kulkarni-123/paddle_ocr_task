from paddleocr import TableCellsDetection
model = TableCellsDetection(model_name="RT-DETR-L_wired_table_cell_det")
output = model.predict(r"images/1762946413_S1-2526-0041654--SALE--KalpavrikshaAyurveda.pdf", threshold=0.3, batch_size=1)
for res in output:
    res.print(json_format=False)
    res.save_to_img("./output/")
    res.save_to_json("./output/table_cell_detection_modeule_res.json")