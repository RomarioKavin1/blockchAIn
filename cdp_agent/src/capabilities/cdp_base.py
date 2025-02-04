import json
import os
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
from cdp import Wallet, Cdp
from pathlib import Path
import logging
from config.cdp_config import initialize_cdp
from src.storage.nildbapi import NilDBAPI
from src.storage.config import NODE_CONFIG
from src.storage.secret_vault_storage import WalletStorage
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalletManager:
    """Manages wallet creation and storage for agents"""
    _instance = None
    _initialized = False

    def __new__(cls, storage_path: str = "agent_wallets.json"):
        if cls._instance is None:
            cls._instance = super(WalletManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, storage_path: str = "agent_wallets.json", node_id: str = "node_a"):
        if not self._initialized:
            # Initialize CDP SDK first
            initialize_cdp()
            
            # Initialize paths
            self.storage_path = storage_path
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Initialize Nillion components
            self.node_id = node_id
            self.nildb_api = NilDBAPI(NODE_CONFIG)
            self.vault = WalletStorage()
            self.schema_id = self._initialize_schema()
            self.wallets = {}
            self._initialized = True
    
    def _initialize_schema(self) -> str:
        """Initialize or get existing schema for Nillion vault"""
        SCHEMA_FILE = "data/nillion_schema_id.txt"
        
        try:
            # First check if schema ID exists in local storage
            if os.path.exists(SCHEMA_FILE):
                with open(SCHEMA_FILE, 'r') as f:
                    schema_id = f.read().strip()
                    if schema_id:
                        logger.info("Using existing schema ID from local storage")
                        return schema_id

            # If no schema ID in local storage, create new schema
            logger.info("No existing schema ID found, creating new one")
            
            # Default schema definition
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
                self.nildb_api.create_schema(node_name, payload)
            
            # Store the new schema ID
            with open(SCHEMA_FILE, 'w') as f:
                f.write(schema_id)
                
            return schema_id

        except Exception as e:
            logger.error(f"Error initializing schema: {e}")
            raise
    
    def _load_wallets(self) -> Dict[str, Dict[str, Any]]:
        """Load existing wallets from Nillion vault"""
        # This is kept for compatibility but now returns an empty dict
        # as wallets are retrieved individually from vault
        return {}
    
    def _save_wallets(self):
        """Save wallets to storage - no longer needed with Nillion"""
        pass  # No need to save all wallets at once with Nillion
    
    def get_wallet_key(self, agent_name: str, thread_id: str) -> str:
        """Generate unique key for wallet storage"""
        return f"{agent_name}_{thread_id}"
    
    async def get_or_create_wallet(self, agent_name: str, thread_id: str, network_id: str = "base-sepolia") -> Wallet:
        """Get existing wallet or create new one for agent+thread combination"""
        try:
            wallet_key = self.get_wallet_key(agent_name, thread_id)
            
            # Try to retrieve from Nillion vault
            logger.info(f"Attempting to retrieve wallet from Nillion vault for {wallet_key}")
            existing_wallet = self.vault.get_wallet(
                self.node_id,
                agent_name,
                thread_id,
                self.schema_id
            )
            
            if existing_wallet:
                logger.info(f"Found existing wallet in Nillion vault for {wallet_key}")
                # Create CDP wallet from stored data
                try:
                    wallet = Wallet.fetch(existing_wallet["wallet_id"])
                    if not wallet:
                        logger.warning(f"Could not fetch wallet with ID {existing_wallet['wallet_id']}, creating new wallet")
                        return await self._create_new_wallet(agent_name, thread_id, network_id)
                    
                    wallet._seed = existing_wallet["seed_data"]
                    return wallet
                except Exception as e:
                    logger.error(f"Error reconstructing wallet from vault data: {e}")
                    return await self._create_new_wallet(agent_name, thread_id, network_id)
            else:
                logger.info(f"Creating new wallet for {wallet_key}")
                return await self._create_new_wallet(agent_name, thread_id, network_id)
                
        except Exception as e:
            logger.error(f"Error in get_or_create_wallet: {e}")
            logger.info("Falling back to creating new wallet")
            return await self._create_new_wallet(agent_name, thread_id, network_id)

    async def _create_new_wallet(self, agent_name: str, thread_id: str, network_id: str) -> Wallet:
        """Create a new wallet and store in Nillion vault"""
        try:
            # Create new wallet
            wallet = Wallet.create(network_id=network_id)
            wallet_key = self.get_wallet_key(agent_name, thread_id)
            
            # Prepare data for Nillion storage
            wallet_data = {
                "wallet_id": wallet.id,
                "network_id": network_id,
                "created_at": datetime.now().isoformat()
            }
            
            # Get wallet seed
            seed_data = wallet._seed
            
            # Store in Nillion vault
            logger.info(f"Storing new wallet in Nillion vault for {wallet_key}")
            storage_success = self.vault.store_wallet(
                self.node_id,
                agent_name,
                thread_id,
                wallet_data,
                seed_data,
                self.schema_id
            )
            
            if not storage_success:
                logger.error("Failed to store wallet in Nillion vault")
                raise Exception("Failed to store wallet in Nillion vault")
            
            logger.info(f"Successfully stored wallet in Nillion vault for {wallet_key}")
            
            # Request from faucet for new wallets
            await self._fund_new_wallet(wallet)
            
            return wallet
        except Exception as e:
            logger.error(f"Failed to create new wallet: {e}")
            raise
    
    def get_wallet(self, node_name: str, agent_name: str, thread_id: str, schema: str) -> Optional[Dict[str, Any]]:
        """Retrieve wallet and decrypt seed."""
        print("get_wallet :", "nodename:", node_name, agent_name, thread_id, schema)
        try:
            filter_dict = {"agent_name": agent_name, "thread_id": thread_id}
            records = self.nildb_api.data_read(node_name, schema, filter_dict)
            
            if not records or len(records) == 0:
                return None
            
            record = records[0]
            try:
                decrypted_seed = self.decrypt_seed(json.loads(record["encrypted_seed"]))
                
                return {
                    "wallet_id": record["wallet_id"],
                    "network_id": record.get("network_id", ""),  # Use get() with default value
                    "seed_data": decrypted_seed
                }
            except Exception as e:
                print(f"Error decrypting seed: {e}")
                return None
                
        except Exception as e:
            print(f"Error retrieving wallet: {e}")
            return None

    async def _fund_new_wallet(self, wallet: Wallet):
        """Fund new wallet with test tokens"""
        try:
            # Request ETH from faucet
            logger.info("Requesting ETH from faucet...")
            faucet_tx = wallet.faucet()
            faucet_tx.wait()
            logger.info(f"Funded wallet with ETH: {wallet.balance('eth')} ETH")
            
            # Request USDC from faucet
            logger.info("Requesting USDC from faucet...")
            usdc_tx = wallet.faucet(asset_id="usdc")
            usdc_tx.wait()
            logger.info(f"Funded wallet with USDC: {wallet.balance('usdc')} USDC")
        except Exception as e:
            logger.warning(f"Failed to fund wallet from faucet: {e}")

class CDPCapability(ABC):
    """Base class for CDP capabilities that can be added to agents"""
    
    def __init__(self):
        self.wallet_manager = WalletManager("data/agent_wallets.json")
    
    @abstractmethod
    async def execute(self, agent_name: str, thread_id: str, **kwargs):
        """Execute the capability"""
        pass