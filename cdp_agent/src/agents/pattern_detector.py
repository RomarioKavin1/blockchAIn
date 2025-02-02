### src/agents/research/pattern_detector.py ###
from typing import Dict, Any, List, Optional
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.pyth_capabilities import PythPriceCapability
from capabilities.trade_capabilities import TradeCapability
from capabilities.asset_capabilities import BalanceCapability
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PatternDetectorMixin(CDPAgentMixin):
    """Mixin for Pattern Detector capabilities"""
    def __init__(self):
        super().__init__([
            PythPriceCapability,
            TradeCapability,
            BalanceCapability
        ])

class PatternDetector(BaseAgent, PatternDetectorMixin):
    """Pattern Detector agent specializing in market pattern analysis"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        PatternDetectorMixin.__init__(self)
        self.tracked_assets = {
            'eth': 'ETH', 'ethereum': 'ETH',
            'btc': 'BTC', 'bitcoin': 'BTC',
            'usdc': 'USDC',
            'usdt': 'USDT'
        }
        self.pattern_thresholds = {
            'volume_spike': 0.5,  # 50% increase
            'price_movement': 0.03,  # 3% movement
            'volatility_high': 0.05  # 5% volatility
        }

    async def analyze_price_pattern(self, thread_id: str, 
                                  asset: str) -> Dict[str, Any]:
        """Analyze price patterns for an asset"""
        try:
            price_data = await self.execute_capability(
                "PythPriceCapability",
                self.config.name,
                thread_id,
                asset_id=asset
            )

            if price_data["status"] != "success":
                return {"status": "error", "error": f"No price data for {asset}"}

            # Calculate basic metrics
            price = float(price_data["price"])
            confidence = float(price_data.get("confidence", 0)) / 1e8
            volatility = (confidence / price) * 100

            # Identify patterns
            patterns = []
            if volatility > self.pattern_thresholds['volatility_high']:
                patterns.append("High Volatility")
            
            return {
                "status": "success",
                "price": price,
                "volatility": volatility,
                "patterns": patterns,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to analyze price pattern: {e}")
            return {"status": "error", "error": str(e)}

    async def analyze_volume_pattern(self, thread_id: str, 
                                   asset: str) -> Dict[str, Any]:
        """Analyze trading volume patterns"""
        try:
            # Get current trading activity
            balance_data = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id,
                asset_id=asset
            )

            if balance_data["status"] != "success":
                return {"status": "error", "error": f"No volume data for {asset}"}

            # Analyze volume patterns
            volume = float(balance_data.get("balance", 0))
            patterns = []
            
            if volume > 1000:  # Example threshold
                patterns.append("High Volume")

            return {
                "status": "success",
                "volume": volume,
                "patterns": patterns,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to analyze volume pattern: {e}")
            return {"status": "error", "error": str(e)}

    async def verify_pattern(self, thread_id: str, asset: str, 
                           pattern_type: str) -> Dict[str, Any]:
        """Verify detected patterns through trade analysis"""
        try:
            trade_data = await self.execute_capability(
                "TradeCapability",
                self.config.name,
                thread_id,
                asset_id=asset
            )

            return {
                "status": "success",
                "pattern_type": pattern_type,
                "confirmation": trade_data.get("status") == "success",
                "confidence": "high" if trade_data.get("status") == "success" else "low",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to verify pattern: {e}")
            return {"status": "error", "error": str(e)}

    def _identify_pattern_focus(self, message: str) -> Dict[str, Any]:
        """Identify pattern analysis focus from natural language"""
        message = message.lower()
        
        # Detect assets
        assets = []
        for token, standard in self.tracked_assets.items():
            if token in message:
                assets.append(standard)

        # Default to major assets if none mentioned
        if not assets:
            assets = ['ETH', 'BTC']

        # Determine pattern type focus
        if any(word in message for word in ['volume', 'trading', 'activity']):
            focus = "volume_patterns"
        elif any(word in message for word in ['volatility', 'movement', 'swing']):
            focus = "volatility_patterns"
        elif any(word in message for word in ['trend', 'direction', 'moving']):
            focus = "trend_patterns"
        else:
            focus = "all_patterns"

        return {
            "assets": assets,
            "focus": focus,
            "timeframe": "current"  # Could be expanded based on message
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process pattern detection requests conversationally"""
        try:
            pattern_focus = self._identify_pattern_focus(request.message)
            assets = pattern_focus["assets"]
            focus = pattern_focus["focus"]

            all_patterns = {}
            for asset in assets:
                asset_patterns = {
                    "price": await self.analyze_price_pattern(thread_id, asset),
                    "volume": await self.analyze_volume_pattern(thread_id, asset)
                }
                
                # Verify significant patterns
                if asset_patterns["price"]["status"] == "success" and asset_patterns["price"]["patterns"]:
                    verification = await self.verify_pattern(thread_id, asset, "price")
                    asset_patterns["verification"] = verification

                all_patterns[asset] = asset_patterns

            # Generate insights based on focus
            if focus == "volume_patterns":
                content = "Volume Pattern Analysis:\n\n"
                for asset, patterns in all_patterns.items():
                    volume_data = patterns["volume"]
                    if volume_data["status"] == "success":
                        content += (
                            f"{asset} Volume Patterns:\n"
                            f"• Trading Volume: {volume_data['volume']}\n"
                            f"• Detected Patterns: {', '.join(volume_data['patterns']) or 'No significant patterns'}\n\n"
                        )
                content += "Would you like me to monitor any specific volume thresholds?"

            elif focus == "volatility_patterns":
                content = "Volatility Pattern Analysis:\n\n"
                for asset, patterns in all_patterns.items():
                    price_data = patterns["price"]
                    if price_data["status"] == "success":
                        content += (
                            f"{asset} Volatility Patterns:\n"
                            f"• Current Volatility: {price_data['volatility']:.2f}%\n"
                            f"• Price: ${price_data['price']:,.2f}\n"
                            f"• Patterns: {', '.join(price_data['patterns']) or 'No significant patterns'}\n\n"
                        )
                content += "Would you like me to track any specific volatility levels?"

            elif focus == "trend_patterns":
                content = "Trend Analysis:\n\n"
                for asset, patterns in all_patterns.items():
                    price_data = patterns["price"]
                    if price_data["status"] == "success":
                        content += (
                            f"{asset} Trend Patterns:\n"
                            f"• Current Price: ${price_data['price']:,.2f}\n"
                            f"• Market State: {'Volatile' if price_data['volatility'] > 5 else 'Stable'}\n"
                            f"• Identified Patterns: {', '.join(price_data['patterns']) or 'No significant patterns'}\n\n"
                        )
                content += "Would you like me to analyze any specific trend patterns?"

            else:
                content = "Comprehensive Pattern Analysis:\n\n"
                for asset, patterns in all_patterns.items():
                    price_data = patterns["price"]
                    volume_data = patterns["volume"]
                    if price_data["status"] == "success" and volume_data["status"] == "success":
                        content += (
                            f"{asset} Analysis:\n"
                            f"• Price: ${price_data['price']:,.2f}\n"
                            f"• Volatility: {price_data['volatility']:.2f}%\n"
                            f"• Volume: {volume_data['volume']}\n"
                            f"• Detected Patterns: {', '.join(price_data['patterns'] + volume_data['patterns']) or 'No significant patterns'}\n\n"
                        )
                content += "Which patterns would you like me to analyze in detail?"

            return AgentResponse(
                content=content,
                metadata={
                    "pattern_focus": pattern_focus,
                    "patterns": all_patterns,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error in pattern detection: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue while analyzing market patterns. "
                    "Could you specify which type of patterns you're interested in? "
                    "I can look at volume patterns, volatility, or price trends."
                ),
                metadata={"status": "error", "error": str(e)}
            )