import json

# Load the UserProfile data that contains the lecturer IDs and last names
with open('/workspaces/cse3cax_webapp/DB_data/userprofile_data.json', 'r') as f:
    user_profiles = json.load(f)

# Create a dictionary to map last names to user IDs
last_name_to_user_id = {profile['last_name']: profile['user_id'] for profile in user_profiles}

# Load the initial lecturer expertise JSON file
with open('/workspaces/cse3cax_webapp/DB_data/lecturer_expertise.json', 'r') as f:
    data = json.load(f)

# Create a list to store the transformed data
transformed_data = []

# Loop over the original data and transform it to Django fixture format
for pk, entry in enumerate(data, start=1):
    # Get the user ID by the lecturer's last name
    user_id = last_name_to_user_id.get(entry["lecturer_name"])
    
    # Only add the entry if the user ID was found
    if user_id:
        transformed_entry = {
            "model": "core.lecturerexpertise",  # Model reference
            "pk": pk,  # Primary key
            "fields": {
                "user": user_id,  # The foreign key to UserProfile (int)
                "subject": entry["subject_code"]  # Assuming subject_code refers to subject_id in Subject
            }
        }
        transformed_data.append(transformed_entry)
    else:
        print(f"Lecturer with last name {entry['lecturer_name']} not found in UserProfile data.")

# Save the transformed data to a new JSON file
with open('lecturer_expertise_django.json', 'w') as f:
    json.dump(transformed_data, f, indent=4)

print("Conversion complete. Data saved to lecturer_expertise_django.json")
