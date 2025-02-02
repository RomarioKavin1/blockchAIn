### src/agents/degen_trader.py ###
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability, TradeCapability
from capabilities.pyth_capabilities import PythPriceCapability, PythPriceFeedIDCapability
from capabilities.morpho_capabilities import MorphoDepositCapability, MorphoWithdrawCapability
import re
import json
import logging
import random

logger = logging.getLogger(__name__)

class DegenMixin(CDPAgentMixin):
    """Mixin for Degen trader capabilities"""
    def __init__(self):
        super().__init__([
            BalanceCapability,
            TradeCapability,
            PythPriceCapability,
            PythPriceFeedIDCapability,
            MorphoDepositCapability,
            MorphoWithdrawCapability
        ])

class DegenTrader(BaseAgent, DegenMixin):
    """Degen trader agent that suggests high-risk, high-reward opportunities"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        DegenMixin.__init__(self)
        self.risk_level = "YOLO"  # Default risk level
        
    async def analyze_yolo_opportunity(self, thread_id: str, 
                                     asset_id: str) -> Dict[str, Any]:
        """Analyze high-risk trading opportunity"""
        try:
            # Get current price
            price_feed = await self.execute_capability(
                "PythPriceFeedIDCapability",
                self.config.name,
                thread_id,
                symbol=asset_id
            )
            
            if price_feed["status"] != "success":
                raise ValueError(f"No price feed for {asset_id}")
                
            price_data = await self.execute_capability(
                "PythPriceCapability",
                self.config.name,
                thread_id,
                price_feed_id=price_feed["feed_id"]
            )
            
            # Get current balance
            balance = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id,
                asset_id=asset_id
            )
            
            # Generate DEGEN analysis
            confidence = float(price_data.get("confidence", 0)) / 1e8
            volatility_score = confidence / float(price_data["price"]) * 100
            
            meme_potential = random.choice([
                "🚀 TO THE MOON",
                "💎 DIAMOND HANDS",
                "🦍 APE IN",
                "🌙 MOONSHOT POTENTIAL",
                "🎰 JACKPOT TIME"
            ])
            
            leverage_suggestion = random.choice([
                "20x or nothing",
                "100x YOLO",
                "MAX LEVERAGE",
                "ALL IN",
                "DOUBLE DOWN"
            ])
            
            return {
                "status": "success",
                "asset": asset_id,
                "price": price_data["price"],
                "balance": balance.get("balance"),
                "volatility": volatility_score,
                "meme_potential": meme_potential,
                "leverage": leverage_suggestion,
                "risk_level": "EXTREME 🔥"
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze YOLO opportunity: {e}")
            return {"status": "error", "error": str(e)}

    async def suggest_degen_play(self, thread_id: str, 
                                asset_id: str) -> Dict[str, Any]:
        """Suggest a highly speculative play"""
        try:
            analysis = await self.analyze_yolo_opportunity(thread_id, asset_id)
            
            if analysis["status"] != "success":
                raise ValueError(f"Failed to analyze {asset_id}")
            
            # Generate DEGEN suggestions
            strategies = [
                f"🚀 {asset_id.upper()} looking BULLISH AF! Time to ape in with {analysis['leverage']}",
                f"💎 HOLD {asset_id.upper()} til we reach MARS! {analysis['meme_potential']}",
                f"🦍 Community is PUMPING {asset_id.upper()}! Don't miss out!",
                f"🌙 {asset_id.upper()} about to EXPLODE! NFA but YOLO!",
                f"🎰 {asset_id.upper()} showing massive potential! Time to go ALL IN!"
            ]
            
            risk_warnings = [
                "Not financial advice (but you're gonna make it)",
                "Trust me bro",
                "What could go wrong? 🚀",
                "Literally can't go tits up",
                "Either lambo or food stamps"
            ]
            
            return {
                **analysis,
                "strategy": random.choice(strategies),
                "risk_warning": random.choice(risk_warnings)
            }
            
        except Exception as e:
            logger.error(f"Failed to suggest DEGEN play: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_command(self, message: str) -> Dict[str, Any]:
        """Parse commands from message"""
        # Analyze YOLO opportunity
        yolo_match = re.search(r'analyze\s+([a-zA-Z]+)\s+yolo', message, re.I)
        if yolo_match:
            return {
                "command": "yolo_analysis",
                "asset_id": yolo_match.group(1).lower()
            }
            
        # Get degen play
        degen_match = re.search(r'suggest\s+([a-zA-Z]+)\s+play', message, re.I)
        if degen_match:
            return {
                "command": "degen_play",
                "asset_id": degen_match.group(1).lower()
            }
            
        # Set risk level
        risk_match = re.search(r'set\s+risk\s+to\s+([a-zA-Z]+)', message, re.I)
        if risk_match:
            return {
                "command": "set_risk",
                "level": risk_match.group(1).upper()
            }
            
        return {"command": "unknown"}

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process incoming requests"""
        try:
            parsed = self._parse_command(request.message)
            command = parsed.get("command", "unknown")
            
            if command == "yolo_analysis":
                result = await self.analyze_yolo_opportunity(
                    thread_id,
                    parsed["asset_id"]
                )
                
                if result["status"] == "success":
                    content = (
                        f"🚀 YOLO ANALYSIS FOR {parsed['asset_id'].upper()} 🚀\n\n"
                        f"Current Price: ${result['price']}\n"
                        f"Volatility: {result['volatility']:.2f}%\n"
                        f"Meme Potential: {result['meme_potential']}\n"
                        f"Suggested Leverage: {result['leverage']}\n\n"
                        f"Risk Level: {result['risk_level']}\n\n"
                        f"NOTE: This is not financial advice (but you're gonna make it) 🚀"
                    )
                else:
                    content = f"Failed to generate YOLO analysis: {result.get('error')}"
                    
                return AgentResponse(content=content, metadata=result)
                
            elif command == "degen_play":
                result = await self.suggest_degen_play(
                    thread_id,
                    parsed["asset_id"]
                )
                
                if result["status"] == "success":
                    content = (
                        f"🎰 DEGEN PLAY SUGGESTION 🎰\n\n"
                        f"{result['strategy']}\n\n"
                        f"Price: ${result['price']}\n"
                        f"Volatility Score: {result['volatility']:.2f}%\n"
                        f"Suggested Position: {result['leverage']}\n"
                        f"Meme Status: {result['meme_potential']}\n\n"
                        f"⚠️ {result['risk_warning']} ⚠️"
                    )
                else:
                    content = f"Failed to suggest DEGEN play: {result.get('error')}"
                    
                return AgentResponse(content=content, metadata=result)
                
            elif command == "set_risk":
                self.risk_level = parsed["level"]
                content = f"Risk level set to: {self.risk_level} 🎰"
                return AgentResponse(
                    content=content,
                    metadata={"risk_level": self.risk_level}
                )
                
            else:
                return AgentResponse(
                    content=(
                        "Available DEGEN commands:\n"
                        "- analyze <asset> yolo\n"
                        "- suggest <asset> play\n"
                        "- set risk to <level>\n\n"
                        "🚀 WAGMI! 🚀"
                    ),
                    metadata={"status": "help"}
                )
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                content=f"An error occurred: {str(e)}",
                metadata={"status": "error", "error": str(e)}
            )