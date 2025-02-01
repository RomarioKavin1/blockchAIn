from typing import Dict, Any, List, Type
from .cdp_base import CDPCapability, WalletManager

# Import all capabilities
from .asset_capabilities import (
    BalanceCapability, TransferCapability, 
    TradeCapability, WrapETHCapability
)
from .nft_capabilities import (
    NFTBalanceCapability, DeployNFTCapability,
    MintNFTCapability, TransferNFTCapability
)
from .token_capabilities import DeployTokenCapability
from .morpho_capabilities import (
    MorphoDepositCapability, MorphoWithdrawCapability
)
from .pyth_capabilities import (
    PythPriceCapability, PythPriceFeedIDCapability
)
from .wallet_capabilities import (
    WalletDetailsCapability, RegisterBasenameCapability
)
from .wow_capabilities import (
    WowCreateTokenCapability, WowBuyTokenCapability,
    WowSellTokenCapability
)

class CDPAgentMixin:
    """Base mixin for adding CDP capabilities to agents"""
    
    def __init__(self, capabilities: List[Type[CDPCapability]] = None):
        self.wallet_manager = WalletManager("data/agent_wallets.json")
        self.capabilities: Dict[str, CDPCapability] = {}
        if capabilities:
            for cap in capabilities:
                self.add_capability(cap())

    def add_capability(self, capability: CDPCapability):
        """Add a CDP capability to the agent"""
        self.capabilities[capability.__class__.__name__] = capability

    async def execute_capability(self, capability_name: str, agent_name: str, 
                               thread_id: str, **kwargs) -> Dict[str, Any]:
        """Execute a specific CDP capability"""
        if capability_name not in self.capabilities:
            return {
                "status": "error",
                "error": f"Capability {capability_name} not found"
            }
        return await self.capabilities[capability_name].execute(
            agent_name, thread_id, **kwargs
        )

class TokenDeploymentMixin(CDPAgentMixin):
    """Mixin for token deployment capabilities"""
    def __init__(self):
        super().__init__([
            DeployTokenCapability,
            BalanceCapability
        ])
        
class AssetManagementMixin(CDPAgentMixin):
    """Mixin for basic asset management capabilities"""
    def __init__(self):
        super().__init__([
            BalanceCapability,
            TransferCapability,
            TradeCapability,
            WrapETHCapability
        ])

class NFTManagementMixin(CDPAgentMixin):
    """Mixin for NFT-related capabilities"""
    def __init__(self):
        super().__init__([
            NFTBalanceCapability,
            DeployNFTCapability,
            MintNFTCapability,
            TransferNFTCapability
        ])

class DefiManagementMixin(CDPAgentMixin):
    """Mixin for DeFi-specific capabilities"""
    def __init__(self):
        super().__init__([
            MorphoDepositCapability,
            MorphoWithdrawCapability,
            PythPriceCapability,
            PythPriceFeedIDCapability,
            TradeCapability
        ])

class WalletManagementMixin(CDPAgentMixin):
    """Mixin for wallet management capabilities"""
    def __init__(self):
        super().__init__([
            WalletDetailsCapability,
            RegisterBasenameCapability,
            BalanceCapability
        ])

class TokenManagementMixin(CDPAgentMixin):
    """Mixin for token-related capabilities"""
    def __init__(self):
        super().__init__([
            DeployTokenCapability,
            WowCreateTokenCapability,
            WowBuyTokenCapability,
            WowSellTokenCapability
        ])

class FullCDPAgentMixin(CDPAgentMixin):
    """Mixin that includes all CDP capabilities"""
    def __init__(self):
        super().__init__([
            # Asset capabilities
            BalanceCapability,
            TransferCapability,
            TradeCapability,
            WrapETHCapability,
            
            # NFT capabilities
            NFTBalanceCapability,
            DeployNFTCapability,
            MintNFTCapability,
            TransferNFTCapability,
            
            # Token capabilities
            DeployTokenCapability,
            
            # Morpho capabilities
            MorphoDepositCapability,
            MorphoWithdrawCapability,
            
            # Pyth capabilities
            PythPriceCapability,
            PythPriceFeedIDCapability,
            
            # Wallet capabilities
            WalletDetailsCapability,
            RegisterBasenameCapability,
            
            # Wow capabilities
            WowCreateTokenCapability,
            WowBuyTokenCapability,
            WowSellTokenCapability
        ])

# Specialized mixins for your specific agents
class PersonalAccountantMixin(CDPAgentMixin):
    """Mixin for Personal Accountant agent"""
    def __init__(self):
        super().__init__([
            BalanceCapability,
            TransferCapability,
            NFTBalanceCapability,
            WalletDetailsCapability,
            PythPriceCapability
        ])

class DeFiAdvisorMixin(CDPAgentMixin):
    """Mixin for Financial Advisor agent"""
    def __init__(self):
        super().__init__([
            BalanceCapability,
            PythPriceCapability,
            PythPriceFeedIDCapability,
            MorphoDepositCapability,
            MorphoWithdrawCapability,
            TradeCapability
        ])

class DegenTraderMixin(CDPAgentMixin):
    """Mixin for Degen Trader agent"""
    def __init__(self):
        super().__init__([
            TradeCapability,
            WowCreateTokenCapability,
            WowBuyTokenCapability,
            WowSellTokenCapability,
            PythPriceCapability
        ])

class ResearchAnalystMixin(CDPAgentMixin):
    """Mixin for Research agents"""
    def __init__(self):
        super().__init__([
            PythPriceCapability,
            PythPriceFeedIDCapability,
            BalanceCapability
        ])

class GovernanceAdvisorMixin(CDPAgentMixin):
    """Mixin for Governance agents"""
    def __init__(self):
        super().__init__([
            WalletDetailsCapability,
            BalanceCapability,
            TransferCapability
        ])
