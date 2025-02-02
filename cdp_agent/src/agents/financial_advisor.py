from typing import Dict, Any, Optional
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability, TradeCapability
from capabilities.pyth_capabilities import PythPriceCapability, PythPriceFeedIDCapability
from capabilities.morpho_capabilities import MorphoDepositCapability, MorphoWithdrawCapability
import re
import json
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
    """Financial Advisor agent that provides market insights and investment suggestions"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        FinancialAdvisorMixin.__init__(self)
        
    async def analyze_market(self, thread_id: str, asset_id: str) -> Dict[str, Any]:
        """Analyze market data for an asset"""
        try:
            # Get price feed ID
            feed_result = await self.execute_capability(
                "PythPriceFeedIDCapability",
                self.config.name,
                thread_id,
                symbol=asset_id
            )
            
            if feed_result["status"] != "success":
                raise ValueError(f"Failed to get price feed for {asset_id}")
                
            # Get price data
            price_result = await self.execute_capability(
                "PythPriceCapability",
                self.config.name,
                thread_id,
                price_feed_id=feed_result["feed_id"]
            )
            
            if price_result["status"] != "success":
                raise ValueError(f"Failed to get price data for {asset_id}")

            return {
                "status": "success",
                "asset": asset_id,
                "price": price_result["price"],
                "feed_id": feed_result["feed_id"],
                "confidence": price_result.get("confidence"),
                "last_updated": price_result.get("publish_time")
            }
        except Exception as e:
            logger.error(f"Failed to analyze market: {e}")
            return {"status": "error", "error": str(e)}

    async def analyze_yield_opportunities(self, thread_id: str, 
                                        asset_id: str) -> Dict[str, Any]:
        """Analyze yield opportunities for an asset"""
        try:
            # Get current balance
            balance_result = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id,
                asset_id=asset_id
            )
            
            # Get market data
            market_data = await self.analyze_market(thread_id, asset_id)
            
            if market_data["status"] != "success":
                raise ValueError(f"Failed to get market data for {asset_id}")

            return {
                "status": "success",
                "asset": asset_id,
                "balance": balance_result.get("balance"),
                "current_price": market_data["price"],
                "opportunities": [
                    {
                        "protocol": "Morpho",
                        "apy": "Calculate APY here",
                        "risk_level": "Calculate risk here"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Failed to analyze yield opportunities: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_command(self, message: str) -> Dict[str, Any]:
        """Parse commands from message"""
        # Analyze market
        market_match = re.search(r'analyze\s+market\s+for\s+([a-zA-Z]+)', message, re.I)
        if market_match:
            return {
                "command": "analyze_market",
                "asset_id": market_match.group(1).lower()
            }
            
        # Analyze yield
        yield_match = re.search(r'analyze\s+yield\s+for\s+([a-zA-Z]+)', message, re.I)
        if yield_match:
            return {
                "command": "analyze_yield",
                "asset_id": yield_match.group(1).lower()
            }
            
        # Suggest trade
        trade_match = re.search(
            r'suggest\s+trade\s+from\s+([a-zA-Z]+)\s+to\s+([a-zA-Z]+)', 
            message, 
            re.I
        )
        if trade_match:
            return {
                "command": "suggest_trade",
                "from_asset": trade_match.group(1).lower(),
                "to_asset": trade_match.group(2).lower()
            }
            
        return {"command": "unknown"}
    async def analyze_trade_opportunity(self, 
                                      from_analysis: Dict[str, Any], 
                                      to_analysis: Dict[str, Any]) -> str:
        """Analyze trade opportunity and provide detailed recommendation"""
        try:
            from_asset = from_analysis["asset"].upper()
            to_asset = to_analysis["asset"].upper()
            from_price = float(from_analysis["price"])
            to_price = float(to_analysis["price"])
            
            # For ETH to USDC analysis
            if from_asset == "ETH" and to_asset == "USDC":
                eth_value_in_usdc = from_price * 1  # 1 ETH value in USDC
                
                analysis = (
                    f"Trade Analysis: {from_asset} → {to_asset}\n\n"
                    f"Current Prices:\n"
                    f"• {from_asset}: ${from_price:,.2f}\n"
                    f"• {to_asset}: ${to_price:,.2f}\n\n"
                    f"Trade Value:\n"
                    f"• 1 ETH = {eth_value_in_usdc:,.2f} USDC\n\n"
                    f"Market Analysis:\n"
                )

                # Add market insights
                if from_asset == "ETH":
                    confidence = float(from_analysis["confidence"]) / 1e8
                    analysis += (
                        f"• Price Confidence: ±${confidence:,.2f}\n"
                        f"• Market Volatility: "
                        f"{'High' if confidence > 100 else 'Moderate' if confidence > 50 else 'Low'}\n"
                    )

                # Add recommendation
                analysis += "\nRecommendation:\n"
                if to_asset == "USDC":
                    analysis += "• Consider partial conversion to USDC if you need stable value\n"
                    analysis += "• Keep some ETH exposure for potential upside\n"
                    analysis += "• Suggested split: 70% ETH / 30% USDC for balanced risk\n"

                # Add action steps
                analysis += "\nSuggested Actions:\n"
                analysis += "1. Start with a small test transaction\n"
                analysis += "2. Monitor gas fees for optimal timing\n"
                analysis += "3. Consider using limit orders if available\n"

                # Add risk warnings
                analysis += "\nRisk Considerations:\n"
                analysis += "• Market volatility may affect execution price\n"
                analysis += "• Consider transaction costs (gas fees)\n"
                analysis += "• Monitor slippage during large trades\n"

            # For USDC to ETH analysis
            elif from_asset == "USDC" and to_asset == "ETH":
                usdc_value_in_eth = 1 / from_price  # 1 USDC value in ETH
                
                analysis = (
                    f"Trade Analysis: {from_asset} → {to_asset}\n\n"
                    f"Current Prices:\n"
                    f"• {from_asset}: ${to_price:,.2f}\n"
                    f"• {to_asset}: ${from_price:,.2f}\n\n"
                    f"Trade Value:\n"
                    f"• 1000 USDC = {(1000 * usdc_value_in_eth):.4f} ETH\n\n"
                    f"Market Analysis:\n"
                )

                # Add market insights
                confidence = float(to_analysis["confidence"]) / 1e8
                analysis += (
                    f"• Price Confidence: ±${confidence:,.2f}\n"
                    f"• Market Volatility: "
                    f"{'High' if confidence > 100 else 'Moderate' if confidence > 50 else 'Low'}\n"
                )

                # Add recommendation
                analysis += "\nRecommendation:\n"
                analysis += "• Consider DCA (Dollar Cost Averaging) into ETH\n"
                analysis += "• Split large trades into smaller portions\n"
                analysis += "• Suggested entry: 20% now, 80% over next 4 weeks\n"

                # Add action steps
                analysis += "\nSuggested Actions:\n"
                analysis += "1. Set up regular DCA intervals\n"
                analysis += "2. Monitor gas fees for optimal timing\n"
                analysis += "3. Consider limit orders for better entry\n"

                # Add risk warnings
                analysis += "\nRisk Considerations:\n"
                analysis += "• ETH price volatility risk\n"
                analysis += "• Consider transaction costs (gas fees)\n"
                analysis += "• Monitor market conditions regularly\n"

            else:
                # Generic analysis for other pairs
                analysis = (
                    f"Trade Analysis: {from_asset} → {to_asset}\n\n"
                    f"Current Prices:\n"
                    f"• {from_asset}: ${from_price:,.2f}\n"
                    f"• {to_asset}: ${to_price:,.2f}\n\n"
                    "Generic Trading Advice:\n"
                    "• Monitor market conditions\n"
                    "• Consider transaction costs\n"
                    "• Start with small test transactions\n"
                )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing trade opportunity: {e}")
            return "Failed to analyze trade opportunity"


    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process incoming requests"""
        try:
            # Parse command
            parsed = self._parse_command(request.message)
            command = parsed.get("command", "unknown")
            
            if command == "analyze_market":
                result = await self.analyze_market(thread_id, parsed["asset_id"])
                if result["status"] == "success":
                    content = (
                        f"Market Analysis for {parsed['asset_id'].upper()}:\n"
                        f"Current Price: ${result['price']}\n"
                    )
                    if result.get("confidence"):
                        content += f"Confidence: {result['confidence']}\n"
                    if result.get("last_updated"):
                        content += f"Last Updated: {result['last_updated']}\n"
                else:
                    content = f"Failed to analyze market: {result.get('error')}"
                    
                return AgentResponse(content=content, metadata=result)
                
            elif command == "analyze_yield":
                result = await self.analyze_yield_opportunities(
                    thread_id, 
                    parsed["asset_id"]
                )
                if result["status"] == "success":
                    content = (
                        f"Yield Analysis for {parsed['asset_id'].upper()}:\n"
                        f"Current Price: ${result['current_price']}\n"
                    )
                    if result.get("balance"):
                        content += f"Your Balance: {result['balance']}\n"
                    content += "\nAvailable Opportunities:\n"
                    for opp in result.get("opportunities", []):
                        content += (
                            f"- {opp['protocol']}: {opp['apy']} APY "
                            f"(Risk: {opp['risk_level']})\n"
                        )
                else:
                    content = f"Failed to analyze yield: {result.get('error')}"
                    
                return AgentResponse(content=content, metadata=result)
                
            elif command == "suggest_trade":
                from_analysis = await self.analyze_market(
                    thread_id, 
                    parsed["from_asset"]
                )
                to_analysis = await self.analyze_market(
                    thread_id, 
                    parsed["to_asset"]
                )
                
                if from_analysis["status"] == "success" and to_analysis["status"] == "success":
                    content = await self.analyze_trade_opportunity(from_analysis, to_analysis)
                else:
                    content = "Failed to analyze trade opportunity"
                
                return AgentResponse(
                    content=content,
                    metadata={
                        "from_analysis": from_analysis,
                        "to_analysis": to_analysis
                    }
                )
                
            else:
                return AgentResponse(
                    content=(
                        "Available commands:\n"
                        "- analyze market for <asset>\n"
                        "- analyze yield for <asset>\n"
                        "- suggest trade from <asset> to <asset>"
                    ),
                    metadata={"status": "help"}
                )
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                content=f"An error occurred: {str(e)}",
                metadata={"status": "error", "error": str(e)}
            )