from typing import Dict, Any, Optional
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability, TransferCapability
from capabilities.wallet_capabilities import WalletDetailsCapability
from capabilities.nft_capabilities import NFTBalanceCapability
import re
import logging
import json

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
        self.approved_agents = set()  # Set of approved agent IDs
        
    async def check_balances(self, thread_id: str) -> Dict[str, Any]:
        """Check all balances including tokens and NFTs"""
        try:
            # Get token balances
            balance_result = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id
            )
            
            # Get NFT balances
            nft_result = await self.execute_capability(
                "NFTBalanceCapability",
                self.config.name,
                thread_id
            )
            
            return {
                "tokens": balance_result.get("balances", {}),
                "nfts": nft_result.get("balances", {})
            }
        except Exception as e:
            logger.error(f"Failed to check balances: {e}")
            return {"error": str(e)}

    async def approve_agent(self, agent_id: str) -> bool:
        """Add an agent to the approved list"""
        self.approved_agents.add(agent_id)
        return True

    async def revoke_agent(self, agent_id: str) -> bool:
        """Remove an agent from the approved list"""
        if agent_id in self.approved_agents:
            self.approved_agents.remove(agent_id)
            return True
        return False

    async def fund_agent(self, thread_id: str, agent_id: str, 
                        amount: float, asset_id: str) -> Dict[str, Any]:
        """Transfer funds to another agent"""
        if agent_id not in self.approved_agents:
            return {
                "status": "error",
                "error": "Agent not approved for funding"
            }
            
        try:
            # Get target agent's wallet details
            agent_wallet = await self.execute_capability(
                "WalletDetailsCapability",
                agent_id,
                thread_id
            )
            
            if agent_wallet.get("status") != "success":
                raise ValueError("Failed to get agent wallet details")
                
            # Transfer funds
            transfer_result = await self.execute_capability(
                "TransferCapability",
                self.config.name,
                thread_id,
                amount=amount,
                asset_id=asset_id,
                destination=agent_wallet["address"]
            )
            
            return transfer_result
        except Exception as e:
            logger.error(f"Failed to fund agent: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _parse_command(self, message: str) -> Dict[str, Any]:
        """Parse commands from message"""
        # Check balances
        if re.search(r'check\s+balances?', message, re.I):
            return {"command": "check_balances"}
            
        # Fund agent command
        fund_match = re.search(
            r'fund\s+agent\s+([a-zA-Z0-9-]+)\s+with\s+(\d+\.?\d*)\s+([a-zA-Z]+)', 
            message, 
            re.I
        )
        if fund_match:
            return {
                "command": "fund_agent",
                "agent_id": fund_match.group(1),
                "amount": float(fund_match.group(2)),
                "asset_id": fund_match.group(3).lower()
            }
            
        # Approve agent command
        approve_match = re.search(r'approve\s+agent\s+([a-zA-Z0-9-]+)', message, re.I)
        if approve_match:
            return {
                "command": "approve_agent",
                "agent_id": approve_match.group(1)
            }
            
        # Revoke agent command
        revoke_match = re.search(r'revoke\s+agent\s+([a-zA-Z0-9-]+)', message, re.I)
        if revoke_match:
            return {
                "command": "revoke_agent",
                "agent_id": revoke_match.group(1)
            }
            
        return {"command": "unknown"}

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process incoming requests"""
        try:
            # Parse command from message
            parsed = self._parse_command(request.message)
            command = parsed.get("command", "unknown")
            
            if command == "check_balances":
                balances = await self.check_balances(thread_id)
                return AgentResponse(
                    content=f"Current balances:\n{json.dumps(balances, indent=2)}",
                    metadata=balances
                )
                
            elif command == "fund_agent":
                result = await self.fund_agent(
                    thread_id,
                    parsed["agent_id"],
                    parsed["amount"],
                    parsed["asset_id"]
                )
                
                if result.get("status") == "success":
                    content = (
                        f"Successfully funded agent {parsed['agent_id']} "
                        f"with {parsed['amount']} {parsed['asset_id']}"
                    )
                else:
                    content = f"Failed to fund agent: {result.get('error')}"
                    
                return AgentResponse(content=content, metadata=result)
                
            elif command == "approve_agent":
                success = await self.approve_agent(parsed["agent_id"])
                content = (
                    f"Agent {parsed['agent_id']} {'approved' if success else 'approval failed'}"
                )
                return AgentResponse(
                    content=content,
                    metadata={"status": "success" if success else "error"}
                )
                
            elif command == "revoke_agent":
                success = await self.revoke_agent(parsed["agent_id"])
                content = (
                    f"Agent {parsed['agent_id']} {'revoked' if success else 'not found'}"
                )
                return AgentResponse(
                    content=content,
                    metadata={"status": "success" if success else "error"}
                )
                
            else:
                return AgentResponse(
                    content=(
                        "Available commands:\n"
                        "- check balances\n"
                        "- fund agent <agent-id> with <amount> <asset>\n"
                        "- approve agent <agent-id>\n"
                        "- revoke agent <agent-id>"
                    ),
                    metadata={"status": "help"}
                )
                
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return AgentResponse(
                content=f"An error occurred: {str(e)}",
                metadata={"status": "error", "error": str(e)}
            )