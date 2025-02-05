// config/agents.ts
import { Agent, Swarm, AgentGroup } from "@/types/agents";

export const agentGroups: AgentGroup[] = [
  {
    id: "defai",
    name: "deFAI",
    description: "Core financial management and analysis agents",
  },
  {
    id: "research",
    name: "Research",
    description: "Market research and analysis specialists",
  },
  {
    id: "governance",
    name: "Governance",
    description: "DAO governance and strategy experts",
  },
  {
    id: "god",
    name: "Supreme",
    description: "Ultimate controller with unlimited power",
  },
];
const allCapabilities = [
  {
    name: "BalanceCapability",
    description: "Complete balance and portfolio management across all chains",
  },
  {
    name: "TransferCapability",
    description: "Universal fund transfer and management",
  },
  {
    name: "WalletDetailsCapability",
    description: "Complete wallet analysis and management",
  },
  {
    name: "NFTBalanceCapability",
    description: "Comprehensive NFT portfolio tracking",
  },
  {
    name: "TradeCapability",
    description: "Advanced trading strategy and execution",
  },
  {
    name: "PythPriceCapability",
    description: "Universal price data and market analysis",
  },
  {
    name: "PythPriceFeedIDCapability",
    description: "Advanced price feed management",
  },
  {
    name: "MorphoDepositCapability",
    description: "Yield optimization and management",
  },
  {
    name: "MorphoWithdrawCapability",
    description: "Strategic position management",
  },
  {
    name: "WowBuyTokenCapability",
    description: "Trend analysis and momentum trading",
  },
  {
    name: "WowSellTokenCapability",
    description: "Market sentiment and exit strategy",
  },
];

