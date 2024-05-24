import json

# Step 1: Read the JSON file
with open('desktop-cat\config.json', 'r') as file:
    data = json.load(file)

print("Original Data:", data)

# Step 2: Update the JSON data
data['new_key'] = 'aa'
# If it's a list, you can append a new item, for example:
# data.append({"new_key": "new_value"})

print("Updated Data:", data)

# Step 3: Write the updated JSON data back to the file
# with open('desktop-cat\config.json', 'w') as file:
#     json.dump(data, file, indent=4)