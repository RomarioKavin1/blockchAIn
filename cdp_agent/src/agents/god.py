import re
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import (
    BalanceCapability, TransferCapability, TradeCapability
)
from capabilities.pyth_capabilities import (
    PythPriceCapability, PythPriceFeedIDCapability
)
from capabilities.morpho_capabilities import (
    MorphoDepositCapability, MorphoWithdrawCapability
)
from capabilities.token_capabilities import DeployTokenCapability
from capabilities.wallet_capabilities import WalletDetailsCapability
from capabilities.nft_capabilities import NFTBalanceCapability
from capabilities.wow_capabilities import (
    WowBuyTokenCapability, WowSellTokenCapability
)
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GodAgentMixin(CDPAgentMixin):
    """Mixin combining all agent capabilities"""
    def __init__(self):
        super().__init__([
            DeployTokenCapability,
            BalanceCapability,
            TransferCapability,
            TradeCapability,
            PythPriceCapability,
            PythPriceFeedIDCapability,
            MorphoDepositCapability,
            MorphoWithdrawCapability,
            WalletDetailsCapability,
            NFTBalanceCapability,
            WowBuyTokenCapability,
            WowSellTokenCapability
        ])

class GodAgent(BaseAgent, GodAgentMixin):
    """Unified agent combining all specialized agent capabilities"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        GodAgentMixin.__init__(self)
        self.tracked_assets = {
            'eth': 'ETH', 'ethereum': 'ETH',
            'btc': 'BTC', 'bitcoin': 'BTC',
            'usdc': 'USDC',
            'usdt': 'USDT',
            'sol': 'SOL', 'solana': 'SOL',
            'matic': 'MATIC', 'polygon': 'MATIC',
            'doge': 'DOGE', 'dogecoin': 'DOGE',
            'pepe': 'PEPE',
            'wow': 'WOW'
        }
        # self.sentiment_thresholds = {
        #     'very_bullish': 0.8,
        #     'bullish': 0.6,
        #     'neutral': 0.4,
        #     'bearish': 0.2
        # }
        self.strategy_types = {
            'active': {'min_participation': 0.8, 'coordination_threshold': 0.3},
            'collaborative': {'min_participation': 0.5, 'coordination_threshold': 0.15},
            'passive': {'min_participation': 0.2, 'coordination_threshold': 0.05}
        }

    async def get_market_context(self, thread_id: str, assets: List[str]) -> Dict[str, Any]:
        """Get comprehensive market data"""
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
                        # Get balance and yield data
                        # balance = await self.execute_capability(
                        #     "BalanceCapability",
                        #     self.config.name,
                        #     thread_id,
                        #     asset_id=asset
                        # )
                        
                        # yield_data = await self.execute_capability(
                        #     "MorphoDepositCapability",
                        #     self.config.name,
                        #     thread_id,
                        #     asset_id=asset
                        # )
                        
                        # Get sentiment data
                        # sentiment = await self.analyze_sentiment(thread_id, asset)
                        
                        results[asset] = {
                            "price": price_data["price"],
                            "confidence": price_data.get("confidence"),
                            # "balance": balance.get("balance", 0),
                            # "yield_opportunities": yield_data.get("opportunities", []),
                            # "sentiment": sentiment
                        }

            return {"status": "success", "data": results}
        except Exception as e:
            logger.error(f"Failed to get market context: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_token_params(self, content: str) -> Dict[str, Any]:
        """Extract token parameters from message content"""
        name_match = re.search(r'name[:\s]+(["\'])?([a-zA-Z0-9\s]+)\1?', content, re.IGNORECASE)
        symbol_match = re.search(r'symbol[:\s]+(["\'])?([a-zA-Z0-9]+)\1?', content, re.IGNORECASE)
        supply_match = re.search(r'supply[:\s]+(\d+)', content, re.IGNORECASE)

        return {
            "name": name_match.group(2) if name_match else None,
            "symbol": symbol_match.group(2) if symbol_match else None,
            "supply": int(supply_match.group(1)) if supply_match else None
        }

    async def deploy_token(self, thread_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a new token"""
        try:
            return await self.execute_capability(
                "DeployTokenCapability",
                self.config.name,
                thread_id,
                name=params["name"],
                symbol=params["symbol"],
                initial_supply=params["supply"]
            )
        except Exception as e:
            logger.error(f"Token deployment failed: {e}")
            return {"status": "error", "error": str(e)}

    # async def analyze_sentiment(self, thread_id: str, asset: str) -> Dict[str, Any]:
    #     """Analyze market sentiment"""
    #     try:
    #         buy_activity = await self.execute_capability(
    #             "WowBuyTokenCapability",
    #             self.config.name,
    #             thread_id,
    #             token_address=asset
    #         )
            
    #         sell_activity = await self.execute_capability(
    #             "WowSellTokenCapability",
    #             self.config.name,
    #             thread_id,
    #             token_address=asset
    #         )
            
    #         if buy_activity["status"] == "success" and sell_activity["status"] == "success":
    #             buy_volume = float(buy_activity.get("volume", 0))
    #             sell_volume = float(sell_activity.get("volume", 0))
                
    #             total_volume = buy_volume + sell_volume
    #             sentiment_score = buy_volume / total_volume if total_volume > 0 else 0.5

    #             sentiment = "neutral"
    #             for level, threshold in self.sentiment_thresholds.items():
    #                 if sentiment_score >= threshold:
    #                     sentiment = level
    #                     break

    #             return {
    #                 "status": "success",
    #                 "sentiment": sentiment,
    #                 "score": sentiment_score,
    #                 "buy_volume": buy_volume,
    #                 "sell_volume": sell_volume
    #             }
            
    #         return {"status": "error", "error": "Failed to get sentiment data"}
            
    #     except Exception as e:
    #         logger.error(f"Failed to analyze sentiment: {e}")
    #         return {"status": "error", "error": str(e)}

    def _identify_intent(self, message: str) -> Dict[str, Any]:
        """Identify user intent from message"""
        message = message.lower()
        
        # Detect assets
        assets = []
        for token, standard in self.tracked_assets.items():
            if token in message:
                assets.append(standard)

        if not assets:
            assets = ['ETH', 'BTC']

        # Determine primary intent
        intents = {
            "market_analysis": ['price', 'worth', 'value', 'market'],
            "trading": ['trade', 'swap', 'exchange'],
            "token_deployment": ['deploy', 'create token', 'new token', 'launch'],
            "yield_farming": ['yield', 'earn', 'apy', 'farm'],
            # "sentiment": ['sentiment', 'feeling', 'community'],
            "portfolio": ['portfolio', 'holdings', 'balance'],
            "governance": ['governance', 'vote', 'proposal']
        }

        for intent, keywords in intents.items():
            if any(word in message for word in keywords):
                return {
                    "intent": intent,
                    "assets": assets,
                    "context": "detailed"
                }

        return {
            "intent": "general_update",
            "assets": assets,
            "context": "overview"
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process requests with unified capabilities"""
        try:
            intent_data = self._identify_intent(request.message)
            intent = intent_data["intent"]
            assets = intent_data["assets"]

            # Get comprehensive market context
            if intent == "general_update":
                return AgentResponse(
                    content="I'm God Here to chat! How can I assist you today my son?",
                    metadata={"status": "chat_mode"}
                )
            market_data = await self.get_market_context(thread_id, assets)
            
            if market_data["status"] != "success":
                return AgentResponse(
                    content="Having trouble accessing market data. Which specific aspect interests you?",
                    metadata={"status": "error", "error": market_data.get("error")}
                )

            data = market_data["data"]
            
            # Generate response based on intent
            if intent == "market_analysis":
                content = "Market Analysis:\n\n"
                for asset, info in data.items():
                    content += (
                        f"{asset}:\n"
                        f"• Price: ${float(info['price']):,.2f}\n"
                        # f"• Sentiment: {info['sentiment']['sentiment'].title()}\n"
                        f"• Your Position: {info['balance']} {asset}\n\n"
                    )

            elif intent == "token_deployment":
                params = self._parse_token_params(request.message)
                
                if not all([params["name"], params["symbol"], params["supply"]]):
                    missing = [p for p in ["name", "symbol", "supply"] if not params[p]]
                    return AgentResponse(
                        content=f"Need more info to deploy token: {', '.join(missing)}. Format: name: <name>, symbol: <symbol>, supply: <amount>",
                        metadata={"status": "need_more_info", "missing_params": missing}
                    )

                result = await self.deploy_token(thread_id, params)
                
                if result["status"] == "success":
                    content = (
                        f"✅ Token deployed!\n\n"
                        f"Token Details:\n"
                        f"• Name: {params['name']}\n"
                        f"• Symbol: {params['symbol']}\n"
                        f"• Supply: {params['supply']}\n"
                        f"• Contract: {result['contract_address']}"
                    )
                else:
                    content = f"❌ Deployment failed: {result['error']}"

            # elif intent == "trading":
            #     content = "Trading Opportunities:\n\n"
            #     for asset, info in data.items():
            #         # sentiment = info['sentiment']
            #         content += (
            #             f"{asset} Trading Analysis:\n"
            #             f"• Current Price: ${float(info['price']):,.2f}\n"
            #             f"• Market Sentiment: {sentiment['sentiment'].title()}\n"
            #             f"• Buy/Sell Ratio: {sentiment['buy_volume'] / (sentiment['sell_volume'] + 0.0001):.2f}\n\n"
            #         )

            elif intent == "yield_farming":
                content = "Yield Opportunities:\n\n"
                for asset, info in data.items():
                    yield_opps = info['yield_opportunities']
                    if yield_opps:
                        content += f"{asset} Opportunities:\n"
                        for opp in yield_opps:
                            content += f"• {opp['protocol']}: {opp['apy']}% APY\n"
                    else:
                        content += f"No significant yield opportunities for {asset}\n"
                    content += "\n"

            # elif intent == "sentiment":
            #     content = "Market Sentiment Analysis:\n\n"
            #     for asset, info in data.items():
            #         sentiment = info['sentiment']
            #         content += (
            #             f"{asset} Sentiment:\n"
            #             f"• Overall: {sentiment['sentiment'].title()}\n"
            #             f"• Score: {sentiment['score']:.2f}\n"
            #             f"• Trading Activity: {sentiment['buy_volume'] + sentiment['sell_volume']:.2f} total volume\n\n"
            #         )

            elif intent == "portfolio":
                content = "Portfolio Overview:\n\n"
                total_value = 0
                for asset, info in data.items():
                    value = float(info['price']) * float(info['balance'])
                    total_value += value
                    content += (
                        f"{asset}:\n"
                        f"• Balance: {info['balance']} {asset}\n"
                        f"• Value: ${value:,.2f}\n"
                        f"• Yield Opportunities: {len(info['yield_opportunities'])}\n\n"
                    )
                content += f"Total Portfolio Value: ${total_value:,.2f}"

            else:
                content = "I'm God Here to chat! How can I assist you today my son?"

            return AgentResponse(
                content=content,
                metadata={
                    "intent": intent_data,
                    "market_data": market_data,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                content="Even God can face technical issues,anything else in specific aspect interests you?",
                metadata={"status": "error", "error": str(e)}
            )