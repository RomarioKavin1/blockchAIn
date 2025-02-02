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
        
        # Token mapping
        self.asset_tokens = {
            'btc': 'btc', 'bitcoin': 'btc',
            'eth': 'eth', 'ethereum': 'eth',
            'usdc': 'usdc', 'usdt': 'usdt',
            'sol': 'sol', 'solana': 'sol',
            'matic': 'matic', 'polygon': 'matic',
            'doge': 'doge', 'dogecoin': 'doge'
        }

    def _identify_intent(self, message: str) -> Dict[str, Any]:
        """Identify the user's intent from natural language"""
        message = message.lower()

        # Look for assets mentioned in the message
        mentioned_assets = []
        for token, asset_id in self.asset_tokens.items():
            if token in message:
                mentioned_assets.append(asset_id)
        
        # Intent classification with example phrases
        intents = {
            "price_check": [
                'price', 'worth', 'value', 'cost', 'how much', 'what is', 'trading at'
            ],
            "degen_play": [
                'moon', 'pump', 'ape', 'yolo', 'all in', 'fomo', 'send it', 'lfg',
                'bullish', 'leverage', '100x', 'massive', 'explosion'
            ],
            "opportunity_analysis": [
                'opportunity', 'chance', 'potential', 'possible', 'good time',
                'should i', 'what about', 'thinking about', 'consider'
            ],
            "risk_assessment": [
                'risk', 'safe', 'dangerous', 'careful', 'worried', 'scared',
                'concerned', 'downside'
            ]
        }

        # Check each intent
        for intent, keywords in intents.items():
            if any(word in message for word in keywords):
                return {
                    "intent": intent,
                    "assets": mentioned_assets
                }

        # If no specific intent but assets mentioned
        if mentioned_assets:
            return {
                "intent": "general_analysis",
                "assets": mentioned_assets
            }

        return {
            "intent": "unknown",
            "assets": []
        }
        
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
            
            if price_data["status"] != "success":
                raise ValueError(f"Failed to get price for {asset_id}")

            # Get current balance
            balance = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id,
                asset_id=asset_id
            )
            
            # Generate DEGEN analysis
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

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process incoming requests naturally"""
        try:
            # Identify intent and context
            intent_data = self._identify_intent(request.message)
            intent = intent_data["intent"]
            assets = intent_data["assets"]

            # If no assets found but intent is clear, use default assets
            if not assets and intent != "unknown":
                assets = ["eth"]  # Default to ETH if no asset specified
            
            if intent == "unknown":
                return AgentResponse(
                    content=(
                        "Yo fam! 🚀 Not sure what you're looking for, but I can help you:\n"
                        "- Find the next moonshot\n"
                        "- Spot degen opportunities\n"
                        "- Give you price updates\n"
                        "- Suggest high-risk plays\n\n"
                        "Just tell me what you're interested in! BTC? ETH? Let's make some moves! 💎🙌"
                    ),
                    metadata={"status": "help"}
                )

            # Handle different intents
            responses = []
            for asset in assets:
                if intent == "price_check":
                    analysis = await self.analyze_yolo_opportunity(thread_id, asset)
                    if analysis["status"] == "success":
                        responses.append(
                            f"🚨 {asset.upper()} is at ${analysis['price']} rn!\n"
                            f"Looking {analysis['meme_potential']} fam!"
                        )

                elif intent == "degen_play":
                    play = await self.suggest_degen_play(thread_id, asset)
                    if play["status"] == "success":
                        responses.append(
                            f"{play['strategy']}\n"
                            f"Current price: ${play['price']}\n"
                            f"{play['risk_warning']}"
                        )

                elif intent in ["opportunity_analysis", "general_analysis"]:
                    analysis = await self.analyze_yolo_opportunity(thread_id, asset)
                    play = await self.suggest_degen_play(thread_id, asset)
                    
                    if analysis["status"] == "success" and play["status"] == "success":
                        responses.append(
                            f"🔥 {asset.upper()} OPPORTUNITY ALERT 🔥\n\n"
                            f"{play['strategy']}\n"
                            f"Price: ${analysis['price']}\n"
                            f"Vibe Check: {analysis['meme_potential']}\n"
                            f"Move: {play['leverage']}\n\n"
                            f"Trust me bro! 🚀"
                        )

                elif intent == "risk_assessment":
                    analysis = await self.analyze_yolo_opportunity(thread_id, asset)
                    if analysis["status"] == "success":
                        responses.append(
                            f"Risk Assessment for {asset.upper()} (but who cares about risk?):\n"
                            f"- Price: ${analysis['price']}\n"
                            f"- Volatility: BULLISH AF!\n"
                            f"- Sentiment: {analysis['meme_potential']}\n"
                            f"- WAGMI Rating: 💯\n\n"
                            f"Remember: We don't do risk management here! 🎰"
                        )

            if responses:
                return AgentResponse(
                    content="\n\n".join(responses),
                    metadata={
                        "intent": intent,
                        "assets": assets,
                        "status": "success"
                    }
                )
            else:
                return AgentResponse(
                    content="Bruh... Something went wrong. But WAGMI! 🚀",
                    metadata={"status": "error"}
                )

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                content="Even degens have bad days... Something went wrong but we'll bounce back! 💪",
                metadata={"status": "error", "error": str(e)}
            )