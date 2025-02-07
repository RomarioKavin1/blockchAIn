### src/agents/research/data_scientist.py ###
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability
from capabilities.pyth_capabilities import PythPriceCapability, PythPriceFeedIDCapability
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DataScientistMixin(CDPAgentMixin):
        """Mixin for Data Scientist capabilities"""
        def __init__(self):
            super().__init__([
                BalanceCapability,
                PythPriceCapability,
                PythPriceFeedIDCapability
            ])

class DataScientist(BaseAgent, DataScientistMixin):
    """Data Scientist agent specializing in on-chain data analysis"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        DataScientistMixin.__init__(self)
        self.assets_of_interest = {
            'eth': 'ETH', 'ethereum': 'ETH',
            'btc': 'BTC', 'bitcoin': 'BTC',
            'usdc': 'USDC',
            'usdt': 'USDT',
            'sol': 'SOL', 'solana': 'SOL'
        }

    async def get_asset_metrics(self, thread_id: str, asset: str) -> Dict[str, Any]:
        """Get comprehensive metrics for an asset"""
        try:
            # Get price feed first
            feed_result = await self.execute_capability(
                "PythPriceFeedIDCapability",
                self.config.name,
                thread_id,
                symbol=asset
            )
            
            if feed_result["status"] != "success":
                return {"status": "error", "error": f"No price feed found for {asset}"}
            
            # Get current price data
            price_data = await self.execute_capability(
                "PythPriceCapability",
                self.config.name,
                thread_id,
                price_feed_id=feed_result["feed_id"]
            )
            
            # Get volume data through balance checks of major addresses
            volume_data = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id,
                asset_id=asset
            )

            return {
                "status": "success",
                "price": price_data.get("price"),
                "confidence": price_data.get("confidence"),
                "volume": volume_data.get("balance"),
                "feed_id": feed_result["feed_id"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get asset metrics: {e}")
            return {"status": "error", "error": str(e)}

    async def analyze_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected metrics for insights"""
        try:
            price = float(metrics["price"])
            confidence = float(metrics.get("confidence", 0)) / 1e8
            volatility = (confidence / price) * 100

            analysis = {
                "price_metrics": {
                    "current_price": price,
                    "volatility": volatility,
                    "confidence_interval": f"±${confidence:,.2f}"
                },
                "market_conditions": "stable" if volatility < 2 else "volatile",
                "timestamp": metrics["timestamp"]
            }

            return analysis
        except Exception as e:
            logger.error(f"Failed to analyze metrics: {e}")
            return {"status": "error", "error": str(e)}

    def _identify_research_focus(self, message: str) -> Dict[str, Any]:
        """Identify research focus from natural language"""
        message = message.lower()
        
        # Detect assets mentioned
        assets = []
        for token, standard in self.assets_of_interest.items():
            if token in message:
                assets.append(standard)

        # If no specific assets mentioned, look at major ones
        if not assets:
            assets = ['ETH', 'BTC']  # Default assets

        # Determine analysis type
        if any(word in message for word in ['volume', 'trading', 'liquidity', 'flows']):
            focus = "volume_analysis"
        elif any(word in message for word in ['volatility', 'stable', 'movement']):
            focus = "volatility_analysis"
        elif any(word in message for word in ['price', 'value', 'worth']):
            focus = "price_analysis"
        elif any(word in message for word in ['correlation', 'relationship', 'compare']):
            focus = "correlation_analysis"
        else:
            focus = "general_analysis"

        return {
            "assets": assets,
            "focus": focus,
            "timeframe": "recent"  # Could be expanded based on message
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process research requests conversationally"""
        try:
            research_focus = self._identify_research_focus(request.message)
            assets = research_focus["assets"]
            focus = research_focus["focus"]

            # Collect metrics for all relevant assets
            asset_data = {}
            for asset in assets:
                metrics = await self.get_asset_metrics(thread_id, asset)
                if metrics["status"] == "success":
                    analysis = await self.analyze_metrics(metrics)
                    asset_data[asset] = {**metrics, "analysis": analysis}

            # Generate insights based on focus
            if focus == "volume_analysis":
                content = "Based on the on-chain data:\n\n"
                for asset, data in asset_data.items():
                    content += (
                        f"{asset} Analysis:\n"
                        f"• Trading Volume: {data['volume']}\n"
                        f"• Current Price: ${float(data['price']):,.2f}\n"
                        f"Would you like me to analyze any specific volume patterns?\n"
                    )

            elif focus == "volatility_analysis":
                content = "Volatility Analysis:\n\n"
                for asset, data in asset_data.items():
                    analysis = data["analysis"]
                    content += (
                        f"{asset}:\n"
                        f"• Current Volatility: {analysis['price_metrics']['volatility']:.2f}%\n"
                        f"• Confidence Interval: {analysis['price_metrics']['confidence_interval']}\n"
                        f"• Market Condition: {analysis['market_conditions'].title()}\n\n"
                    )
                content += "Would you like me to track any specific volatility metrics?"

            elif focus == "correlation_analysis":
                if len(assets) >= 2:
                    content = f"Analyzing relationship between {' and '.join(assets)}:\n\n"
                    # Add correlation analysis here
                    content += "Would you like me to investigate any specific correlation patterns?"
                else:
                    content = "I can analyze correlations between assets. Which pairs would you like me to examine?"

            else:
                content = "Here's my analysis of the current market data:\n\n"
                for asset, data in asset_data.items():
                    analysis = data["analysis"]
                    content += (
                        f"{asset} Metrics:\n"
                        f"• Price: ${float(data['price']):,.2f}\n"
                        f"• Market State: {analysis['market_conditions'].title()}\n"
                        f"• Volatility: {analysis['price_metrics']['volatility']:.2f}%\n\n"
                    )
                content += "What specific aspects would you like me to analyze further?"

            return AgentResponse(
                content=content,
                metadata={
                    "research_focus": research_focus,
                    "asset_data": asset_data,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error in data analysis: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue while analyzing the data. "
                    "Could you specify which metrics you're most interested in? "
                    "I can focus on price movements, volume patterns, or volatility analysis."
                ),
                metadata={"status": "error", "error": str(e)}
            )