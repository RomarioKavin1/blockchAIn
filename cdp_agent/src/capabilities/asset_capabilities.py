from typing import Dict, Any, Optional
from .cdp_base import CDPCapability
import logging
from cdp_agentkit_core.actions import CdpAction
logger = logging.getLogger(__name__)

class BalanceCapability(CDPCapability):
    """Get balance for specific assets"""
    async def execute(self, agent_name: str, thread_id: str, 
                     asset_id: Optional[str] = None) -> Dict[str, Any]:
        try:
            wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
            if asset_id:
                balance = wallet.balance(asset_id)
                return {"status": "success", "balance": str(balance), "asset": asset_id}
            else:
                balances = wallet.balances()
                return {"status": "success", "balances": {k: str(v) for k, v in balances.items()}}
        except Exception as e:
            logger.error(f"Balance check failed: {e}")
            return {"status": "error", "error": str(e)}

class TransferCapability(CDPCapability):
    """Transfer assets between addresses"""
    async def execute(self, agent_name: str, thread_id: str, 
                     amount: float, asset_id: str, destination: str,
                     gasless: bool = False) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            transfer = wallet.transfer(amount, asset_id, destination, gasless=gasless)
            result = transfer.wait()
            return {
                "status": "success",
                "transaction_hash": result.transaction_hash,
                "amount": amount,
                "asset_id": asset_id,
                "destination": destination
            }
        except Exception as e:
            logger.error(f"Transfer failed: {e}")
            return {"status": "error", "error": str(e)}

class TradeCapability(CDPCapability):
    """Trade assets (mainnets only)"""
    async def execute(self, agent_name: str, thread_id: str,
                     amount: float, from_asset: str, to_asset: str) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id, "base-mainnet")
        try:
            trade = wallet.trade(amount, from_asset, to_asset)
            result = trade.wait()
            return {
                "status": "success",
                "transaction_hash": result.transaction_hash,
                "amount": amount,
                "from_asset": from_asset,
                "to_asset": to_asset
            }
        except Exception as e:
            logger.error(f"Trade failed: {e}")
            return {"status": "error", "error": str(e)}

class WrapETHCapability(CDPCapability):
    """Wrap ETH to WETH"""
    async def execute(self, agent_name: str, thread_id: str,
                     amount: float) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            # Call wrap_eth method
            transaction = wallet.wrap_eth(amount)
            result = transaction.wait()
            return {
                "status": "success",
                "transaction_hash": result.transaction_hash,
                "amount": amount
            }
        except Exception as e:
            logger.error(f"ETH wrap failed: {e}")
            return {"status": "error", "error": str(e)}