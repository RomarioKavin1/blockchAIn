import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from src.storage.config import NODE_CONFIG
from src.storage.nildbapi import NilDBAPI
import nilql
import os

# Initialize NilDB API
nildb_api = NilDBAPI(NODE_CONFIG)

class WalletStorage:
    """Handles wallet storage and encryption using NilDB API and Nillion."""
    
    def __init__(self):
        self.schema_id = self._get_or_create_schema()
        self.secret_key = nilql.ClusterKey.generate({'nodes': [{}] * len(NODE_CONFIG)}, {'store': True})
    
    def _get_or_create_schema(self) -> str:
        """Create schema if it does not exist."""
        SCHEMA_FILE_PATH = "data/nillion_schema_id.txt"
        
        try:
            # Check if schema ID exists in local file
            os.makedirs("data", exist_ok=True)
            if os.path.exists(SCHEMA_FILE_PATH):
                with open(SCHEMA_FILE_PATH, 'r') as f:
                    schema_id = f.read().strip()
                    if schema_id:
                        print(f"Using existing schema ID: {schema_id}")
                        return schema_id

            # Create new schema
            DEFAULT_SCHEMA = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "_id": {
                            "type": "string",
                            "format": "uuid",
                            "coerce": True
                        },
                        "agent_name": {
                            "type": "string"
                        },
                        "thread_id": {
                            "type": "string"
                        },
                        "wallet_id": {
                            "type": "string"
                        },
                        "network_id": {
                            "type": "string"
                        },
                        "encrypted_seed": {
                            "type": "string"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "coerce": True
                        }
                    },
                    "required": [
                        "_id",
                        "agent_name",
                        "thread_id",
                        "wallet_id",
                        "encrypted_seed"
                    ],
                    "additionalProperties": False
                }
            }

            schema_id = str(uuid.uuid4())
            
            for node_name in NODE_CONFIG.keys():
                payload = {
                    "_id": schema_id,
                    "name": "wallet_storage",
                    "keys": ["_id"],
                    "schema": DEFAULT_SCHEMA
                }
                nildb_api.create_schema(node_name, payload)
            
            # Save schema ID to local file
            with open(SCHEMA_FILE_PATH, 'w') as f:
                f.write(schema_id)
            
            print(f"Created new schema with ID: {schema_id}")
            return schema_id

        except Exception as e:
            print(f"Error in _get_or_create_schema: {e}")
            raise

    def encrypt_seed(self, seed_data: str) -> List[str]:
        """Encrypt seed using secret sharing."""
        return list(nilql.encrypt(self.secret_key, seed_data))
    
    def decrypt_seed(self, encrypted_shares: List[str]) -> str:
        """Decrypt stored seed data."""
        return str(nilql.decrypt(self.secret_key, encrypted_shares))
    
    def store_wallet(self, node_name: str, agent_name: str, thread_id: str, wallet_data: Dict[str, Any], seed_data: str,schema:str) -> bool:
        """Store encrypted wallet seed in NilDB."""
        print("store_wallet :","nodename:",node_name, agent_name, thread_id, wallet_data, seed_data,schema)
        try:
            encrypted_seed = self.encrypt_seed(seed_data)
            record = {
                "_id": str(uuid.uuid4()),
                "agent_name": agent_name,
                "thread_id": thread_id,
                "wallet_id": wallet_data["wallet_id"],
                "network_id": wallet_data["network_id"],
                "encrypted_seed": json.dumps(encrypted_seed),
                # "created_at": datetime.now().isoformat()
            }
            return nildb_api.data_upload(node_name, schema, [record])
        except Exception as e:
            print(f"Error storing wallet: {e}")
            return False

    def get_wallet(self, node_name: str, agent_name: str, thread_id: str,schema:str) -> Optional[Dict[str, Any]]:
        """Retrieve wallet and decrypt seed."""
        print("get_wallet :","nodename:",node_name, agent_name, thread_id,schema)
        try:
            filter_dict = {"agent_name": agent_name, "thread_id": thread_id}
            records = nildb_api.data_read(node_name, schema, filter_dict)
            
            if not records:
                return None
            
            record = records[0]
            decrypted_seed = self.decrypt_seed(json.loads(record["encrypted_seed"]))
            
            return {
                "wallet_id": record["wallet_id"],
                "network_id": record["network_id"],
                "seed_data": decrypted_seed
            }
        except Exception as e:
            print(f"Error retrieving wallet: {e}")
            return None
