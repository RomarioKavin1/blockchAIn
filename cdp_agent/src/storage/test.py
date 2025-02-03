
import json

from src.storage.define_collection import define_collection

def main():
    """Main function to define a collection"""
    try:
        with open('schema.json', 'r') as schema_file:
            schema = json.load(schema_file)
        
        if define_collection(schema):
            print("Collection defined successfully.")
        else:
            print("Failed to define collection.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
