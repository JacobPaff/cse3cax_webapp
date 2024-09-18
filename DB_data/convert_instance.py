import csv
import json

# Define the months associated with each position
months = [
    "2021-01-01", "2021-02-01", "2021-03-01", "2021-04-01", "2021-05-01", "2021-06-01",
    "2021-07-01", "2021-08-01", "2021-09-01", "2021-10-01", "2021-11-01", "2021-12-01",
    "2022-01-01", "2022-02-01", "2022-03-01", "2022-04-01", "2022-05-01", "2022-06-01",
    "2022-07-01", "2022-08-01", "2022-09-01", "2022-10-01", "2022-11-01", "2022-12-01"
]

# Replace this string with your actual file path or content
csv_data = """CSE1ITX,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X
CSE1PGX,X,X,X,,,,X,X,X,,,,X,X,X,,,,X,X,X,,,
CSE1CFX,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X
CSE1OFX,X,X,X,,,,X,X,X,,,,X,X,X,,,,X,X,X,,,
CSE1ISX,X,,,X,X,X,,,,X,X,X,,,,X,X,X,,,,X,X,X
CSE2NFX,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X
CSE2DCX,,X,,X,X,X,,,,X,X,X,,,,X,X,X,,,,X,X,X
CSE1SPX,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X
CSE1SIX,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X,X
CSE1IOX,X,X,X,,,,X,X,X,,,,X,X,X,,,,X,X,X,,,
CSE2ICX,,X,X,,,,,X,,,,,,X,,,,,,X,,,,
CSE2CNX,,,,,X,,,X,,,X,,,X,,,X,,,X,,,X,
CSE2SDX,,,,,X,,,X,,,X,,,,,,X,,,,,,X,
BUS2PMX,,X,X,X,X,,,X,,,X,X,X,,,,X,,,,X,X,X,
CSE2VVX,,X,,,X,,,,,,X,,,,,,X,,,,,,X,
MAT2DMX,,X,,,X,,,X,,,,,,X,,,,,,X,,,,
CSE2MAX,,X,,,X,,,,,,X,,,,,,X,,,,,,X,
CSE2OSX,,X,,,X,,,,,,X,,,,,,X,,,,,,X,
CSE2ADX,,,,,X,,,,,,X,,,,,,X,,,,,,X,
CSE2CPX,,X,,,,,,,,X,,,,X,,,,,X,,,,,
CSE2MLX,,X,,,X,,,,,,,,,X,,,X,,,,,,,
CSE2SAX,,X,,,X,,,X,,,X,,,X,,,X,,,X,,,X,
CSE2ANX,,X,,,X,,,X,,,X,,,X,,,X,,,X,,,X,
CSE2WDX,,X,,,X,,,X,,,X,,,X,,,X,,,X,,,X,
CSE3BGX,,X,,,,,,X,,,,,,X,,,,,,X,,,,
CSE3CIX,,,,,,,,X,,,,,,,,,X,,,,,,,
CSE3CSX,,X,,,,,,,,,X,,,,,,X,,,,,,X,
CSE3NWX,,,,,X,,,,,,X,,,,,,,,,X,,,,
CSE3OTX,,X,,,,,,X,,,,,,X,,,,,,X,,,,
CSE3WSX,,,,,X,,,,,,,,,X,,,,,,,,,X,
CSE3PAX,,X,,,X,,,X,,,X,,,X,,,X,,,X,,,X,
CSE3PBX,,X,,,X,,,X,,,X,,,X,,,X,,,X,,,X,
CSE3PEX,,,,,X,,,,,,X,,,,,,X,,,,,,X,
CSE3ACX,,,,,,,,X,,,,,,X,,,,,,X,,,,
CSE3SOX,,,,X,,,,,,,X,,X,,,,X,,,,,X,X,
CSE3BDX,,,,,,,,X,,,,,,X,,,,,,X,,,,
CSE3PCX,,,,,,,,,,,,,,X,,,,,,X,,,,
CSE3CAX,,,,,,,,,,,,,,X,,,X,,,X,,,X,
CSE3CBX,,,,,,,,,,,,,,,,,X,,,X,,,X,"""

# Read CSV data
csv_reader = csv.reader(csv_data.splitlines())
result = []

# Loop through each row in the CSV
for row in csv_reader:
    subject = row[0]  # Subject code is in the first column
    for idx, value in enumerate(row[1:]):
        if value == 'X':  # Check if the subject has a class in that month
            result.append({
                "subject": subject,
                "start_date": months[idx]  # Corresponding month from months list
            })

# Convert to JSON format
json_output = json.dumps(result, indent=4)

# Optionally save to a file
with open('subject_instance.json', 'w') as json_file:
    json_file.write(json_output)