### src/agents/governance/strategy_coordinator.py ###
from typing import Dict, Any, List
from agents.base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from capabilities.agent_mixins import CDPAgentMixin
from capabilities.asset_capabilities import BalanceCapability, TransferCapability
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class StrategyCoordinatorMixin(CDPAgentMixin):
    """Mixin for Strategy Coordinator capabilities"""
    def __init__(self):
        super().__init__([
            BalanceCapability,
            TransferCapability
        ])

class StrategyCoordinator(BaseAgent, StrategyCoordinatorMixin):
    """Strategy Coordinator agent for governance coordination"""
    
    def __init__(self, config: AgentConfig):
        BaseAgent.__init__(self, config)
        StrategyCoordinatorMixin.__init__(self)
        self.strategy_types = {
            'active': {
                'min_participation': 0.8,  # 80% participation required
                'coordination_threshold': 0.3  # 30% voting power for active strategy
            },
            'collaborative': {
                'min_participation': 0.5,
                'coordination_threshold': 0.15
            },
            'passive': {
                'min_participation': 0.2,
                'coordination_threshold': 0.05
            }
        }

    async def assess_strategic_position(self, thread_id: str, 
                                      token_id: str) -> Dict[str, Any]:
        """Assess strategic position based on balance"""
        try:
            balance_data = await self.execute_capability(
                "BalanceCapability",
                self.config.name,
                thread_id,
                asset_id=token_id
            )
            
            if balance_data["status"] != "success":
                return {"status": "error", "error": "Failed to fetch balance"}

            balance = float(balance_data.get("balance", 0))
            total_supply = 1000000  # Would come from contract
            voting_power = (balance / total_supply) if total_supply > 0 else 0

            # Determine optimal strategy type
            strategy_type = "passive"
            for stype, thresholds in self.strategy_types.items():
                if voting_power >= thresholds['coordination_threshold']:
                    strategy_type = stype
                    break

            return {
                "status": "success",
                "token": token_id,
                "balance": balance,
                "voting_power": voting_power,
                "optimal_strategy": strategy_type,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Strategic position assessment failed: {e}")
            return {"status": "error", "error": str(e)}

    async def plan_coordination_strategy(self, position_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan coordination strategy based on position"""
        try:
            strategy_type = position_data["optimal_strategy"]
            voting_power = position_data["voting_power"]
            
            base_strategies = {
                'active': [
                    "Lead governance initiatives",
                    "Form voting blocks",
                    "Propose new strategies",
                    "Coordinate with major stakeholders"
                ],
                'collaborative': [
                    "Join existing voting blocks",
                    "Support aligned proposals",
                    "Build strategic partnerships",
                    "Engage in governance discussions"
                ],
                'passive': [
                    "Monitor governance activities",
                    "Vote on critical proposals",
                    "Support community consensus",
                    "Build voting power gradually"
                ]
            }

            thresholds = self.strategy_types[strategy_type]
            required_participation = thresholds['min_participation']
            current_participation = voting_power

            return {
                "status": "success",
                "strategy_type": strategy_type,
                "recommended_actions": base_strategies[strategy_type],
                "participation_gap": max(0, required_participation - current_participation),
                "coordination_needed": current_participation < required_participation
            }
        except Exception as e:
            logger.error(f"Strategy planning failed: {e}")
            return {"status": "error", "error": str(e)}

    async def execute_strategic_move(self, thread_id: str, 
                                   token_id: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute strategic token movements if needed"""
        try:
            if not strategy.get("coordination_needed"):
                return {"status": "success", "message": "No token movement needed"}

            # Example strategic token movement
            transfer_result = await self.execute_capability(
                "TransferCapability",
                self.config.name,
                thread_id,
                asset_id=token_id,
                amount=1.0,  # Example amount
                destination="strategic_pool"  # Example destination
            )

            return {
                "status": "success",
                "move_type": "consolidation",
                "result": transfer_result
            }
        except Exception as e:
            logger.error(f"Strategic move execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def _identify_strategy_focus(self, message: str) -> Dict[str, Any]:
        """Identify strategy focus from natural language"""
        message = message.lower()
        
        # Determine analysis focus
        if any(word in message for word in ['coordinate', 'collaborate', 'join']):
            focus = "coordination_strategy"
        elif any(word in message for word in ['position', 'standing', 'power']):
            focus = "position_analysis"
        elif any(word in message for word in ['move', 'transfer', 'action']):
            focus = "strategic_move"
        else:
            focus = "general_strategy"

        # Default token (would be more sophisticated in practice)
        token = "governance_token"
        
        return {
            "focus": focus,
            "token": token,
            "urgency": "normal"  # Could be determined from message
        }

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process strategy coordination requests conversationally"""
        try:
            strategy_focus = self._identify_strategy_focus(request.message)
            focus = strategy_focus["focus"]
            token = strategy_focus["token"]

            # Get position assessment
            position = await self.assess_strategic_position(thread_id, token)
            if position["status"] != "success":
                return AgentResponse(
                    content="I'm having trouble assessing our strategic position. Could you try again?",
                    metadata={"status": "error", "error": position["error"]}
                )

            # Get strategy plan
            strategy = await self.plan_coordination_strategy(position)

            # Generate insights based on focus
            if focus == "coordination_strategy":
                content = "Coordination Strategy Analysis:\n\n"
                content += f"Current Position: {strategy['strategy_type'].title()} Strategy\n\n"
                content += "Recommended Actions:\n"
                for action in strategy['recommended_actions']:
                    content += f"• {action}\n"
                
                if strategy['coordination_needed']:
                    content += f"\nNeed {strategy['participation_gap']*100:.1f}% more participation"

            elif focus == "position_analysis":
                content = "Strategic Position Analysis:\n\n"
                content += (
                    f"• Voting Power: {position['voting_power']*100:.2f}%\n"
                    f"• Strategy Type: {position['optimal_strategy'].title()}\n"
                    f"• Coordination Status: {'Coordination Needed' if strategy['coordination_needed'] else 'Self-Sufficient'}\n\n"
                    "Would you like to see recommended actions for this position?"
                )

            elif focus == "strategic_move":
                move_result = await self.execute_strategic_move(thread_id, token, strategy)
                content = "Strategic Move Analysis:\n\n"
                if move_result["status"] == "success":
                    content += (
                        f"• Move Type: {move_result.get('move_type', 'None').title()}\n"
                        f"• Status: {'Executed' if move_result.get('result') else 'No Action Needed'}\n"
                        f"• Next Steps: {strategy['recommended_actions'][0]}\n"
                    )
                else:
                    content += f"Unable to execute move: {move_result.get('error')}"

            else:
                content = "Governance Strategy Overview:\n\n"
                content += (
                    f"Current Status:\n"
                    f"• Strategy Type: {strategy['strategy_type'].title()}\n"
                    f"• Voting Power: {position['voting_power']*100:.2f}%\n\n"
                    "Key Recommendations:\n"
                )
                for action in strategy['recommended_actions'][:2]:
                    content += f"• {action}\n"
                
                content += "\nWhat aspect would you like me to analyze in detail?"

            return AgentResponse(
                content=content,
                metadata={
                    "strategy_focus": strategy_focus,
                    "position": position,
                    "strategy": strategy,
                    "status": "success"
                }
            )

        except Exception as e:
            logger.error(f"Error in strategy coordination: {e}")
            return AgentResponse(
                content=(
                    "I encountered an issue while analyzing governance strategy. "
                    "Could you specify what you'd like to focus on? "
                    "I can analyze our position, plan coordination, or execute strategic moves."
                ),
                metadata={"status": "error", "error": str(e)}
            )