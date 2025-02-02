from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability, TradeCapability
from capabilities.pyth_capabilities import PythPriceCapability, PythPriceFeedIDCapability
from capabilities.morpho_capabilities import MorphoDepositCapability, MorphoWithdrawCapability
import logging

logger = logging.getLogger(__name__)

class FinancialAdvisorMixin(CDPAgentMixin):
    """Mixin for Financial Advisor capabilities"""
    def __init__(self):
        super().__init__([
            BalanceCapability,
            TradeCapability,
            PythPriceCapability,
            PythPriceFeedIDCapability,
            MorphoDepositCapability,
            MorphoWithdrawCapability
        ])

class FinancialAdvisor(BaseAgent, FinancialAdvisorMixin):
    """Financial Advisor agent that provides market insights and recommendations"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        FinancialAdvisorMixin.__init__(self)
        self.common_assets = {
            'eth': 'ETH', 'ethereum': 'ETH',
            'btc': 'BTC', 'bitcoin': 'BTC',
            'usdc': 'USDC',
            'usdt': 'USDT',
            'sol': 'SOL', 'solana': 'SOL',
            'matic': 'MATIC', 'polygon': 'MATIC'
        }

    async def get_market_context(self, thread_id: str, assets: List[str]) -> Dict[str, Any]:
        """Get comprehensive market context for assets"""
        results = {}
        try:
            for asset in assets:
                # Get price feed and data
                feed = await self.execute_capability(
                    "PythPriceFeedIDCapability",
                    self.config.name,
                    thread_id,
                    symbol=asset
                )
                
                if feed["status"] == "success":
                    price_data = await self.execute_capability(
                        "PythPriceCapability",
                        self.config.name,
                        thread_id,
                        price_feed_id=feed["feed_id"]
                    )
                    
                    if price_data["status"] == "success":
                        # Get user's balance for context
                        balance = await self.execute_capability(
                            "BalanceCapability",
                            self.config.name,
                            thread_id,
                            asset_id=asset
                        )
                        
                        # Get yield opportunities
                        yield_data = await self.execute_capability(
                            "MorphoDepositCapability",
                            self.config.name,
                            thread_id,
                            asset_id=asset
                        )
                        
                        results[asset] = {
                            "price": price_data["price"],
                            "confidence": price_data.get("confidence"),
                            "balance": balance.get("balance", 0),
                            "yield_opportunities": yield_data.get("opportunities", [])
                        }

            return {
                "status": "success",
                "data": results
            }

        except Exception as e:
            logger.error(f"Failed to get market context: {e}")
            return {"status": "error", "error": str(e)}

    def _identify_intent(self, message: str) -> Dict[str, Any]:
        """Identify user intent from natural language"""
        message = message.lower()
        
        # Detect mentioned assets
        mentioned_assets = []
        for token, standard_name in self.common_assets.items():
            if token in message:
                mentioned_assets.append(standard_name)

        # Default to major assets if none mentioned
        if not mentioned_assets:
            mentioned_assets = ['ETH', 'BTC']

        # Intent classification
        if any(word in message for word in ['price', 'worth', 'value', 'cost', 'market']):
            return {
                "intent": "market_analysis",
                "assets": mentioned_assets,
                "context": "price_focused"
            }
            
        if any(word in message for word in ['trade', 'swap', 'exchange', 'convert']):
            return {
                "intent": "trade_suggestion",
                "assets": mentioned_assets,
                "context": "trading"
            }
            
        if any(word in message for word in ['yield', 'earn', 'apy', 'farm', 'interest']):
            return {
                "intent": "yield_analysis",
                "assets": mentioned_assets,
                "context": "yield_focused"
            }
            
        if any(word in message for word in ['risk', 'safe', 'protect', 'secure', 'worried']):
            return {
                "intent": "risk_assessment",
                "assets": mentioned_assets,
                "context": "risk_focused"
            }
            
        if any(word in message for word in ['what', 'suggest', 'recommend', 'should', 'advice']):
            return {
                "intent": "general_advice",
                "assets": mentioned_assets,
                "context": "advisory"
            }

        return {
            "intent": "market_update",
            "assets": mentioned_assets,
            "context": "general"
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process requests in a conversational manner"""
        try:
            intent_data = self._identify_intent(request.message)
            intent = intent_data["intent"]
            assets = intent_data["assets"]
            context = intent_data["context"]

            # Get market context for all relevant assets
            market_data = await self.get_market_context(thread_id, assets)
            
            if market_data["status"] != "success":
                return AgentResponse(
                    content=(
                        "I'm having trouble accessing some market data at the moment. "
                        "Could you please specify which aspect of the market you're most interested in? "
                        "I can focus on prices, trading opportunities, or yield strategies."
                    ),
                    metadata={"status": "error", "error": market_data.get("error")}
                )

            data = market_data["data"]
            
            if intent == "market_analysis":
                content = "Based on current market data:\n\n"
                for asset, info in data.items():
                    content += (
                        f"{asset} is trading at ${float(info['price']):,.2f}. "
                        f"Your current position: {info['balance']} {asset}. "
                    )
                    
                if context == "price_focused":
                    content += "\n\nWould you like me to analyze any specific trading opportunities or yield strategies?"

            elif intent == "trade_suggestion":
                if len(assets) >= 2:
                    asset1, asset2 = assets[:2]
                    price1 = float(data[asset1]["price"])
                    price2 = float(data[asset2]["price"])
                    
                    content = (
                        f"Looking at {asset1}/{asset2} pair:\n\n"
                        f"{asset1}: ${price1:,.2f}\n"
                        f"{asset2}: ${price2:,.2f}\n\n"
                        f"Given current market conditions, "
                    )
                    
                    # Add trading suggestion based on user's holdings
                    if data[asset1]["balance"] > 0:
                        content += (
                            f"with your {data[asset1]['balance']} {asset1} position, "
                            f"you might consider a partial conversion to {asset2} "
                            f"to diversify. Would you like a detailed analysis of this trade?"
                        )
                    else:
                        content += (
                            f"you might consider starting with a small position. "
                            f"Would you like me to analyze optimal entry points?"
                        )
                else:
                    content = "Which assets are you interested in trading? I can provide specific analysis for any pair."

            elif intent == "yield_analysis":
                content = "Current yield opportunities:\n\n"
                for asset, info in data.items():
                    yield_opps = info.get("yield_opportunities", [])
                    if yield_opps:
                        content += f"{asset} Opportunities:\n"
                        for opp in yield_opps:
                            content += f"• {opp['protocol']}: {opp['apy']} APY\n"
                    else:
                        content += f"No significant yield opportunities found for {asset} at the moment.\n"
                
                content += "\nWould you like a risk analysis of any specific yield strategy?"

            elif intent == "risk_assessment":
                content = "Risk Analysis:\n\n"
                for asset, info in data.items():
                    confidence = float(info.get("confidence", 0)) / 1e8
                    volatility = confidence / float(info["price"]) * 100
                    
                    content += (
                        f"{asset}:\n"
                        f"• Price: ${float(info['price']):,.2f}\n"
                        f"• Volatility: {'High' if volatility > 5 else 'Moderate' if volatility > 2 else 'Low'}\n"
                        f"• Position Size: {info['balance']} {asset}\n\n"
                    )
                
                content += "Would you like specific risk mitigation recommendations?"

            else:
                # General market update
                content = "Here's your market update:\n\n"
                for asset, info in data.items():
                    content += (
                        f"{asset} is at ${float(info['price']):,.2f}. "
                        f"You're holding {info['balance']} {asset}.\n"
                    )
                    
                content += "\nWhat aspect would you like me to analyze in detail?"

            return AgentResponse(
                content=content,
                metadata={
                    "intent": intent,
                    "context": context,
                    "market_data": market_data,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                content=(
                    "I'm encountering some issues with market analysis at the moment. "
                    "Could you specify what information you're most interested in? "
                    "I can focus on specific assets or aspects of the market."
                ),
                metadata={"status": "error", "error": str(e)}
            )