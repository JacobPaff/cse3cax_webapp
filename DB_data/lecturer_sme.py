import csv
import json

# Simulated CSV data from your example
csv_data = """Lecturer Name,CSE1ITX,CSE1PGX,CSE1CFX,CSE1OFX,CSE1ISX,CSE2NFX,CSE2DCX,CSE1SPX,CSE1SIX,CSE1IOX,CSE2ICX,CSE2CNX,CSE2SDX,BUS2PMX,CSE2VVX,MAT2DMX,CSE2MAX,CSE2OSX,CSE2ADX,CSE2CPX,CSE2MLX,CSE2SAX,CSE2ANX,CSE2WDX,CSE3BGX,CSE3CIX,CSE3CSX,CSE3NWX,CSE3OTX,CSE3WSX,CSE3PAX,CSE3PBX,CSE3PEX,CSE3ACX,CSE3SOX,CSE3BDX,CSE3PCX,CSE3CAX,CSE3CBX
Acacia,X,X,X,,X,,X,,X,,X,,X,,X,,,X,,,X,,,,,X,,,,X,,,,,X,,,,
Beech,X,X,,X,,X,,,X,X,,X,,,,,,X,X,,,,,X,,,,X,,,,,,X,,,X,,
Cypress,X,,,X,,X,,,,X,X,,,X,,,X,,,,,,X,,X,,,,X,,X,X,,,,,,X,X
Douglas,,X,,X,X,,X,,,X,,X,X,,X,,,,,X,,X,,,,,,,X,,,,X,,,X,,,
Eucalypt,,,,,,,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Flame,X,X,,X,,X,,,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Guava,X,X,,X,,X,,,,X,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,
Hickory,X,,,X,X,,X,,,X,,,X,,,,,,,,,,,,,,,,,,,,,,,,,,
Ironbark,,X,X,,,,,,,,,,,,,X,,,,X,,,,,,,X,,,,,,X,,,,,,
Jacaranda,,,,,,,,,,,,,,,,,,X,,,,,,,,,,,,,,,,,,,,,
Karri,X,X,,X,,X,,,X,X,,X,,X,,,,,X,,,,,X,,,X,,,,X,X,,,,X,,X,X
Laurel,X,X,,X,,X,,,X,X,X,,,,,,X,,X,,,,,,,,X,,,,,,,,,,X,,
Maple,X,,X,X,X,,X,,,X,X,,X,,,,,X,,,,,,,,,,X,,,,,,,X,,,,
"""

# Define the subject codes
subjects = [
    "CSE1ITX", "CSE1PGX", "CSE1CFX", "CSE1OFX", "CSE1ISX", "CSE2NFX", "CSE2DCX", "CSE1SPX", "CSE1SIX", "CSE1IOX", 
    "CSE2ICX", "CSE2CNX", "CSE2SDX", "BUS2PMX", "CSE2VVX", "MAT2DMX", "CSE2MAX", "CSE2OSX", "CSE2ADX", "CSE2CPX", 
    "CSE2MLX", "CSE2SAX", "CSE2ANX", "CSE2WDX", "CSE3BGX", "CSE3CIX", "CSE3CSX", "CSE3NWX", "CSE3OTX", "CSE3WSX", 
    "CSE3PAX", "CSE3PBX", "CSE3PEX", "CSE3ACX", "CSE3SOX", "CSE3BDX", "CSE3PCX", "CSE3CAX", "CSE3CBX"
]

# Read CSV data
csv_reader = csv.reader(csv_data.splitlines())
next(csv_reader)  # Skip the header row

result = []

# Process each row of the CSV
for row in csv_reader:
    lecturer_name = row[0]  # Get the lecturer's last name (UserProfile.last_name)
    for idx, value in enumerate(row[1:]):
        if value == 'X':  # Check if the lecturer is assigned to the subject
            result.append({
                "lecturer_name": lecturer_name,
                "subject_code": subjects[idx]
            })

# Convert to JSON format
json_output = json.dumps(result, indent=4)

# Optionally, save to a file
with open('lecturer_expertise.json', 'w') as json_file:
    json_file.write(json_output)

# # Print the JSON output
# print(json_output)

