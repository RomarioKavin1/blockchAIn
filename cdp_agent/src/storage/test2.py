import json
import uuid
from datetime import datetime

from src.storage.config import NODE_CONFIG
from src.storage.nildbapi import NilDBAPI
from src.storage.define_collection import define_collection
from src.storage.secret_vault_storage import WalletStorage  # Assuming your class is here

# Initialize NilDB API and Vault
nildb_api = NilDBAPI(NODE_CONFIG)
vault = WalletStorage()
schemaid=""
def test_schema_creation()->str:
    """Test schema creation using the provided schema.json."""
    with open("schema.json", "r") as f:
        schema = json.load(f)
    
    success = define_collection(schema)
    
    if success:
        print("[✓] Schema created successfully.")
        return success
    else:
        print("[X] Schema creation failed.")
        return "failed"

def test_store_wallet(schemaid:str):
    """Test storing a wallet with an encrypted seed."""
    wallet_data = {
        "wallet_id": str(uuid.uuid4()),
        "network_id": "Ethereum",
        "created_at": datetime.now().isoformat()
    }
    
    seed_data = "my_super_secret_seed_phrase"
    
    success = vault.store_wallet("node_a","test_agent", "test_thread", wallet_data, seed_data,schemaid)
    
    if success:
        print("[✓] Wallet stored successfully.")
    else:
        print("[X] Wallet storage failed.")

def test_retrieve_wallet(schemaid:str):
    """Test retrieving a wallet and decrypting the seed."""
    wallet = vault.get_wallet("node_a","test_agent", "test_thread",schemaid)
    
    if wallet:
        print(f"[✓] Wallet retrieved successfully: {wallet}")
    else:
        print("[X] Wallet retrieval failed.")

if __name__ == "__main__":
    print("Running NilDB Wallet Tests...\n")
    
    schemaid=test_schema_creation()
    print("mainn",schemaid)
    if schemaid=="failed":
        print("Schema creation failed. Exiting tests.")
    else:
        test_store_wallet(schemaid)
        test_retrieve_wallet(schemaid)
