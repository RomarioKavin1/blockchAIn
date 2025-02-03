import json
import uuid

from src.storage.config import NODE_CONFIG
from src.storage.nildbapi import NilDBAPI

# Initialize services
nildb_api = NilDBAPI(NODE_CONFIG)

def define_collection(schema: dict) -> str:
    """Define a collection and register it on the nodes."""
    try:
        # Generate and id for the schema
        schema_id = str(uuid.uuid4())

        # Create schema across nodes
        success = True
        for i, node_name in enumerate(NODE_CONFIG.keys()):
            payload = {
                "_id": schema_id,
                "name": "My Data",
                "keys": [
                    "_id"
                  ],
                "schema": schema,
            }
            if not nildb_api.create_schema(node_name, payload):
                success = False
                break

        print(f"Schema ID: {schema_id}")
        return schema_id if success else None
    except Exception as e:
        print(f"Error creating schema: {str(e)}")
        return None
    
if __name__ == "__main__":
    # register on nodes
    define_collection(json.load(open('schema.json', 'r')))