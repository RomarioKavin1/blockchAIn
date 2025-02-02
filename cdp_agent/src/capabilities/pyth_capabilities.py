### src/capabilities/pyth_capabilities.py ###
import requests
from typing import Dict, Any
from .cdp_base import CDPCapability
import logging

logger = logging.getLogger(__name__)

class PythPriceFeedIDCapability(CDPCapability):
    """Get Pyth Network price feed ID for a token"""
    
    async def execute(self, agent_name: str, thread_id: str, 
                     symbol: str) -> Dict[str, Any]:
        """Get price feed ID for given token symbol"""
        try:
            url = f"https://hermes.pyth.network/v2/price_feeds?query={symbol}&asset_type=crypto"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return {
                    "status": "error",
                    "error": f"No price feed found for {symbol}"
                }
                
            filtered_data = [
                item for item in data 
                if item["attributes"]["base"].lower() == symbol.lower()
            ]
            
            if not filtered_data:
                return {
                    "status": "error",
                    "error": f"No price feed found for {symbol}"
                }
                
            return {
                "status": "success",
                "feed_id": filtered_data[0]["id"],
                "symbol": symbol
            }
                
        except Exception as e:
            logger.error(f"Pyth feed ID fetch failed: {e}")
            return {"status": "error", "error": str(e)}

class PythPriceCapability(CDPCapability):
    """Get price data from Pyth Network"""
    
    def _format_price(self, price: int, exponent: int) -> str:
        """Format price with proper decimal places"""
        if exponent < 0:
            adjusted_price = price * 100
            divisor = 10**-exponent
            scaled_price = adjusted_price // divisor
            price_str = f"{scaled_price // 100}.{scaled_price % 100:02}"
            return price_str if not price_str.startswith(".") else f"0{price_str}"
        scaled_price = price // (10**exponent)
        return str(scaled_price)
    
    async def execute(self, agent_name: str, thread_id: str,
                     price_feed_id: str) -> Dict[str, Any]:
        """Get price data for given feed ID"""
        try:
            url = f"https://hermes.pyth.network/v2/updates/price/latest?ids[]={price_feed_id}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            parsed_data = data["parsed"]
            if not parsed_data:
                return {
                    "status": "error",
                    "error": f"No price data found for {price_feed_id}"
                }
                
            price_info = parsed_data[0]["price"]
            price = int(price_info["price"])
            exponent = price_info["expo"]
            
            formatted_price = self._format_price(price, exponent)
            
            return {
                "status": "success",
                "price": formatted_price,
                "confidence": price_info.get("conf"),
                "publish_time": price_info.get("publish_time"),
                "feed_id": price_feed_id
            }
                
        except Exception as e:
            logger.error(f"Pyth price fetch failed: {e}")
            return {"status": "error", "error": str(e)}