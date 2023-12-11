# config_manager.py

import json
import os

class ConfigManager:
    def __init__(self):
        # Define the static path to the config.json file
        self.config_path = os.path.join("..", "config", "config.json")
        self.config = self.load_config()

    def load_config(self):
        # Load the config from the static path
        try:
            with open(self.config_path, 'r') as config_file:
                data = json.load(config_file)
                if not data:  # Check if the data is empty
                    print("Warning: 'config.json' is empty. Using default settings.")
                return data
        except FileNotFoundError:
            print("Error: 'config.json' file not found.")
            return {}  # Return an empty dictionary if the file doesn't exist
        except json.JSONDecodeError:
            print("Error: Invalid JSON in 'config.json'.")
            return {}  # Return an empty dictionary if the file contains invalid JSON

    def get_config(self, key):
        return self.config.get(key)

    def update_config(self, key, value):
        self.config[key] = value

    def save_config(self):
        # Save the config to the static path
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

