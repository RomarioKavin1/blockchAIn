from typing import Dict, Any
from .cdp_base import CDPCapability
import logging
logger = logging.getLogger(__name__)
class MorphoDepositCapability(CDPCapability):
    """Deposit into a Morpho Vault"""
    async def execute(self, agent_name: str, thread_id: str,
                     amount: float, asset_id: str) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            transaction = wallet.morpho_deposit(amount, asset_id)
            result = transaction.wait()
            return {
                "status": "success",
                "transaction_hash": result.transaction_hash,
                "amount": amount,
                "asset_id": asset_id
            }
        except Exception as e:
            logger.error(f"Morpho deposit failed: {e}")
            return {"status": "error", "error": str(e)}

class MorphoWithdrawCapability(CDPCapability):
    """Withdraw from a Morpho Vault"""
    async def execute(self, agent_name: str, thread_id: str,
                     amount: float, asset_id: str) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            transaction = wallet.morpho_withdraw(amount, asset_id)
            result = transaction.wait()
            return {
                "status": "success",
                "transaction_hash": result.transaction_hash,
                "amount": amount,
                "asset_id": asset_id
            }
        except Exception as e:
            logger.error(f"Morpho withdrawal failed: {e}")
            return {"status": "error", "error": str(e)}
