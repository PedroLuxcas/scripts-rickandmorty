import json
import os

class JSONHandler:
    def __init__(self, data_folder='data'):
        self.data_folder = os.path.join(os.path.dirname(__file__), '..', data_folder)
    
    def read_json(self, filename):
        """Reads a JSON file and returns the data"""
        file_path = os.path.join(self.data_folder, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"   📂 Loaded {filename}: {len(data) if isinstance(data, list) else 1} records")
                return data
        except FileNotFoundError:
            print(f"❌ File {filename} not found at {file_path}!")
            return None
        except json.JSONDecodeError:
            print(f"❌ Error decoding JSON from {filename}!")
            return None