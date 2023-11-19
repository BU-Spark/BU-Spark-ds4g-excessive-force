import argparse
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

    for record in records[1:]:
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

def parse_file(filename):
    columns = []
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            chars = page.extract_words()
            text = page.extract_text()
            counter = 0
            for word in chars:
                if "IAD" not in word["text"]
                    field_specs[] +word
            if text:
                page_records = text.split("\n")
                columns = split_into_columns(page_records, field_specs)
                records.extend(columns)
    print(columns)
    df = pd.DataFrame(records, columns=[f'Column{i+1}' for i in range(len(field_specs))])

    # with open(filename, 'r') as file:
    #     content = file.read()

    # # Splitting the content into records
    # records = re.split(r'IAD\d{4}-\d{4}', content)[1:]
    # records = ['IAD' + re.findall(r'IAD\d{4}-\d{4}', content)[i] + record for i, record in enumerate(records)]

    # # Parsing each record
    # parsed_records = [parse_record(record) for record in records]

    # return parsed_records


# excel_path = 'output1.xlsx'
# df.to_excel(excel_path, index=False)

# excel_path


def main():
    # Usage
    #parsed_records = parse_file('calibre-converted-BPD-IAD-complaints-2019-partial.txt')
    #export_to_csv(parsed_records, 'output.csv')

    parser = argparse.ArgumentParser(description='Parse a file and export to CSV.')
    parser.add_argument('input_file', default="BPD IAD complaints 2019.pdf", help='The file to parse.')
    parser.add_argument('-o', '--output_file', default='output.csv', help='The output CSV file. Defaults to "output.csv".')
    args = parser.parse_args()

    parsed_records = parse_file(args.input_file)
    #export_to_csv(parsed_records, args.output_file)

if __name__ == "__main__":
    main()