export const agents: Agent[] = [
  // deFAI Group
  {
    id: "personal-accountant",
    name: "Personal Accountant",
    type: "Finance",
    group: "defai",
    description:
      "Your trusted financial manager with complete fund access and management capabilities",
    capabilities: [
      {
        name: "BalanceCapability",
        description: "Check all asset balances across wallets",
      },
      {
        name: "TransferCapability",
        description: "Manage and execute fund transfers",
      },
      {
        name: "WalletDetailsCapability",
        description: "Comprehensive wallet management",
      },
      {
        name: "NFTBalanceCapability",
        description: "Track and manage NFT assets",
      },
    ],
    avatarUrl: "/avatars/personal-accountant.png",
  },
  {
    id: "financial-advisor",
    name: "Financial Advisor",
    type: "Finance",
    group: "defai",
    description:
      "Strategic advisor providing deep financial insights and investment recommendations",
    capabilities: [
      {
        name: "BalanceCapability",
        description: "Analysis of balance positions",
      },
      {
        name: "TradeCapability",
        description: "Strategic trade recommendations",
      },
      {
        name: "PythPriceCapability",
        description: "Real-time price data analysis",
      },
      {
        name: "PythPriceFeedIDCapability",
        description: "Advanced price feed monitoring",
      },
      {
        name: "MorphoDepositCapability",
        description: "Yield opportunity analysis",
      },
      {
        name: "MorphoWithdrawCapability",
        description: "Yield management optimization",
      },
    ],
    avatarUrl: "/avatars/financial-advisor.png",
  },
  {
    id: "degen",
    name: "Degen",
    type: "Trading",
    group: "defai",
    description:
      "High-risk, high-reward strategist with deep social media insights",
    capabilities: [
      {
        name: "BalanceCapability",
        description: "Portfolio analysis for opportunities",
      },
      { name: "TradeCapability", description: "Execute high-potential trades" },
      { name: "PythPriceCapability", description: "Price movement analysis" },
      {
        name: "PythPriceFeedIDCapability",
        description: "Market data monitoring",
      },
      {
        name: "MorphoDepositCapability",
        description: "Yield farming opportunities",
      },
      {
        name: "MorphoWithdrawCapability",
        description: "Quick position management",
      },
    ],
    avatarUrl: "/avatars/degen.png",
  },
  {
    id: "risk-manager",
    name: "Risk Manager",
    type: "Finance",
    group: "defai",
    description: "Ensures portfolio safety and monitors risk exposure",
    capabilities: [
      { name: "BalanceCapability", description: "Position risk monitoring" },
      { name: "PythPriceCapability", description: "Price risk assessment" },
      {
        name: "MorphoDepositCapability",
        description: "Yield strategy risk analysis",
      },
      {
        name: "MorphoWithdrawCapability",
        description: "Emergency position management",
      },
    ],
    avatarUrl: "/avatars/risk-manager.png",
  },
  {
    id: "god-agent",
    name: "Universal Controller",
    type: "Supreme",
    group: "god",
    description:
      "The ultimate agent with unlimited access and capabilities across all domains. Combines financial expertise, research prowess, and governance mastery.",
    capabilities: allCapabilities,
    avatarUrl: "/avatars/god.png",
  },

  // Research Group
  {
    id: "data-scientist",
    name: "Data Scientist",
    type: "Research",
    group: "research",
    description: "Advanced on-chain data analysis and pattern recognition",
    capabilities: [
      {
        name: "BalanceCapability",
        description: "Deep data analysis of positions",
      },
      { name: "PythPriceCapability", description: "Price data analysis" },
      {
        name: "PythPriceFeedIDCapability",
        description: "Market data correlation",
      },
    ],
    avatarUrl: "/avatars/data-scientist.png",
  },
  {
    id: "news-aggregator",
    name: "News Aggregator",
    type: "Research",
    group: "research",
    description: "Real-time news monitoring and impact analysis",
    capabilities: [
      { name: "PythPriceCapability", description: "News impact on prices" },
      {
        name: "WalletDetailsCapability",
        description: "Whale wallet monitoring",
      },
    ],
    avatarUrl: "/avatars/news-aggregator.png",
  },
  {
    id: "pattern-detector",
    name: "Pattern Detector",
    type: "Research",
    group: "research",
    description: "Identifies market patterns and trading opportunities",
    capabilities: [
      {
        name: "PythPriceCapability",
        description: "Pattern recognition in price data",
      },
      {
        name: "TradeCapability",
        description: "Pattern-based trade verification",
      },
      { name: "BalanceCapability", description: "Volume pattern analysis" },
    ],
    avatarUrl: "/avatars/pattern-detector.png",
  },
  {
    id: "sentiment-analyzer",
    name: "Sentiment Analyzer",
    type: "Research",
    group: "research",
    description: "Social media and market sentiment analysis",
    capabilities: [
      { name: "WowBuyTokenCapability", description: "Trend momentum analysis" },
      {
        name: "WowSellTokenCapability",
        description: "Sentiment reversal detection",
      },
      {
        name: "PythPriceCapability",
        description: "Price-sentiment correlation",
      },
    ],
    avatarUrl: "/avatars/sentiment-analyzer.png",
  },
  // Governance Group
  {
    id: "proposal-analyzer",
    name: "Proposal Analyzer",
    type: "Governance",
    group: "governance",
    description: "DAO proposal analysis and stakeholder assessment",
    capabilities: [
      {
        name: "WalletDetailsCapability",
        description: "Stakeholder voting analysis",
      },
    ],
    avatarUrl: "/avatars/proposal-analyzer.png",
  },
  {
    id: "vote-calculator",
    name: "Vote Calculator",
    type: "Governance",
    group: "governance",
    description: "Optimizes voting power and strategies",
    capabilities: [
      { name: "BalanceCapability", description: "Voting power calculations" },
    ],
    avatarUrl: "/avatars/vote-calculator.png",
  },
  {
    id: "strategy-coordinator",
    name: "Strategy Coordinator",
    type: "Governance",
    group: "governance",
    description: "Coordinates governance strategy and execution",
    capabilities: [
      {
        name: "BalanceCapability",
        description: "Strategic position assessment",
      },
      { name: "TransferCapability", description: "Strategic move execution" },
    ],
    avatarUrl: "/avatars/strategy-coordinator.png",
  },
  //   {
  //     id: "impact-assessor",
  //     name: "Impact Assessor",
  //     type: "Governance",
  //     group: "governance",
  //     description: "Analyzes proposal impacts on protocol and token",
  //     capabilities: [
  //       { name: "PythPriceCapability", description: "Price impact assessment" },
  //       { name: "BalanceCapability", description: "Balance impact analysis" },
  //     ],
  //     avatarUrl: "/avatars/impact-assessor.png",
  //   },
];

// Example swarms
export const swarms: Swarm[] = [
  {
    id: "finance-squad",
    name: "Finance Squad",
    description: "Complete financial management and advisory team",
    agents: ["personal-accountant", "financial-advisor", "risk-manager"],
    lastActive: new Date().toISOString(),
    created: new Date().toISOString(),
  },
  {
    id: "research-team",
    name: "Research Team",
    description: "Market research and analysis specialists",
    agents: [
      "data-scientist",
      "news-aggregator",
      "pattern-detector",
      "sentiment-analyzer",
    ],
    lastActive: new Date().toISOString(),
    created: new Date().toISOString(),
  },
  {
    id: "governance-council",
    name: "Governance Council",
    description: "DAO governance strategy and analysis team",
    agents: ["proposal-analyzer", "vote-calculator"],
    lastActive: new Date().toISOString(),
    created: new Date().toISOString(),
  },
];

export const getAgent = (id: string): Agent | undefined =>
  agents.find((agent) => agent.id === id);

export const getAgentsByGroup = (groupId: string): Agent[] =>
  agents.filter((agent) => agent.group === groupId);

export const getSwarm = (id: string): Swarm | undefined =>
  swarms.find((swarm) => swarm.id === id);
