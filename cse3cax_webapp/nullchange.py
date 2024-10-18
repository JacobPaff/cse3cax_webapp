import json

# Load the JSON data (assuming you have it in a file called 'data.json')
with open('U:\Assignments\T4\CSE3CBX - INDUSTRY PROJECT FOR CLOUD TECHNOLOGY\Git\cse3cax_webapp\cse3cax_webapp\subject_instance.json', 'r') as file:
    data = json.load(file)

# Replace null enrollments with 0
for item in data:
    if item['fields']['enrollments'] is None:
        item['fields']['enrollments'] = 0

# Save the updated data back to the file
with open('U:\Assignments\T4\CSE3CBX - INDUSTRY PROJECT FOR CLOUD TECHNOLOGY\Git\cse3cax_webapp\cse3cax_webapp\subject_instance.json', 'w') as file:
    json.dump(data, file, indent=4)