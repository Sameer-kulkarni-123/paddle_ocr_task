
from paddleocr import TableStructureRecognition
model = TableStructureRecognition(model_name="SLANet")
output = model.predict(input=r"images/1762946413_S1-2526-0041654--SALE--KalpavrikshaAyurveda.pdf", batch_size=1)
for res in output:
    res.print(json_format=False)
    res.save_to_json("./output/table_structure_recog_res.json")