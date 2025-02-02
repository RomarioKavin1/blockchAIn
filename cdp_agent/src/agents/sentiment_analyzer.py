from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.wow_capabilities import WowBuyTokenCapability, WowSellTokenCapability
from capabilities.pyth_capabilities import PythPriceCapability
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SentimentAnalyzerMixin(CDPAgentMixin):
    """Mixin for Sentiment Analyzer capabilities"""
    def __init__(self):
        super().__init__([
            WowBuyTokenCapability,
            WowSellTokenCapability,
            PythPriceCapability
        ])

class SentimentAnalyzer(BaseAgent, SentimentAnalyzerMixin):
    """Sentiment Analyzer agent specializing in social sentiment analysis"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        SentimentAnalyzerMixin.__init__(self)
        self.monitored_assets = {
            'eth': 'ETH', 'ethereum': 'ETH',
            'btc': 'BTC', 'bitcoin': 'BTC',
            'doge': 'DOGE', 'dogecoin': 'DOGE',
            'pepe': 'PEPE',
            'wow': 'WOW'
        }
        self.sentiment_thresholds = {
            'very_bullish': 0.8,
            'bullish': 0.6,
            'neutral': 0.4,
            'bearish': 0.2
        }

    async def analyze_token_sentiment(self, thread_id: str, 
                                    asset: str) -> Dict[str, Any]:
        """Analyze sentiment through Wow token activity"""
        try:
            # Check buy side sentiment
            buy_activity = await self.execute_capability(
                "WowBuyTokenCapability",
                self.config.name,
                thread_id,
                token_address=self.get_token_address(asset)  # You'd need to implement this
            )
            
            # Check sell side sentiment
            sell_activity = await self.execute_capability(
                "WowSellTokenCapability",
                self.config.name,
                thread_id,
                token_address=self.get_token_address(asset)
            )
            
            # Calculate buy/sell ratio for sentiment
            if buy_activity["status"] == "success" and sell_activity["status"] == "success":
                buy_volume = float(buy_activity.get("volume", 0))
                sell_volume = float(sell_activity.get("volume", 0))
                
                total_volume = buy_volume + sell_volume
                if total_volume > 0:
                    sentiment_score = buy_volume / total_volume
                else:
                    sentiment_score = 0.5  # Neutral if no activity

                # Determine sentiment level
                sentiment = "neutral"
                for level, threshold in self.sentiment_thresholds.items():
                    if sentiment_score >= threshold:
                        sentiment = level
                        break

                return {
                    "status": "success",
                    "sentiment_score": sentiment_score,
                    "sentiment": sentiment,
                    "buy_volume": buy_volume,
                    "sell_volume": sell_volume,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {"status": "error", "error": "Failed to get token activity data"}
            
        except Exception as e:
            logger.error(f"Failed to analyze token sentiment: {e}")
            return {"status": "error", "error": str(e)}

    async def analyze_price_correlation(self, thread_id: str, 
                                      asset: str, 
                                      sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlation between sentiment and price"""
        try:
            price_data = await self.execute_capability(
                "PythPriceCapability",
                self.config.name,
                thread_id,
                asset_id=asset
            )
            
            if price_data["status"] == "success" and sentiment_data["status"] == "success":
                return {
                    "status": "success",
                    "price": price_data["price"],
                    "sentiment_score": sentiment_data["sentiment_score"],
                    "correlation": "aligned" if (
                        float(price_data["price"]) > 0 and 
                        sentiment_data["sentiment_score"] > 0.5
                    ) else "divergent",
                    "timestamp": datetime.now().isoformat()
                }
                
            return {"status": "error", "error": "Insufficient data for correlation"}
            
        except Exception as e:
            logger.error(f"Failed to analyze price correlation: {e}")
            return {"status": "error", "error": str(e)}

    def _identify_sentiment_focus(self, message: str) -> Dict[str, Any]:
        """Identify sentiment analysis focus from natural language"""
        message = message.lower()
        
        # Detect assets
        assets = []
        for token, standard in self.monitored_assets.items():
            if token in message:
                assets.append(standard)

        # Default to major assets if none mentioned
        if not assets:
            assets = ['ETH', 'BTC']

        # Determine analysis focus
        if any(word in message for word in ['crowd', 'people', 'community', 'social']):
            focus = "social_sentiment"
        elif any(word in message for word in ['price', 'correlation', 'relationship']):
            focus = "price_correlation"
        elif any(word in message for word in ['trend', 'movement', 'direction']):
            focus = "trend_sentiment"
        elif any(word in message for word in ['meme', 'viral', 'hype']):
            focus = "meme_sentiment"
        else:
            focus = "general_sentiment"

        return {
            "assets": assets,
            "focus": focus
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process sentiment analysis requests conversationally"""
        try:
            sentiment_focus = self._identify_sentiment_focus(request.message)
            assets = sentiment_focus["assets"]
            focus = sentiment_focus["focus"]

            # Collect sentiment data for all assets
            sentiment_data = {}
            for asset in assets:
                token_sentiment = await self.analyze_token_sentiment(thread_id, asset)
                if token_sentiment["status"] == "success":
                    correlation = await self.analyze_price_correlation(
                        thread_id, asset, token_sentiment
                    )
                    sentiment_data[asset] = {
                        "sentiment": token_sentiment,
                        "correlation": correlation
                    }

            # Generate insights based on focus
            if focus == "social_sentiment":
                content = "Social Sentiment Analysis:\n\n"
                for asset, data in sentiment_data.items():
                    sentiment = data["sentiment"]
                    content += (
                        f"{asset} Community Sentiment:\n"
                        f"• Sentiment: {sentiment['sentiment'].title()}\n"
                        f"• Score: {sentiment['sentiment_score']:.2f}\n"
                        f"• Activity: Buy Volume {sentiment['buy_volume']:.2f}, "
                        f"Sell Volume {sentiment['sell_volume']:.2f}\n\n"
                    )
                content += "Would you like me to track any specific sentiment metrics?"

            elif focus == "price_correlation":
                content = "Price-Sentiment Correlation:\n\n"
                for asset, data in sentiment_data.items():
                    correlation = data["correlation"]
                    if correlation["status"] == "success":
                        content += (
                            f"{asset} Analysis:\n"
                            f"• Price: ${float(correlation['price']):,.2f}\n"
                            f"• Sentiment Score: {correlation['sentiment_score']:.2f}\n"
                            f"• Correlation: {correlation['correlation'].title()}\n\n"
                        )
                content += "Would you like me to analyze any specific correlations?"

            elif focus == "meme_sentiment":
                content = "Meme Token Sentiment:\n\n"
                for asset, data in sentiment_data.items():
                    sentiment = data["sentiment"]
                    content += (
                        f"{asset} Meme Analysis:\n"
                        f"• Hype Level: {sentiment['sentiment'].title()}\n"
                        f"• Community Activity: {'High' if sentiment['buy_volume'] > sentiment['sell_volume'] else 'Low'}\n"
                        f"• Trend Direction: {'Positive' if sentiment['sentiment_score'] > 0.5 else 'Negative'}\n\n"
                    )
                content += "Want me to monitor any specific meme tokens?"

            else:
                content = "Overall Sentiment Analysis:\n\n"
                for asset, data in sentiment_data.items():
                    sentiment = data["sentiment"]
                    correlation = data["correlation"]
                    content += (
                        f"{asset} Overview:\n"
                        f"• Market Sentiment: {sentiment['sentiment'].title()}\n"
                        f"• Price Movement: {'Aligned' if correlation['correlation'] == 'aligned' else 'Divergent'} with sentiment\n"
                        f"• Community Activity: {sentiment['buy_volume'] / (sentiment['sell_volume'] + 0.0001):.2f}x buy/sell ratio\n\n"
                    )
                content += "Which aspect would you like me to analyze further?"

            return AgentResponse(
                content=content,
                metadata={
                    "sentiment_focus": sentiment_focus,
                    "sentiment_data": sentiment_data,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue while analyzing market sentiment. "
                    "Could you specify which aspect you're most interested in? "
                    "I can look at social sentiment, price correlations, or meme trends."
                ),
                metadata={"status": "error", "error": str(e)}
            )