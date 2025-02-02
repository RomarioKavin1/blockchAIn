### src/agents/personal_accountant.py ###
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability, TransferCapability
from capabilities.wallet_capabilities import WalletDetailsCapability
from capabilities.nft_capabilities import NFTBalanceCapability
import logging

logger = logging.getLogger(__name__)

class PersonalAccountantMixin(CDPAgentMixin):
    """Mixin for Personal Accountant capabilities"""
    def __init__(self):
        super().__init__([
            BalanceCapability,
            TransferCapability,
            WalletDetailsCapability,
            NFTBalanceCapability
        ])

class PersonalAccountant(BaseAgent, PersonalAccountantMixin):
    """Personal Accountant agent that manages funds and provides inter-agent transfers"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        PersonalAccountantMixin.__init__(self)
        self.approved_agents = set()
        self.common_assets = {
            'eth': 'ETH', 'ethereum': 'ETH',
            'usdc': 'USDC',
            'usdt': 'USDT',
            'btc': 'BTC', 'bitcoin': 'BTC'
        }

    async def get_portfolio_summary(self, thread_id: str) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        try:
            # Get token balances
            token_result = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id
            )
            
            # For NFTs, we need specific contract addresses
            # This is a placeholder - you would need to maintain a list of NFT contracts you want to track
            nft_contracts = [
                "0x123...",  # Example NFT contract address
            ]
            
            nft_balances = {}
            for contract in nft_contracts:
                nft_result = await self.execute_capability(
                    "NFTBalanceCapability",
                    self.config.name,
                    thread_id,
                    contract_address=contract
                )
                if nft_result.get("status") == "success":
                    nft_balances[contract] = nft_result.get("balance", 0)

            # Get wallet status
            wallet_result = await self.execute_capability(
                "WalletDetailsCapability",
                self.config.name,
                thread_id
            )

            # Return combined results
            return {
                "status": "success",
                "tokens": token_result.get("balances", {}),
                "nfts": nft_balances,
                "wallet": wallet_result
            }

        except Exception as e:
            logger.error(f"Failed to get portfolio summary: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "tokens": {},
                "nfts": {},
                "wallet": {}
            }
    def _identify_intent(self, message: str) -> Dict[str, Any]:
        """Identify user intent from natural language"""
        message = message.lower()
        
        # Detect mentioned assets
        mentioned_assets = []
        for token, standard_name in self.common_assets.items():
            if token in message:
                mentioned_assets.append(standard_name)

        # Detect agents
        agent_mention = None
        if "agent" in message:
            # Try to find agent ID in message
            words = message.split()
            for i, word in enumerate(words):
                if word == "agent" and i + 1 < len(words):
                    agent_mention = words[i + 1]

        # Intent classification
        intents = {
            "check_balance": [
                'balance', 'holding', 'have', 'own', 'worth', 'portfolio'
            ],
            "transfer_funds": [
                'send', 'transfer', 'move', 'give', 'fund', 'allocate'
            ],
            "agent_management": [
                'approve', 'revoke', 'allow', 'permission', 'access'
            ],
            "wallet_status": [
                'wallet', 'address', 'account', 'status'
            ]
        }

        # Check each intent
        for intent, keywords in intents.items():
            if any(word in message for word in keywords):
                return {
                    "intent": intent,
                    "assets": mentioned_assets,
                    "agent": agent_mention
                }

        # Default to portfolio overview if no specific intent
        return {
            "intent": "portfolio_overview",
            "assets": mentioned_assets,
            "agent": agent_mention
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process requests in a conversational manner"""
        try:
            intent_data = self._identify_intent(request.message)
            intent = intent_data["intent"]
            assets = intent_data["assets"]
            agent = intent_data["agent"]

            # Always get portfolio summary for context
            portfolio = await self.get_portfolio_summary(thread_id)
            
            if portfolio["status"] == "error":
                logger.warning(f"Portfolio fetch error: {portfolio['error']}")
                # Continue with available data

            if intent == "check_balance":
                if assets:
                    # Specific asset balance check
                    balances = portfolio.get("tokens", {})
                    responses = []
                    for asset in assets:
                        balance = balances.get(asset.lower(), 0)
                        responses.append(f"Your {asset} balance is {balance}")
                    
                    content = ". ".join(responses)
                    content += "\n\nWould you like to see your other holdings as well?"
                else:
                    # Full portfolio overview
                    token_balances = portfolio.get("tokens", {})
                    nft_balances = portfolio.get("nfts", {})
                    
                    content = "Here's your current portfolio summary:\n\n"
                    
                    if token_balances:
                        content += "Token Holdings:\n"
                        for token, balance in token_balances.items():
                            content += f"• {token.upper()}: {balance}\n"
                    else:
                        content += "No token holdings found.\n"
                    
                    if nft_balances:
                        content += "\nNFT Holdings:\n"
                        for contract, balance in nft_balances.items():
                            content += f"• Collection {contract[:6]}...{contract[-4:]}: {balance}\n"

            elif intent == "transfer_funds" and agent:
                if agent not in self.approved_agents:
                    content = (
                        f"I notice you're trying to transfer funds to {agent}. "
                        f"This agent isn't currently approved. Would you like me to "
                        f"set up approval first? I can then help with the transfer."
                    )
                else:
                    amount = 0.1  # Default amount, should be extracted from message
                    asset = assets[0] if assets else "ETH"
                    
                    content = (
                        f"I can help transfer funds to {agent}. "
                        f"I see you have {portfolio['tokens'].get(asset.lower(), 0)} {asset}. "
                        f"How much would you like to transfer?"
                    )

            elif intent == "agent_management":
                if agent:
                    if "revoke" in request.message.lower():
                        self.approved_agents.discard(agent)
                        content = f"I've revoked {agent}'s access. They can no longer receive funds."
                    else:
                        self.approved_agents.add(agent)
                        content = (
                            f"I've approved {agent} for fund transfers. "
                            f"You can now allocate funds to them as needed. "
                            f"Would you like to set up a transfer now?"
                        )
                else:
                    content = (
                        "Currently approved agents:\n" +
                        "\n".join(f"• {agent}" for agent in self.approved_agents)
                    )

            else:
                # Default portfolio overview
                content = (
                    "I can help you manage your portfolio and handle fund transfers. "
                    "Would you like to:\n"
                    "• See your current holdings?\n"
                    "• Transfer funds to another agent?\n"
                    "• Check specific asset balances?\n"
                    "Just let me know what you need assistance with."
                )

            return AgentResponse(
                content=content,
                metadata={
                    "intent": intent,
                    "portfolio": portfolio,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue while processing your request. "
                    "Could you please specify what information you're looking for? "
                    "I can check balances, handle transfers, or provide a portfolio overview."
                ),
                metadata={"status": "error", "error": str(e)}
            )