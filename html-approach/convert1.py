import pdfplumber
import pandas as pd

pdf_path = 'input.pdf'

def extract_fields_from_line(line, field_specs):
    fields = []
    for start, end in field_specs:
        fields.append(line[start:end].strip())
    return fields

def split_into_columns(records, field_specs, num_columns=12):
    all_columns = []
    current_record = []

    for record in records:
        if record.startswith("IAD"):
            # Save the previous record if it exists
            if current_record:
                all_columns.append(current_record)
            # Start a new record
            current_record = extract_fields_from_line(record, field_specs)
        else:
            # Continuation of the last field onto the next line
            current_record[-1] += " " + record.strip()

    # Add the last record
    all_columns.append(current_record)

    # Ensure all records have the required number of columns
    for record in all_columns:
        while len(record) < num_columns:
            record.append('')

    return all_columns

records = []

field_specs = [
    (0, 12),   # Column 1: characters 1-12
    (13, 35),  # Column 2: characters 14-35
    (36, 51),  # Column 3: characters 37-51

]

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            page_records = text.split("\n")
            columns = split_into_columns(page_records, field_specs)
            records.extend(columns)

df = pd.DataFrame(records, columns=[f'Column{i+1}' for i in range(len(field_specs))])

excel_path = 'output1.xlsx'
df.to_excel(excel_path, index=False)

excel_path
