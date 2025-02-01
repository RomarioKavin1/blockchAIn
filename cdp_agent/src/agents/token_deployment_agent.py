from typing import Dict, Any
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import TokenDeploymentMixin

import logging
import re

logger = logging.getLogger(__name__)
class TokenDeploymentAgent(BaseAgent, TokenDeploymentMixin):
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        TokenDeploymentMixin.__init__(self)
        
    def _parse_token_params(self, content: str) -> Dict[str, Any]:
        """Extract token parameters from the message content"""
        # Look for token name
        name_match = re.search(r'name[:\s]+(["\'])?([a-zA-Z0-9\s]+)\1?', content, re.IGNORECASE)
        name = name_match.group(2) if name_match else None

        # Look for token symbol
        symbol_match = re.search(r'symbol[:\s]+(["\'])?([a-zA-Z0-9]+)\1?', content, re.IGNORECASE)
        symbol = symbol_match.group(2) if symbol_match else None

        # Look for initial supply
        supply_match = re.search(r'supply[:\s]+(\d+)', content, re.IGNORECASE)
        supply = int(supply_match.group(1)) if supply_match else None

        return {
            "name": name,
            "symbol": symbol,
            "supply": supply
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process the token deployment request"""
        try:
            # Extract token parameters
            params = self._parse_token_params(request.message)
            
            # If parameters are missing, ask for them
            if not all([params["name"], params["symbol"], params["supply"]]):
                missing_params = []
                if not params["name"]:
                    missing_params.append("name")
                if not params["symbol"]:
                    missing_params.append("symbol")
                if not params["supply"] is None:
                    missing_params.append("initial supply")
                
                return AgentResponse(
                    content=f"I need the following information to deploy your token: {', '.join(missing_params)}. "
                           f"Please provide them in the format: name: <token name>, symbol: <token symbol>, supply: <initial supply>",
                    metadata={"status": "need_more_info", "missing_params": missing_params}
                )

            # Deploy the token
            deployment_result = await self.execute_capability(
                "DeployTokenCapability",
                self.config.name,
                thread_id,
                name=params["name"],
                symbol=params["symbol"],
                initial_supply=params["supply"]
            )

            if deployment_result["status"] == "success":
                response_content = (
                    f"✅ Successfully deployed your token!\n\n"
                    f"Token Details:\n"
                    f"- Name: {params['name']}\n"
                    f"- Symbol: {params['symbol']}\n"
                    f"- Initial Supply: {params['supply']}\n"
                    f"- Contract Address: {deployment_result['contract_address']}\n\n"
                    f"You can now trade this token or add it to wallets using the contract address."
                )
            else:
                response_content = (
                    f"❌ Token deployment failed:\n{deployment_result['error']}\n\n"
                    f"Please try again or provide different parameters."
                )

            return AgentResponse(
                content=response_content,
                metadata=deployment_result
            )

        except Exception as e:
            logger.error(f"Error processing token deployment: {e}")
            return AgentResponse(
                content=f"An error occurred while processing your request: {str(e)}",
                metadata={"status": "error", "error": str(e)}
            )