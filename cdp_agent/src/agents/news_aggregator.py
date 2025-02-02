### src/agents/research/news_aggregator.py ###
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.pyth_capabilities import PythPriceCapability
from capabilities.wallet_capabilities import WalletDetailsCapability
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NewsAggregatorMixin(CDPAgentMixin):
    """Mixin for News Aggregator capabilities"""
    def __init__(self):
        super().__init__([
            PythPriceCapability,
            WalletDetailsCapability
        ])

class NewsAggregator(BaseAgent, NewsAggregatorMixin):
    """News Aggregator agent specializing in market impact analysis"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        NewsAggregatorMixin.__init__(self)
        self.significant_wallets = {
            "binance": "0x28C6c06298d514Db089934071355E5743bf21d60",
            "coinbase": "0x71660c4005BA85c37ccec55d0C4493E66Fe775d3",
            "ftx_custody": "0x2FAF487A4414Fe77e2327F0bf4AE2a264a776AD2",
            # Add more significant wallets to track
        }
        self.assets_to_track = {
            'eth': 'ETH', 'ethereum': 'ETH',
            'btc': 'BTC', 'bitcoin': 'BTC',
            'usdc': 'USDC',
            'usdt': 'USDT'
        }

    async def track_wallet_activity(self, thread_id: str, 
                                  wallets: List[str]) -> Dict[str, Any]:
        """Track activity of significant wallets"""
        try:
            wallet_data = {}
            for name, address in self.significant_wallets.items():
                if name in wallets:
                    result = await self.execute_capability(
                        "WalletDetailsCapability",
                        self.config.name,
                        thread_id,
                        address=address
                    )
                    if result["status"] == "success":
                        wallet_data[name] = result

            return {
                "status": "success",
                "wallet_data": wallet_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to track wallets: {e}")
            return {"status": "error", "error": str(e)}

    async def analyze_price_impact(self, thread_id: str, 
                                 asset: str) -> Dict[str, Any]:
        """Analyze price impact of recent events"""
        try:
            price_data = await self.execute_capability(
                "PythPriceCapability",
                self.config.name,
                thread_id,
                asset_id=asset
            )

            if price_data["status"] != "success":
                return {"status": "error", "error": f"No price data for {asset}"}

            return {
                "status": "success",
                "price": price_data["price"],
                "confidence": price_data.get("confidence"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to analyze price impact: {e}")
            return {"status": "error", "error": str(e)}

    def _identify_news_focus(self, message: str) -> Dict[str, Any]:
        """Identify news focus from natural language"""
        message = message.lower()
        
        # Detect relevant assets
        assets = []
        for token, standard in self.assets_to_track.items():
            if token in message:
                assets.append(standard)

        # Default to major assets if none mentioned
        if not assets:
            assets = ['ETH', 'BTC']

        # Detect relevant exchanges/entities
        exchanges = []
        exchange_keywords = {
            'binance': ['binance', 'cz'],
            'coinbase': ['coinbase', 'cb'],
            'ftx': ['ftx', 'sbf']
        }
        for exchange, keywords in exchange_keywords.items():
            if any(keyword in message for keyword in keywords):
                exchanges.append(exchange)

        # Determine analysis focus
        if any(word in message for word in ['whale', 'large', 'transfer', 'moved']):
            focus = "whale_movement"
        elif any(word in message for word in ['impact', 'affect', 'result']):
            focus = "market_impact"
        elif any(word in message for word in ['exchange', 'platform', 'cex']):
            focus = "exchange_activity"
        else:
            focus = "general_analysis"

        return {
            "assets": assets,
            "exchanges": exchanges,
            "focus": focus
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process news analysis requests conversationally"""
        try:
            news_focus = self._identify_news_focus(request.message)
            assets = news_focus["assets"]
            exchanges = news_focus["exchanges"]
            focus = news_focus["focus"]

            # Get price data for relevant assets
            price_impacts = {}
            for asset in assets:
                impact = await self.analyze_price_impact(thread_id, asset)
                if impact["status"] == "success":
                    price_impacts[asset] = impact

            # Track relevant wallet activity
            wallet_activity = None
            if exchanges or focus == "whale_movement":
                wallet_activity = await self.track_wallet_activity(
                    thread_id,
                    exchanges or list(self.significant_wallets.keys())[:3]  # Default to top 3
                )

            # Generate insights based on focus
            if focus == "whale_movement":
                content = "Analyzing significant wallet movements:\n\n"
                if wallet_activity and wallet_activity["status"] == "success":
                    for name, data in wallet_activity["wallet_data"].items():
                        content += (
                            f"{name.title()} Activity:\n"
                            f"• Status: {data.get('status', 'Unknown')}\n"
                            f"• Recent Transactions: {data.get('transaction_count', 'N/A')}\n\n"
                        )
                    content += "Would you like me to monitor any specific transactions?"

            elif focus == "market_impact":
                content = "Analyzing market impact:\n\n"
                for asset, impact in price_impacts.items():
                    content += (
                        f"{asset} Impact Analysis:\n"
                        f"• Current Price: ${float(impact['price']):,.2f}\n"
                        f"• Confidence: ±${float(impact['confidence'])/1e8:,.2f}\n\n"
                    )
                content += "Would you like me to track price movements for any specific news events?"

            elif focus == "exchange_activity":
                content = "Exchange Activity Analysis:\n\n"
                if wallet_activity and wallet_activity["status"] == "success":
                    for name, data in wallet_activity["wallet_data"].items():
                        content += (
                            f"{name.title()}:\n"
                            f"• Activity Level: {data.get('activity_level', 'Normal')}\n"
                            f"• Status: {data.get('status', 'Active')}\n\n"
                        )
                content += "Would you like me to monitor any specific exchange activity?"

            else:
                content = "Current Market Overview:\n\n"
                for asset, impact in price_impacts.items():
                    content += (
                        f"{asset}:\n"
                        f"• Price: ${float(impact['price']):,.2f}\n"
                        f"• Market State: {'Stable' if float(impact['confidence'])/1e8 < 100 else 'Volatile'}\n\n"
                    )
                content += "What specific market news would you like me to analyze?"

            return AgentResponse(
                content=content,
                metadata={
                    "news_focus": news_focus,
                    "price_impacts": price_impacts,
                    "wallet_activity": wallet_activity,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error in news analysis: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue while analyzing market news. "
                    "Could you specify which aspect you're most interested in? "
                    "I can focus on price impacts, exchange activity, or whale movements."
                ),
                metadata={"status": "error", "error": str(e)}
            )