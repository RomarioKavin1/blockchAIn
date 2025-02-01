import json
import os
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod
from cdp import Wallet, Cdp
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalletManager:
    """Manages wallet creation and storage for agents"""
    
    def __init__(self, storage_path: str = "agent_wallets.json"):
        self.storage_path = storage_path
        self.wallets: Dict[str, Dict[str, Any]] = self._load_wallets()
        
    def _load_wallets(self) -> Dict[str, Dict[str, Any]]:
        """Load existing wallets from storage"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not decode {self.storage_path}, starting fresh")
                return {}
        return {}
    
    def _save_wallets(self):
        """Save wallets to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.wallets, f, indent=2)
    
    def get_wallet_key(self, agent_name: str, thread_id: str) -> str:
        """Generate unique key for wallet storage"""
        return f"{agent_name}_{thread_id}"
    
    async def get_or_create_wallet(self, agent_name: str, thread_id: str, network_id: str = "base-sepolia") -> Wallet:
        """Get existing wallet or create new one for agent+thread combination"""
        wallet_key = self.get_wallet_key(agent_name, thread_id)
        
        if wallet_key in self.wallets:
            # Load existing wallet
            wallet_data = self.wallets[wallet_key]
            wallet = Wallet.fetch(wallet_data['wallet_id'])
            try:
                wallet.load_seed(f"seeds/{wallet_key}.json")
            except Exception as e:
                logger.error(f"Failed to load wallet seed: {e}")
                raise
            return wallet
        else:
            # Create new wallet
            try:
                wallet = Wallet.create(network_id=network_id)
                
                # Ensure seeds directory exists
                Path("seeds").mkdir(exist_ok=True)
                
                # Save wallet seed
                wallet.save_seed(f"seeds/{wallet_key}.json", encrypt=True)
                
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
                logger.error(f"Failed to create wallet: {e}")
                raise

    async def _fund_new_wallet(self, wallet: Wallet):
        """Fund new wallet with test tokens"""
        try:
            # Request ETH from faucet
            faucet_tx = wallet.faucet()
            faucet_tx.wait()
            logger.info(f"Funded wallet with ETH: {wallet.balance('eth')} ETH")
            
            # Request USDC from faucet
            usdc_tx = wallet.faucet(asset_id="usdc")
            usdc_tx.wait()
            logger.info(f"Funded wallet with USDC: {wallet.balance('usdc')} USDC")
        except Exception as e:
            logger.warning(f"Failed to fund wallet from faucet: {e}")

class CDPCapability(ABC):
    """Base class for CDP capabilities that can be added to agents"""
    
    def __init__(self):
        self.wallet_manager = WalletManager()
    
    @abstractmethod
    async def execute(self, agent_name: str, thread_id: str, **kwargs):
        """Execute the capability"""
        pass

# class TransferCapability(CDPCapability):
#     """Capability to transfer assets"""
    
#     async def execute(self, agent_name: str, thread_id: str, 
#                      amount: float, asset_id: str, destination: str, 
#                      gasless: bool = False) -> Dict[str, Any]:
#         wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
#         try:
#             transfer = wallet.transfer(amount, asset_id, destination, gasless=gasless)
#             result = transfer.wait()
#             return {
#                 "status": "success",
#                 "transaction_hash": result.transaction_hash,
#                 "amount": amount,
#                 "asset_id": asset_id,
#                 "destination": destination
#             }
#         except Exception as e:
#             logger.error(f"Transfer failed: {e}")
#             return {
#                 "status": "error",
#                 "error": str(e)
#             }

# class TradeCapability(CDPCapability):
#     """Capability to trade assets"""
    
#     async def execute(self, agent_name: str, thread_id: str,
#                      amount: float, from_asset: str, to_asset: str) -> Dict[str, Any]:
#         wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
#         try:
#             trade = wallet.trade(amount, from_asset, to_asset)
#             result = trade.wait()
#             return {
#                 "status": "success",
#                 "transaction_hash": result.transaction_hash,
#                 "amount": amount,
#                 "from_asset": from_asset,
#                 "to_asset": to_asset
#             }
#         except Exception as e:
#             logger.error(f"Trade failed: {e}")
#             return {
#                 "status": "error",
#                 "error": str(e)
#             }

# class BalanceCapability(CDPCapability):
#     """Capability to check balances"""
    
#     async def execute(self, agent_name: str, thread_id: str,
#                      asset_id: Optional[str] = None) -> Dict[str, Any]:
#         wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
#         try:
#             if asset_id:
#                 balance = wallet.balance(asset_id)
#                 return {
#                     "status": "success",
#                     "balances": {asset_id: str(balance)}
#                 }
#             else:
#                 balances = wallet.balances()
#                 return {
#                     "status": "success",
#                     "balances": {k: str(v) for k, v in balances.items()}
#                 }
#         except Exception as e:
#             logger.error(f"Balance check failed: {e}")
#             return {
#                 "status": "error",
#                 "error": str(e)
#             }

### capabilities/agent_mixins.py ###
# from typing import Dict, Any, List
# from .cdp_base import TransferCapability, TradeCapability, BalanceCapability

# class CDPAgentMixin:
#     """Mixin to add CDP capabilities to agents"""
    
#     def __init__(self, capabilities: List[CDPCapability] = None):
#         self.capabilities: Dict[str, CDPCapability] = {}
#         if capabilities:
#             for cap in capabilities:
#                 self.add_capability(cap)

#     def add_capability(self, capability: CDPCapability):
#         """Add a CDP capability to the agent"""
#         self.capabilities[capability.__class__.__name__] = capability

#     async def execute_capability(self, capability_name: str, agent_name: str, 
#                                thread_id: str, **kwargs) -> Dict[str, Any]:
#         """Execute a specific CDP capability"""
#         if capability_name not in self.capabilities:
#             return {
#                 "status": "error",
#                 "error": f"Capability {capability_name} not found"
#             }
#         return await self.capabilities[capability_name].execute(
#             agent_name, thread_id, **kwargs
#         )

# class FullCDPAgentMixin(CDPAgentMixin):
#     """Mixin that includes all CDP capabilities"""
    
#     def __init__(self):
#         super().__init__([
#             TransferCapability(),
#             TradeCapability(),
#             BalanceCapability()
#         ])
