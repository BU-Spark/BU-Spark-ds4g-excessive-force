import argparse
from bs4 import BeautifulSoup
import re
import csv

# Function to clean up space issues in text
def clean_text(text):
    text = re.sub(r' {2,}', ' ', text)  # Replace two or more spaces with a single space
    text = text.replace(' ', '')  # Remove single spaces
    return text.strip()

# Function to check if a row is completely empty
def is_row_empty(row):
    return all(not value.strip() for value in row.values())

# Function to check if a row is empty except for the Description
def is_empty_except_description(row):
    return all(not value.strip() for key, value in row.items() if key != "Description")

# Process elements and group by 'top' position
def process_elements(elements, fields):
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
    return lines

# Process rows, merge descriptions if necessary, skip header and blank rows
def process_rows(lines, fields):
    processed_rows = []
    for top, line in sorted(lines.items()):
        clean_line = {field: clean_text(value) for field, value in line.items()}
        if any(clean_line[field].startswith("IA No") for field in fields) or is_row_empty(clean_line):
            continue  # Skip header and blank rows
        if processed_rows and is_empty_except_description(clean_line):
            # Merge description with the previous row
            processed_rows[-1]["Description"] += " " + clean_line["Description"]
        else:
            processed_rows.append(clean_line)
    return processed_rows

def main(input_file, output_file):
    # Define your field ranges
    fields = {
        "IA No": (54, 74),
        "Incident type": (75, 112),
        "Received date": (113, 128),
        "Title/rank (snap)": (129, 160),
        # ... add other fields here
        "Description": (513, 707)  # Assuming this is the last field
    }

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

    # Read the HTML content from the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = soup.find_all('div')  # Replace 'div' with the appropriate tag
    lines = process_elements(elements, fields)
    processed_rows = process_rows(lines, fields)

    # Write results to the output file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_headers)  # Write custom headers
        for line in processed_rows:
            writer.writerow(line.values())

    print(f"Data written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse HTML and output to CSV")
    parser.add_argument("input_file", help="Input HTML file")
    parser.add_argument("-o", "--output_file", default="output.csv", help="Output CSV file (default: output.csv)")
    args = parser.parse_args()
    main(args.input_file, args.output_file)
