from typing import Dict, Any, Optional
from .cdp_base import CDPCapability
import logging

logger = logging.getLogger(__name__)


class NFTBalanceCapability(CDPCapability):
    """Get balance for specific NFTs (ERC-721)"""
    async def execute(self, agent_name: str, thread_id: str,
                     contract_address: str, token_id: Optional[int] = None) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            balance = wallet.balance_nft(contract_address, token_id)
            return {
                "status": "success",
                "balance": balance,
                "contract": contract_address,
                "token_id": token_id
            }
        except Exception as e:
            logger.error(f"NFT balance check failed: {e}")
            return {"status": "error", "error": str(e)}

class DeployNFTCapability(CDPCapability):
    """Deploy new NFT contracts"""
    async def execute(self, agent_name: str, thread_id: str,
                     name: str, symbol: str, base_uri: str) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            contract = wallet.deploy_nft(name, symbol, base_uri)
            result = contract.wait()
            return {
                "status": "success",
                "contract_address": result.contract_address,
                "name": name,
                "symbol": symbol
            }
        except Exception as e:
            logger.error(f"NFT deployment failed: {e}")
            return {"status": "error", "error": str(e)}

class MintNFTCapability(CDPCapability):
    """Mint NFTs from existing contracts"""
    async def execute(self, agent_name: str, thread_id: str,
                     contract_address: str, token_uri: str) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            transaction = wallet.mint_nft(contract_address, token_uri)
            result = transaction.wait()
            return {
                "status": "success",
                "transaction_hash": result.transaction_hash,
                "contract_address": contract_address,
                "token_uri": token_uri
            }
        except Exception as e:
            logger.error(f"NFT minting failed: {e}")
            return {"status": "error", "error": str(e)}

class TransferNFTCapability(CDPCapability):
    """Transfer an NFT (ERC-721)"""
    async def execute(self, agent_name: str, thread_id: str,
                     contract_address: str, token_id: int,
                     to_address: str) -> Dict[str, Any]:
        wallet = await self.wallet_manager.get_or_create_wallet(agent_name, thread_id)
        try:
            transaction = wallet.transfer_nft(contract_address, token_id, to_address)
            result = transaction.wait()
            return {
                "status": "success",
                "transaction_hash": result.transaction_hash,
                "contract_address": contract_address,
                "token_id": token_id,
                "to_address": to_address
            }
        except Exception as e:
            logger.error(f"NFT transfer failed: {e}")
            return {"status": "error", "error": str(e)}