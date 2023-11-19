import argparse
import re
import csv

def parse_record(record):
    lines = [line for line in record.strip().split('\n')]
    fields = {
        "IA No": "",
        "Incident Type": "",
        "Received Date": "",
        "Title/Rank (snap)": "",
        "First Name": "",
        "Last Name": "",
        "Allegation": "",
        "Finding": "",
        "Action Taken": "",
        "Action Taken Date": "",
        "Days or Hours Suspended": "",
        "Disposition": "",
        "Priority": "",
        "Occurred Date": "",
        "Description": ""
    }

    # Function to safely get a line
    def get_line(index):
        return lines[index] if index < len(lines) else ''

    def get_2_field_line(index):
        line = lines[index] if index < len(lines) else ''
        parts = line.split(None, 1)
        if len(parts) == 1: parts.append('')
        return tuple(parts)

    # Parsing lines individually
    if len(lines) > 0:
        fields["IA No"], fields["Incident Type"] = get_2_field_line(0) #re.split(r'\s+', get_line(0), maxsplit=1)
        fields["Received Date"], fields["Title/Rank (snap)"] = get_2_field_line(2) #re.split(r'\s+', get_line(2), maxsplit=1)
        fields["First Name"] = get_line(4)
        fields["Last Name"] = get_line(6)
        fields["Allegation"] = get_line(8)
        fields["Finding"] = get_line(10)
        if fields["Finding"] == "Unfounded":
            fields["Disposition"] = get_line(12)
            fields["Priority"] = get_line(14)
            fields["Occurred Date"], partial_description = get_2_field_line(16) #re.split(r'\s+', get_line(16), maxsplit=1)
            # Handling the "Description" field, which may span multiple lines
            description_lines = [partial_description] + lines[17:]
            fields["Description"] = ' '.join(description_lines).strip()
        elif fields["Finding"] == 'Not Sustained':
            fields["Disposition"] = get_line(12)
            fields["Occurred Date"], partial_description = get_2_field_line(14) #re.split(r'\s+', get_line(16), maxsplit=1)
            # Handling the "Description" field, which may span multiple lines
            description_lines = [partial_description] + lines[15:]
            fields["Description"] = ' '.join(description_lines).strip()
        else:
            fields["Action Taken"] = get_line(12)
            fields["Action Taken Date"] = get_line(14)
            fields["Days or Hours Suspended"], fields["Disposition"] = get_2_field_line(16) #re.split(r'\s+', get_line(16), maxsplit=1)
            fields["Occurred Date"], partial_description = get_2_field_line(18) #re.split(r'\s+', get_line(18), maxsplit=1)
            # Handling the "Description" field, which may span multiple lines
            description_lines = [partial_description] + lines[19:]
            fields["Description"] = ' '.join(description_lines).strip()

    return list(fields.values())

def parse_file(filename):
    with open(filename, 'r') as file:
        content = file.read()

    # Splitting the content into records
    records = re.split(r'IAD\d{4}-\d{4}', content)[1:]
    records = ['IAD' + re.findall(r'IAD\d{4}-\d{4}', content)[i] + record for i, record in enumerate(records)]

    # Parsing each record
    parsed_records = [parse_record(record) for record in records]

    return parsed_records

def export_to_csv(parsed_records, output_filename):
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Writing header
        header = ["IA No", "Incident Type", "Received Date", "Title/Rank (snap)", "First Name", "Last Name", "Allegation", "Finding", "Action Taken", "Action Taken Date", "Days or Hours Suspended", "Disposition", "Priority", "Occurred Date", "Description"]
        writer.writerow(header)
        # Writing data
        for record in parsed_records:
            writer.writerow(record)

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




# import re
# import csv

# def parse_record(record):
#     # Split the record into fields
#     fields = re.split(r'\s{2,}', record)

#     # Handle blank 'Action Taken' and 'Action Taken Date' fields
#     if len(fields) == 11:
#         fields.append('')
#         fields.append('')

#     # Handle blank 'Priority' field
#     if len(fields) == 13:
#         fields.append('')

#     # Handle multi-line description
#     if record.endswith('\n'):
#         description = fields[-1]
#         for line in record.splitlines()[2:]:
#             description += ' ' + line

#         fields[-1] = description

#     return fields

# def main():
#     # Open the text file for reading
#     with open('calibre-converted-BPD-IAD-complaints-2019-partial.txt', 'r') as f:
#         # Read the entire file
#         data = f.read()

#     # Split the data into records
#     records = data.split('\n\n')

#     # Parse each record
#     parsed_records = []
#     for record in records:
#         parsed_records.append(parse_record(record))

#     # Export parsed records to CSV file
#     with open('output.csv', 'w', newline='') as csvfile:
#         csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
#         csv_writer.writerow(['IA No', 'Incident Type', 'Received Date', 'Title/Rank (Snap)', 'First Name', 'Last Name', 'Allegation', 'Finding', 'Action Taken', 'Action Taken Date', 'Days/Hours Suspended', 'Disposition', 'Priority', 'Occurred Date', 'Description'])

#         for record in parsed_records:
#             csv_writer.writerow(record)

# if __name__ == '__main__':
#     main()




# # import csv
# # import re

# # # Input and output file paths
# # input_file = 'calibre-converted-BPD-IAD-complaints-2019-partial.txt'
# # output_file = 'output.csv'

