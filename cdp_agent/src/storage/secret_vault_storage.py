import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from src.storage.config import NODE_CONFIG
from src.storage.nildbapi import NilDBAPI
import nilql

# Initialize NilDB API
nildb_api = NilDBAPI(NODE_CONFIG)

class WalletStorage:
    """Handles wallet storage and encryption using NilDB API and Nillion."""
    
    def __init__(self):
        self.schema_id = self._get_or_create_schema()
        self.secret_key = nilql.ClusterKey.generate({'nodes': [{}] * len(NODE_CONFIG)}, {'store': True})
    
    def _get_or_create_schema(self) -> str:
        """Create schema if it does not exist."""
        schema = json.load(open('schema.json', 'r'))
        schema_id = str(uuid.uuid4())
        
        for node_name in NODE_CONFIG.keys():
            payload = {
                "_id": schema_id,
                "name": "wallet_storage",
                "keys": ["_id"],
                "schema": schema
            }
            nildb_api.create_schema(node_name, payload)
        
        return schema_id

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
