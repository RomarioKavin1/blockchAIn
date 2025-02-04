import json
import os
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
from cdp import Wallet, Cdp
from pathlib import Path
import logging
from config.cdp_config import initialize_cdp

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

    def __init__(self, storage_path: str = "agent_wallets.json"):
        if not self._initialized:
            # Initialize CDP SDK first
            initialize_cdp()
            
            # Set up wallet manager
            self.storage_path = storage_path
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            self.wallets = self._load_wallets()
            self._initialized = True
    
    def _load_wallets(self) -> Dict[str, Dict[str, Any]]:
        """Load existing wallets from storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Could not decode {self.storage_path}, starting fresh")
        except Exception as e:
            logger.error(f"Error loading wallets: {e}")
        return {}
    
    def _save_wallets(self):
        """Save wallets to storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.wallets, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving wallets: {e}")
    
    def get_wallet_key(self, agent_name: str, thread_id: str) -> str:
        """Generate unique key for wallet storage"""
        return f"{agent_name}_{thread_id}"
    
    async def get_or_create_wallet(self, agent_name: str, thread_id: str, network_id: str = "base-sepolia") -> Wallet:
        """Get existing wallet or create new one for agent+thread combination"""
        try:
            wallet_key = self.get_wallet_key(agent_name, thread_id)
            
            if wallet_key in self.wallets:
                # Load existing wallet
                wallet_data = self.wallets[wallet_key]
                logger.info(f"Loading existing wallet for {wallet_key}")
                wallet = Wallet.fetch(wallet_data['wallet_id'])
                
                # Ensure seeds directory exists
                Path("seeds").mkdir(exist_ok=True)
                seed_path = f"seeds/{wallet_key}.json"
                
                try:
                    if os.path.exists(seed_path):
                        wallet.load_seed(seed_path)
                        logger.info(f"Loaded seed for wallet {wallet_key}")
                        return wallet
                    else:
                        logger.warning(f"Seed file not found for wallet {wallet_key}, creating new wallet")
                        return await self._create_new_wallet(agent_name, thread_id, network_id)
                except Exception as e:
                    logger.error(f"Failed to load wallet seed: {e}")
                    return await self._create_new_wallet(agent_name, thread_id, network_id)
            else:
                logger.info(f"Creating new wallet for {wallet_key}")
                return await self._create_new_wallet(agent_name, thread_id, network_id)
                
        except Exception as e:
            logger.error(f"Error in get_or_create_wallet: {e}")
            raise

    async def _create_new_wallet(self, agent_name: str, thread_id: str, network_id: str) -> Wallet:
        """Create a new wallet and initialize it"""
        try:
            # Create new wallet
            wallet = Wallet.create(network_id=network_id)
            wallet_key = self.get_wallet_key(agent_name, thread_id)
            
            # Ensure directories exist
            Path("seeds").mkdir(exist_ok=True)
            os.makedirs("data", exist_ok=True)
            
            # Save wallet seed
            seed_path = f"seeds/{wallet_key}.json"
            wallet.save_seed(seed_path, encrypt=True)
            
            # Store wallet info
            self.wallets[wallet_key] = {
                "agent_name": agent_name,
                "thread_id": thread_id,
                "wallet_id": wallet.id,
                "network_id": network_id
            }
            self._save_wallets()
            
            # Request from faucet for new wallets
            await self._fund_new_wallet(wallet)
            
            return wallet
        except Exception as e:
            logger.error(f"Failed to create new wallet: {e}")
            raise

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