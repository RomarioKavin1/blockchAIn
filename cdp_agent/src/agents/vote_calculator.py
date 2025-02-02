### src/agents/governance/vote_calculator.py ###
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class VoteCalculatorMixin(CDPAgentMixin):
    """Mixin for Vote Calculator capabilities"""
    def __init__(self):
        super().__init__([
            BalanceCapability
        ])

class VoteCalculator(BaseAgent, VoteCalculatorMixin):
    """Vote Calculator agent for voting power optimization"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        VoteCalculatorMixin.__init__(self)
        self.voting_thresholds = {
            'quorum': 0.04,  # 4% for quorum
            'supermajority': 0.67,  # 67% for special proposals
            'majority': 0.51  # 51% for standard proposals
        }

    async def calculate_voting_power(self, thread_id: str, asset_id: str) -> Dict[str, Any]:
        """Calculate voting power based on token balance"""
        try:
            balance_data = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id,
                asset_id=asset_id
            )
            
            if balance_data["status"] != "success":
                return {"status": "error", "error": "Failed to fetch balance"}

            balance = float(balance_data.get("balance", 0))
            total_supply = 1000000  # This would come from contract
            
            voting_power = {
                "raw_power": balance,
                "percentage": (balance / total_supply) * 100 if total_supply > 0 else 0,
                "quorum_contribution": balance / (total_supply * self.voting_thresholds['quorum']),
                "can_meet_quorum": balance >= (total_supply * self.voting_thresholds['quorum'])
            }

            return {
                "status": "success",
                "asset": asset_id,
                "voting_power": voting_power,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Voting power calculation failed: {e}")
            return {"status": "error", "error": str(e)}

    async def analyze_voting_strategy(self, voting_power: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze optimal voting strategy based on power"""
        try:
            power_percentage = voting_power["voting_power"]["percentage"]
            
            strategies = []
            if power_percentage >= self.voting_thresholds['supermajority'] * 100:
                strategies.append("Can single-handedly pass special proposals")
            elif power_percentage >= self.voting_thresholds['majority'] * 100:
                strategies.append("Can single-handedly pass standard proposals")
            elif power_percentage >= self.voting_thresholds['quorum'] * 100:
                strategies.append("Can single-handedly meet quorum")
            else:
                needed_for_quorum = (self.voting_thresholds['quorum'] * 100) - power_percentage
                strategies.append(f"Need {needed_for_quorum:.1f}% more for quorum")

            return {
                "status": "success",
                "strategies": strategies,
                "optimal_timing": "immediate" if power_percentage > 5 else "wait for more votes",
                "collaboration_needed": power_percentage < self.voting_thresholds['majority'] * 100
            }
        except Exception as e:
            logger.error(f"Strategy analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    def _identify_voting_focus(self, message: str) -> Dict[str, Any]:
        """Identify voting analysis focus from natural language"""
        message = message.lower()
        
        # Determine analysis focus
        if any(word in message for word in ['power', 'strength', 'weight']):
            focus = "power_calculation"
        elif any(word in message for word in ['strategy', 'how to', 'best way']):
            focus = "strategy_analysis"
        elif any(word in message for word in ['quorum', 'threshold', 'minimum']):
            focus = "threshold_analysis"
        else:
            focus = "general_analysis"

        # Detect governance token (simplified)
        token = 'governance_token'  # You would implement proper token detection
        
        return {
            "focus": focus,
            "token": token,
            "threshold_type": "standard"  # Could be special based on message
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process voting calculation requests conversationally"""
        try:
            voting_focus = self._identify_voting_focus(request.message)
            focus = voting_focus["focus"]
            token = voting_focus["token"]

            # Get voting power data
            power_data = await self.calculate_voting_power(thread_id, token)
            if power_data["status"] != "success":
                return AgentResponse(
                    content="I'm having trouble accessing voting power data. Could you try again?",
                    metadata={"status": "error", "error": power_data["error"]}
                )

            # Get strategy analysis
            strategy = await self.analyze_voting_strategy(power_data)

            # Generate insights based on focus
            if focus == "power_calculation":
                content = "Voting Power Analysis:\n\n"
                vp = power_data["voting_power"]
                content += (
                    f"Current Voting Power:\n"
                    f"• Raw Power: {vp['raw_power']:,.0f} tokens\n"
                    f"• Percentage: {vp['percentage']:.2f}%\n"
                    f"• Quorum Contribution: {vp['quorum_contribution']*100:.1f}% of needed quorum\n\n"
                    "Would you like to explore potential voting strategies?"
                )

            elif focus == "strategy_analysis":
                content = "Voting Strategy Analysis:\n\n"
                for strat in strategy["strategies"]:
                    content += f"• {strat}\n"
                
                if strategy["collaboration_needed"]:
                    content += "\nCollaboration Strategy:\n"
                    content += "• Consider forming voting blocks\n"
                    content += "• Engage with other token holders\n"
                    content += "• Monitor voting patterns\n"

            elif focus == "threshold_analysis":
                content = "Threshold Analysis:\n\n"
                vp = power_data["voting_power"]
                content += (
                    f"Current Position:\n"
                    f"• Your Power: {vp['percentage']:.2f}%\n"
                    f"• Quorum Requirement: {self.voting_thresholds['quorum']*100}%\n"
                    f"• Standard Majority: {self.voting_thresholds['majority']*100}%\n"
                    f"• Super Majority: {self.voting_thresholds['supermajority']*100}%\n"
                )

            else:
                content = "Voting Power Overview:\n\n"
                vp = power_data["voting_power"]
                content += (
                    f"• Voting Power: {vp['percentage']:.2f}%\n"
                    f"• Status: {strategy['strategies'][0]}\n"
                    f"• Recommended Timing: {strategy['optimal_timing'].title()}\n\n"
                    "What aspect would you like me to analyze in detail?"
                )

            return AgentResponse(
                content=content,
                metadata={
                    "voting_focus": voting_focus,
                    "power_data": power_data,
                    "strategy": strategy,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error in vote calculation: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue while calculating voting power. "
                    "Could you specify what you'd like to know? "
                    "I can analyze voting power, strategy options, or threshold requirements."
                ),
                metadata={"status": "error", "error": str(e)}
            )