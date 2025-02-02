### src/agents/governance/proposal_analyzer.py ###
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.wallet_capabilities import WalletDetailsCapability
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProposalAnalyzerMixin(CDPAgentMixin):
    """Mixin for Proposal Analyzer capabilities"""
    def __init__(self):
        super().__init__([
            WalletDetailsCapability
        ])

class ProposalAnalyzer(BaseAgent, ProposalAnalyzerMixin):
    """Proposal Analyzer agent for DAO governance analysis"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        ProposalAnalyzerMixin.__init__(self)
        self.stakeholder_categories = {
            'whale': 1000000,  # Example threshold
            'medium': 100000,
            'small': 10000
        }

    async def analyze_stakeholders(self, thread_id: str, address: str) -> Dict[str, Any]:
        """Analyze stakeholder details and categorize them"""
        try:
            stakeholder_data = await self.execute_capability(
                "WalletDetailsCapability",
                self.config.name,
                thread_id,
                address=address
            )
            
            if stakeholder_data["status"] != "success":
                return {"status": "error", "error": "Failed to fetch stakeholder data"}

            # Categorize stakeholder
            balance = float(stakeholder_data.get("balance", 0))
            category = "small"
            for cat, threshold in self.stakeholder_categories.items():
                if balance >= threshold:
                    category = cat
                    break

            return {
                "status": "success",
                "address": address,
                "category": category,
                "voting_power": balance,
                "activity_level": stakeholder_data.get("activity_level", "low")
            }
        except Exception as e:
            logger.error(f"Stakeholder analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    def _identify_proposal_focus(self, message: str) -> Dict[str, Any]:
        """Identify proposal analysis focus from natural language"""
        message = message.lower()
        
        # Determine analysis focus
        if any(word in message for word in ['stakeholder', 'holder', 'whale']):
            focus = "stakeholder_analysis"
        elif any(word in message for word in ['vote', 'voting', 'power']):
            focus = "voting_analysis"
        elif any(word in message for word in ['impact', 'effect', 'result']):
            focus = "impact_analysis"
        else:
            focus = "general_analysis"

        # Extract addresses if present (simplified example)
        addresses = []  # You would implement proper address extraction
        
        return {
            "focus": focus,
            "addresses": addresses,
            "proposal_type": "general"  # Could be expanded based on message
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process proposal analysis requests conversationally"""
        try:
            analysis_focus = self._identify_proposal_focus(request.message)
            focus = analysis_focus["focus"]
            addresses = analysis_focus["addresses"]

            # Use example addresses if none provided
            if not addresses:
                addresses = ["0xexample"]  # You would handle this properly

            # Analyze stakeholders
            stakeholder_data = {}
            for address in addresses:
                analysis = await self.analyze_stakeholders(thread_id, address)
                if analysis["status"] == "success":
                    stakeholder_data[address] = analysis

            # Generate insights based on focus
            if focus == "stakeholder_analysis":
                content = "Stakeholder Analysis:\n\n"
                for address, data in stakeholder_data.items():
                    content += (
                        f"Address {address[:6]}...{address[-4:]}:\n"
                        f"• Category: {data['category'].title()}\n"
                        f"• Voting Power: {data['voting_power']:,.0f}\n"
                        f"• Activity Level: {data['activity_level'].title()}\n\n"
                    )
                content += "Would you like me to analyze any specific stakeholders?"

            elif focus == "voting_analysis":
                total_power = sum(data["voting_power"] for data in stakeholder_data.values())
                content = (
                    f"Voting Power Analysis:\n\n"
                    f"Total Analyzed Power: {total_power:,.0f}\n\n"
                    "Distribution:\n"
                )
                for category in ['whale', 'medium', 'small']:
                    category_power = sum(
                        data["voting_power"] for data in stakeholder_data.values()
                        if data["category"] == category
                    )
                    if category_power > 0:
                        percentage = (category_power / total_power) * 100
                        content += f"• {category.title()}: {percentage:.1f}%\n"

            else:
                content = "Proposal Stakeholder Overview:\n\n"
                categories = {cat: 0 for cat in self.stakeholder_categories.keys()}
                for data in stakeholder_data.values():
                    categories[data["category"]] += 1
                
                for category, count in categories.items():
                    if count > 0:
                        content += f"• {category.title()} Stakeholders: {count}\n"
                
                content += "\nHow would you like to analyze these stakeholders?"

            return AgentResponse(
                content=content,
                metadata={
                    "analysis_focus": analysis_focus,
                    "stakeholder_data": stakeholder_data,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error in proposal analysis: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue while analyzing the proposal. "
                    "Could you specify what aspects you'd like me to focus on? "
                    "I can analyze stakeholders, voting power, or overall impact."
                ),
                metadata={"status": "error", "error": str(e)}
            )
        