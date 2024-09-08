import json

# Read the original JSON data
with open('/workspaces/cse3cax_webapp/role_data.json', 'r') as file:
    data = json.load(file)

# Update the model identifier for each item
for item in data:
    if item['model'] == 'admin_user_input.role':
        item['model'] = 'core.role'

# Write the updated data back to the file
with open('updated_role_data.json', 'w') as file:
    json.dump(data, file, indent=2)

print("JSON file has been updated successfully.")