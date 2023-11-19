import argparse
from bs4 import BeautifulSoup
import re
import csv

# Function to clean up space issues in text
def clean_text(text):
    if len(text) > 1:
        text = re.sub(r' {2,}', '~~', text)  # Replace two or more spaces with ~~
        text = text.replace(' ', '')  # Remove single spaces
        text = re.sub('~~', ' ', text)  # switch it back to a space
    return text.strip()

# Function to check if a row is completely empty
def is_row_empty(row):
    return all(not value.strip() for value in row.values())

# Function to check if a row is empty except for the Description
def is_empty_except_description(row):
    return all(not value.strip() for key, value in row.items() if key != "Description")




from bs4 import BeautifulSoup
import re
import csv

# Define your field ranges
fields = {
    "IA No": (50, 74),
    "Incident type": (75, 109),
    "Received date": (110, 128),
    "Title/rank (snap)": (129, 160),
    "First name": (161, 189),
    "Last name": (190, 216),
    "Allegation": (217, 306),
    "Finding": (307, 327),
    "Action taken": (328, 398),
    "Action taken date": (399, 448),
    "Days or hours suspended": (449, 451),
    "Disposition": (452, 478),
    "Priority": (479, 493),
    "Occurred date": (494, 512),
    "Description": (513, 707)
}

# Function to clean up space issues in text
def clean_text(text):

# Read the HTML content from 'test.html'
with open('test.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')
elements = soup.find_all('span')  # Replace 'div' with the appropriate tag

# Process elements and group by 'top' position
lines = {}
for element in elements:
    # Extract styles from the element
    element_style = element.get('style')

    # Get left and top positions
    try:
        left = int(re.findall(r'left:([0-9]+)px', element_style)[0])
        top = int(re.findall(r'top:([0-9]+)px', element_style)[0])
    except (IndexError, ValueError):
        continue

    if top not in lines:
        lines[top] = {field: '' for field in fields}

    # Check which field this element belongs to and append its text
    for field, (start, end) in fields.items():
        if start <= left <= end:
            lines[top][field] += element.get_text().strip() + ' '

# Custom column headers
column_headers = [
    "IA No",
    "Incident type",
    "Received date",
    "Title/rank (snap)",
    "First name",
    "Last name",
    "Allegation",
    "Finding",
    "Action taken",
    "Action taken date",
    "Days or hours suspended",
    "Disposition",
    "Priority",
    "Occurred date",
    "Description"
]

# Process rows and merge descriptions if necessary, skip header rows
processed_rows = []

for top, line in sorted(lines.items()):
    clean_line = {field: clean_text(value) for field, value in line.items()}
    if any(clean_line[field].startswith("IA No") for field in fields) or is_row_empty(clean_line):
        continue  # Skip header row
    if processed_rows and is_empty_except_description(clean_line):
        # Merge description with the previous row
        processed_rows[-1]["Description"] += " " + clean_line["Description"]
    else:
        processed_rows.append(clean_line)

# Write results to CSV
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    writer.writerow(fields.keys())  # Write header

    # Write data rows
    for line in processed_rows:
        writer.writerow(line.values())

print("Data written to output.csv")

def main():
    # Usage
    #parsed_records = parse_file('calibre-converted-BPD-IAD-complaints-2019-partial.txt')
    #export_to_csv(parsed_records, 'output.csv')

    parser = argparse.ArgumentParser(description='Parse a file and export to CSV.')
    parser.add_argument('input_file', help='The file to parse.')
    parser.add_argument('-o', '--output_file', default='output.csv', help='The output CSV file. Defaults to "output.csv".')
    args = parser.parse_args()

    parsed_records = parse_file(args.input_file)
    export_to_csv(parsed_records, args.output_file)

if __name__ == "__main__":
    main()
