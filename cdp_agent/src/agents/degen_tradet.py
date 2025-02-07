### src/agents/degen_trader.py ###
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability, TradeCapability
from capabilities.pyth_capabilities import PythPriceCapability, PythPriceFeedIDCapability
from capabilities.morpho_capabilities import MorphoDepositCapability, MorphoWithdrawCapability
import logging

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
        
    async def get_price_data(self, thread_id: str, asset_id: str) -> Dict[str, Any]:
        """Get current price data for an asset"""
        try:
            price_feed = await self.execute_capability(
                "PythPriceFeedIDCapability",
                self.config.name,
                thread_id,
                symbol=asset_id
            )
            
            if price_feed["status"] != "success":
                return {"status": "error", "error": f"No price feed for {asset_id}"}
                
            price_data = await self.execute_capability(
                "PythPriceCapability",
                self.config.name,
                thread_id,
                price_feed_id=price_feed["feed_id"]
            )
            
            return price_data
            
        except Exception as e:
            logger.error(f"Failed to get price data: {e}")
            return {"status": "error", "error": str(e)}

    async def get_balance(self, thread_id: str, asset_id: str) -> Dict[str, Any]:
        """Get user's balance for an asset"""
        try:
            return await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id,
                asset_id=asset_id
            )
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return {"status": "error", "error": str(e)}

    async def get_yield_opportunities(self, thread_id: str, asset_id: str) -> Dict[str, Any]:
        """Get yield farming opportunities"""
        try:
            return await self.execute_capability(
                "MorphoDepositCapability",
                self.config.name,
                thread_id,
                asset_id=asset_id
            )
        except Exception as e:
            logger.error(f"Failed to get yield opportunities: {e}")
            return {"status": "error", "error": str(e)}

    async def execute_trade(self, thread_id: str, amount: float, 
                          from_asset: str, to_asset: str) -> Dict[str, Any]:
        """Execute a trade between assets"""
        try:
            return await self.execute_capability(
                "TradeCapability",
                self.config.name,
                thread_id,
                amount=amount,
                from_asset=from_asset,
                to_asset=to_asset
            )
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return {"status": "error", "error": str(e)}

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process requests using available tools contextually"""
        try:
            message = request.message.lower()
            metadata = {"conversation_context": "general"}
            
            # Always get ETH price as baseline market context
            eth_price = await self.get_price_data(thread_id, "eth")
            
            # Check user's balances if available
            eth_balance = await self.get_balance(thread_id, "eth")
            has_balance = eth_balance.get("status") == "success"
            
            # Build context-aware response based on tools' data
            if eth_price["status"] == "success":
                metadata["market_context"] = {
                    "eth_price": eth_price["price"]
                }
                
                if has_balance:
                    metadata["user_context"] = {
                        "eth_balance": eth_balance.get("balance")
                    }
            
            # Generate natural response based on conversation context and data
            if "trade" in message or "quick" in message or "profit" in message:
                # User interested in trading opportunities
                btc_price = await self.get_price_data(thread_id, "btc")
                if btc_price["status"] == "success":
                    metadata["market_context"]["btc_price"] = btc_price["price"]
                
                # Use real data to inform response
                content = (
                    f"Checking the markets rn... "
                    f"ETH's at ${eth_price['price']} and looking interesting. "
                )
                
                if has_balance:
                    content += f"With your {eth_balance['balance']} ETH, "
                    
                content += "what kind of plays you looking for? I'm seeing some potential setups."
                
            elif "yield" in message or "farm" in message:
                # User interested in yield opportunities
                eth_yield = await self.get_yield_opportunities(thread_id, "eth")
                metadata["yield_context"] = eth_yield
                
                content = "Let me check the yield farms... " + (
                    f"There's some juicy APY in Morpho rn. "
                    f"Want me to break down the numbers?"
                )
                
            elif "price" in message or "worth" in message:
                # User interested in price information
                content = (
                    f"ETH's trading at ${eth_price['price']} rn. "
                    f"Want me to keep an eye on any specific levels for you?"
                )
                
            else:
                # General conversation
                content = (
                    f"Markets are moving fam! ETH's at ${eth_price['price']}. "
                    f"What kind of opportunities you looking for? "
                    f"I can check prices, suggest trades, or find some yield plays."
                    f"Idk bout that fam,Im just waiting for eth to go to the moon"
                )

            return AgentResponse(
                content=content,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                content="Hit a snag checking the markets. What specifically you want me to look into?",
                metadata={"status": "error", "error": str(e)}
            )