# # # Define regular expressions to extract data from each line
# # ia_number_pattern = r'IAD\d{4}-\d+'
# # date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
# # name_pattern = r'[A-Za-z\s]+'
# # allegation_pattern = r'.+'
# # finding_pattern = r'Sustained|Unfounded'
# # action_taken_pattern = r'.*'
# # action_date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'
# # suspension_pattern = r'\d+'
# # disposition_pattern = r'\d'
# # priority_pattern = r'\d'
# # occurred_date_pattern = r'\d{1,2}/\d{1,2}/\d{4}'

# # # Initialize the CSV writer with quotes around string data
# # with open(output_file, 'w', newline='') as csvfile:
# #     csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)

# #     # Write the header row to the CSV file
# #     header = ["IA No", "Incident Type", "Received Date", "Title/ Rank (snap)",
# #               "First Name", "Last Name", "Allegation", "Finding", "Action Taken",
# #               "Action Taken Date", "Days or Hours Suspended", "Disposition", "Priority",
# #               "Occurred Date", "Description"]
# #     csv_writer.writerow(header)

# #     # Read and process the input text file
# #     with open(input_file, 'r') as txtfile:
# #         record = {}
# #         in_description = False
# #         description_lines = []

# #         for line in txtfile:
# #             line = line.strip()

# #             if not line:
# #                 continue

# #             if line.startswith("IA No"):
# #                 if record:
# #                     if in_description:
# #                         record["Description"] = '\n'.join(description_lines)
# #                     csv_writer.writerow([record.get(key, "") for key in header])

# #                 record = {"Description": ""}
# #                 in_description = False
# #                 description_lines = []
# #                 record["IA No"] = re.search(ia_number_pattern, line).group()
# #             elif in_description:
# #                 description_lines.append(line)
# #             else:
# #                 key, pattern = [("Incident Type", "Incident Type"),
# #                                 ("Received Date", date_pattern),
# #                                 ("Title/ Rank (snap)", name_pattern),
# #                                 ("First Name", name_pattern),
# #                                 ("Last Name", name_pattern),
# #                                 ("Allegation", allegation_pattern),
# #                                 ("Finding", finding_pattern),
# #                                 ("Action Taken", action_taken_pattern),
# #                                 ("Action Taken Date", action_date_pattern),
# #                                 ("Days or Hours Suspended", suspension_pattern),
# #                                 ("Disposition", disposition_pattern),
# #                                 ("Priority", priority_pattern),
# #                                 ("Occurred Date", occurred_date_pattern)][0]
# #                 match = re.search(pattern, line)
# #                 if match:
# #                     record[key] = match.group()
# #                 elif key == "Finding" and "Unfounded" not in record:
# #                     record[key] = "Unfounded"
# #                 else:
# #                     in_description = True
# #                     description_lines.append(line)

# #         if record:
# #             if in_description:
# #                 record["Description"] = '\n'.join(description_lines)
# #             csv_writer.writerow([record.get(key, "") for key in header])

# # print("CSV file has been created successfully!")












# # # import re
# # # import csv

# # # def parse_records(filename):
# # #     with open(filename, 'r') as file:
# # #         content = file.read()

# # #     # Splitting the content by the IAD pattern
# # #     records = re.split(r'(IAD\d{4}-\d{4})', content)
# # #     records = [record for record in records if record.strip()]  # Remove empty strings

# # #     parsed_records = []
# # #     current_record = []

# # #     for item in records:
# # #         if item.startswith('IAD'):
# # #             if current_record:
# # #                 parsed_records.append(current_record)
# # #             current_record = [item]

# # #         # else:
# # #         #     # Split the item into lines and remove empty lines
# # #         #     lines = [line.strip() for line in item.split('\n') if line.strip()]
# # #         #     # Split the first line into "Received date" and "Title/rank (snap)" columns
# # #         #     if len(lines) > 1:
# # #         #         received_date, title_rank = lines[1].split(None, 1)
# # #         #         current_record.extend(['"{}"'.format(received_date), '"{}"'.format(title_rank)])
# # #         #         current_record.extend(['"{}"'.format(line) for line in lines[2:]])

# # #         else:
# # #             # Split the item into lines and remove empty lines
# # #             lines = [line.strip() for line in item.split('\n') if line.strip()]
# # #             # Split the first line into "Received date" and "Title/rank (snap)" columns
# # #             if len(lines) > 0:
# # #                 received_date, title_rank = lines[1].split(None, 1)
# # #                 current_record.extend(['"{}"'.format(received_date), '"{}"'.format(title_rank)])
# # #                 current_record.extend(['"{}"'.format(line) for line in lines[1:]])

# # #     # Add column headers
# # #     headers = [
# # #         "IA No",
# # #         "Incident type",
# # #         "Received date",
# # #         "Title/rank (snap)",
# # #         "First name",
# # #         "Last name",
# # #         "Allegation",
# # #         "Finding",
# # #         "Action taken",
# # #         "Action taken date",
# # #         "Days or hours suspended",
# # #         "Disposition",
# # #         "Priority",
# # #         "Occurred date"
# # #     ]

# # #     parsed_records.insert(0, headers)

# # #     return parsed_records

# # # def save_as_csv(parsed_records, output_filename):
# # #     with open(output_filename, 'w', newline='') as csvfile:
# # #         csv_writer = csv.writer(csvfile)
# # #         for row in parsed_records:
# # #             csv_writer.writerow(row)


# # # def main():
# # #     input_filename = 'calibre-converted-BPD-IAD-complaints-2019-partial.txt'
# # #     output_filename = 'output.csv'
# # #     parsed_records = parse_records(input_filename)
# # #     save_as_csv(parsed_records, output_filename)

# # # if __name__ == "__main__":
# # #     main()


