import csv
import pdfminer
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLine

def extract_columns(pdf_path, x_positions):
    """
    Extracts columns from a PDF based on a set of x-positions.

    :param pdf_path: Path to the PDF file.
    :param x_positions: List of x-positions to define column boundaries.
    :return: Extracted columns as a list of lists.
    """
    columns = [[] for _ in range(len(x_positions) - 1)]
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    chars = []
                    if isinstance(text_line, LTTextLine):
                        for char in text_line:
                            if isinstance(char, LTChar):
                                chars.append(char)
                        current_column = 0
                        line_text = []
                        for char in chars:
                            if current_column < len(x_positions) - 1 and char.x0 > x_positions[current_column + 1]:
                                current_column += 1
                            line_text.append((current_column, char.get_text()))
                        for col_idx, col in enumerate(columns):
                            col_text = ''.join([ch for col_num, ch in line_text if col_num == col_idx])
                            if col_text.strip():
                                col.append(col_text.strip())
                    else:
                        print(type(text_line), " is not iterable: ", text_line)
    return columns

def write_to_csv(columns, output_file):
    """
    Write the extracted columns to a CSV file.

    :param columns: Extracted columns as a list of lists.
    :param output_file: Path to the output CSV file.
    """
    max_length = max(len(col) for col in columns)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        for i in range(max_length):
            row = [col[i] if i < len(col) else '' for col in columns]
            writer.writerow(row)

# Example usage
pdf_path = 'BPD-IAD-complaints-2019-partial.pdf'
x_positions = [14,40,100, 200, 300, 400, 500, 600]  # Replace with your x-positions
columns = extract_columns(pdf_path, x_positions)

output_csv = 'output.csv'  # Path for the output CSV file
write_to_csv(columns, output_csv)

print(f"Data extracted and written to {output_csv}")