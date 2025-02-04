// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract AISwarmManager is Ownable, ReentrancyGuard {
    // Enums
    constructor() Ownable(msg.sender) {} 
    
    enum SwarmStatus { Inactive, Active, Paused }

    // Structs
    struct Agent {
        uint256 agentId;      // ID that maps to your off-chain agent
        bool isActive;
        uint256 lastInteraction;
    }

    struct Swarm {
        string threadId;      // Unique thread ID for the swarm
        mapping(uint256 => Agent) agents;  // agentId => Agent
        uint256[] agentIds;   // Array to keep track of agent IDs in swarm
        uint256 createdAt;
        SwarmStatus status;
        address owner;
    }

    // State Variables
    mapping(uint256 => Swarm) public swarms;        // swarmId => Swarm
    mapping(address => uint256[]) public userSwarms; // user address => array of swarm IDs
    uint256 private nextSwarmId = 1;

    // Events
    event SwarmCreated(uint256 indexed swarmId, address indexed owner, string threadId);
    event AgentAdded(uint256 indexed swarmId, uint256 indexed agentId);
    event AgentRemoved(uint256 indexed swarmId, uint256 indexed agentId);
    event SwarmStatusUpdated(uint256 indexed swarmId, SwarmStatus status);

    // Modifiers
    modifier onlySwarmOwner(uint256 swarmId) {
        require(swarms[swarmId].owner == msg.sender, "Not swarm owner");
        _;
    }

    modifier swarmExists(uint256 swarmId) {
        require(swarms[swarmId].owner != address(0), "Swarm does not exist");
        _;
    }

    // Core Functions
    function createSwarm(string memory threadId, uint256[] memory initialAgentIds) 
        external 
        nonReentrant 
        returns (uint256)
    {
        uint256 swarmId = nextSwarmId++;
        
        Swarm storage newSwarm = swarms[swarmId];
        newSwarm.threadId = threadId;
        newSwarm.createdAt = block.timestamp;
        newSwarm.status = SwarmStatus.Active;
        newSwarm.owner = msg.sender;

        // Add initial agents
        for (uint256 i = 0; i < initialAgentIds.length; i++) {
            _addAgentToSwarm(swarmId, initialAgentIds[i]);
        }

        userSwarms[msg.sender].push(swarmId);
        
        emit SwarmCreated(swarmId, msg.sender, threadId);
        return swarmId;
    }

    function addAgentToSwarm(uint256 swarmId, uint256 agentId) 
        external 
        swarmExists(swarmId)
        onlySwarmOwner(swarmId) 
    {
        _addAgentToSwarm(swarmId, agentId);
    }

    function removeAgentFromSwarm(uint256 swarmId, uint256 agentId)
        external
        swarmExists(swarmId)
        onlySwarmOwner(swarmId)
    {
        require(swarms[swarmId].agents[agentId].agentId == agentId, "Agent not in swarm");
        
        delete swarms[swarmId].agents[agentId];
        
        // Remove from agentIds array
        uint256[] storage agentIds = swarms[swarmId].agentIds;
        for (uint256 i = 0; i < agentIds.length; i++) {
            if (agentIds[i] == agentId) {
                agentIds[i] = agentIds[agentIds.length - 1];
                agentIds.pop();
                break;
            }
        }
        
        emit AgentRemoved(swarmId, agentId);
    }

    function updateSwarmStatus(uint256 swarmId, SwarmStatus newStatus)
        external
        swarmExists(swarmId)
        onlySwarmOwner(swarmId)
    {
        swarms[swarmId].status = newStatus;
        emit SwarmStatusUpdated(swarmId, newStatus);
    }

    // View Functions
    function getSwarmAgents(uint256 swarmId) 
        external 
        view 
        swarmExists(swarmId)
        returns (uint256[] memory)
    {
        return swarms[swarmId].agentIds;
    }

    function getUserSwarms(address user) 
        external 
        view 
        returns (uint256[] memory)
    {
        return userSwarms[user];
    }

    function getSwarmDetails(uint256 swarmId)
        external
        view
        swarmExists(swarmId)
        returns (
            string memory threadId,
            uint256 agentCount,
            uint256 createdAt,
            SwarmStatus status,
            address owner
        )
    {
        Swarm storage swarm = swarms[swarmId];
        return (
            swarm.threadId,
            swarm.agentIds.length,
            swarm.createdAt,
            swarm.status,
            swarm.owner
        );
    }

    // Internal Functions
    function _addAgentToSwarm(uint256 swarmId, uint256 agentId) internal {
        require(swarms[swarmId].agents[agentId].agentId == 0, "Agent already in swarm");
        
        swarms[swarmId].agents[agentId] = Agent({
            agentId: agentId,
            isActive: true,
            lastInteraction: block.timestamp
        });
        
        swarms[swarmId].agentIds.push(agentId);
        
        emit AgentAdded(swarmId, agentId);
    }
}