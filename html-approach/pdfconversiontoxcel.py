import pdfplumber
import pandas as pd

pdf_path = 'input.pdf'


def split_into_columns(line, num_columns=12):
    columns = line.split()

    while len(columns) < num_columns:
        columns.append('')

    while len(columns) > num_columns:
        columns[-2] += ' ' + columns[-1]
        columns.pop()
    return columns


records = []


with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            for record in text.split(" IAD"):
  
                if record.strip():
                    record = "IAD" + record if not record.startswith("IAD") else record
                    records.append(split_into_columns(record))


df = pd.DataFrame(records, columns=[f'Column{i+1}' for i in range(12)])


excel_path = 'output.xlsx'
df.to_excel(excel_path, index=False)

excel_path
