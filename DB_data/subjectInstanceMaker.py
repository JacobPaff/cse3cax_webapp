import json
from datetime import datetime, timedelta

# Function to get the first Monday of the month
def get_first_monday(year, month):
    # First day of the month
    first_day = datetime(year, month, 1)
    # Calculate the difference to the first Monday
    days_until_monday = (7 - first_day.weekday() + 0) % 7
    first_monday = first_day + timedelta(days=days_until_monday)
    return first_monday.strftime('%Y-%m-%d')

# Load the initial JSON file (your data)
with open('/workspaces/cse3cax_webapp/DB_data/subject_instance.json', 'r') as f:
    data = json.load(f)

# Create a list to store the transformed data
transformed_data = []

# Loop over the original data and transform it to Django fixture format
for pk, entry in enumerate(data, start=1):
    # Extract year and month from the start_date field
    year, month = map(int, entry["start_date"].split("-")[:2])

    # Get the first Monday of the corresponding month
    first_monday = get_first_monday(year, month)

    # Create the transformed entry
    transformed_entry = {
        "model": "core.subjectinstance",  # Model reference
        "pk": pk,  # Primary key
        "fields": {
            "subject": entry["subject"],  # Assuming subject is the subject_id
            "start_date": first_monday,  # Updated date to the first Monday
            "enrollments": None  # You can modify or remove this based on your needs
        }
    }
    transformed_data.append(transformed_entry)

# Save the transformed data to a new JSON file
with open('subject_instance_django.json', 'w') as f:
    json.dump(transformed_data, f, indent=4)

print("Conversion complete. Data saved to subject_instance_django.json")
