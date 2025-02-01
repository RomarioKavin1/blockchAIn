from typing import Dict, Any
from .cdp_base import CDPCapability
import logging
logger = logging.getLogger(__name__)
class PythPriceCapability(CDPCapability):
    """Fetch price from Pyth Network"""
    async def execute(self, agent_name: str, thread_id: str,
                     price_feed_id: str) -> Dict[str, Any]:
        try:
            price = await self.pyth_fetch_price(price_feed_id)
            return {
                "status": "success",
                "price": price,
                "price_feed_id": price_feed_id
            }
        except Exception as e:
            logger.error(f"Pyth price fetch failed: {e}")
            return {"status": "error", "error": str(e)}

class PythPriceFeedIDCapability(CDPCapability):
    """Fetch price feed ID from Pyth Network"""
    async def execute(self, agent_name: str, thread_id: str,
                     symbol: str) -> Dict[str, Any]:
        try:
            feed_id = await self.pyth_fetch_price_feed_id(symbol)
            return {
                "status": "success",
                "feed_id": feed_id,
                "symbol": symbol
            }
        except Exception as e:
            logger.error(f"Pyth feed ID fetch failed: {e}")
            return {"status": "error", "error": str(e)}