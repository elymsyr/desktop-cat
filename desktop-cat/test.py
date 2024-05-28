import json

def modify_json_value(file_path, keys, new_value):
    """
    Modify a specific value in a JSON file.

    Args:
    - file_path (str): Path to the JSON file.
    - keys (list): List of keys representing the path to the value to modify.
    - new_value: New value to set at the specified path.

    Returns:
    - bool: True if the modification was successful, False otherwise.
    """
    try:
        # Open the JSON file for reading
        with open(file_path, 'r') as file:
            data = json.load(file)  # Load JSON data from the file

        # Navigate to the specified path and set the new value
        temp = data
        for key in keys[:-1]:
            temp = temp[key]
        temp[keys[-1]] = new_value

        # Write the modified data back to the JSON file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        return True  # Modification applied successfully
    except Exception as e:
        print(f"An error occurred: {e}")
        return False  # Failed to apply modification

# Example usage:
file_path = "data.json"
keys = ["config", "fonts", "current_font_size"]
new_value = 20

if modify_json_value(file_path, keys, new_value):
    print("Modification applied successfully.")
else:
    print("Failed to apply modification.")
