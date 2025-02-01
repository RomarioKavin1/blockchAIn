from typing import Dict, Any
from .cdp_base import CDPCapability
import logging
logger = logging.getLogger(__name__)
class WalletDetailsCapability(CDPCapability):
    """Get details about the MPC Wallet"""
    async def execute(self, agent_name: str, thread_id: str) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            return {
                "status": "success",
                "wallet_id": wallet.id,
                "address": wallet.default_address.address_id,
                "network": wallet.network_id
            }
        except Exception as e:
            logger.error(f"Wallet details fetch failed: {e}")
            return {"status": "error", "error": str(e)}

class RegisterBasenameCapability(CDPCapability):
    """Register a Basename for the wallet"""
    async def execute(self, agent_name: str, thread_id: str,
                     basename: str) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            transaction = wallet.register_basename(basename)
            result = transaction.wait()
            return {
                "status": "success",
                "transaction_hash": result.transaction_hash,
                "basename": basename
            }
        except Exception as e:
            logger.error(f"Basename registration failed: {e}")
            return {"status": "error", "error": str(e)}