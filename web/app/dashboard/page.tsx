"use client";

import React, { useEffect } from "react";
import { motion } from "framer-motion";
import { useAccount, useReadContracts } from "wagmi";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import LogoComponent from "@/components/logo";
import OptimizedBackground from "@/components/background";
import AgentCard from "@/components/agent-card";
import SwarmCard from "@/components/swarm-card";
import { agents } from "@/config/agents";
import CreateSwarmCard from "@/components/createSwarm";
import { DynamicWidget } from "@dynamic-labs/sdk-react-core";
import { Swarm } from "@/types/agents";
import { swarm_abi, swarm_contract } from "@/lib/deployments";
import { Abi } from "viem";

const CONTRACT_ADDRESS = swarm_contract;
const CONTRACT_ABI = swarm_abi as Abi;

const Dashboard = () => {
  const { address, isConnected } = useAccount();

  const {
    data: swarmIdsResult,
    isPending: isLoadingSwarmIds,
    error: swarmIdsError,
  } = useReadContracts({
    contracts: [
      {
        address: CONTRACT_ADDRESS as `0x${string}`,
        abi: CONTRACT_ABI,
        functionName: "getUserSwarms",
        args: [address as `0x${string}`],
      },
    ],
    query: {
      enabled: !!address && isConnected,
    },
  });

  // Debug logs
  useEffect(() => {
    console.log("Address:", address);
    console.log("Is Connected:", isConnected);
    console.log("Swarm IDs Result:", swarmIdsResult);
    console.log("Swarm IDs Error:", swarmIdsError);
  }, [address, isConnected, swarmIdsResult, swarmIdsError]);

  const swarmIds = swarmIdsResult?.[0]?.result as readonly bigint[] | undefined;

  const swarmDetailsContracts =
    swarmIds
      ?.map((swarmId) => [
        {
          address: CONTRACT_ADDRESS as `0x${string}`,
          abi: CONTRACT_ABI,
          functionName: "getSwarmDetails",
          args: [swarmId],
        },
        {
          address: CONTRACT_ADDRESS as `0x${string}`,
          abi: CONTRACT_ABI,
          functionName: "getSwarmAgents",
          args: [swarmId],
        },
      ])
      .flat() || [];

  const {
    data: swarmDetailsResult,
    isPending: isLoadingDetails,
    error: swarmDetailsError,
  } = useReadContracts({
    contracts: swarmDetailsContracts,
    query: {
      enabled: !!swarmIds?.length,
    },
  });

  // More debug logs
  useEffect(() => {
    console.log("Swarm Details Result:", swarmDetailsResult);
    console.log("Swarm Details Error:", swarmDetailsError);
  }, [swarmDetailsResult, swarmDetailsError]);

  const userSwarms: Swarm[] = [];

  if (swarmIds && swarmDetailsResult) {
    for (let i = 0; i < swarmIds.length; i++) {
      const detailsResult = swarmDetailsResult[i * 2]?.result as
        | [string, bigint, bigint, number, string]
        | undefined;
      const agentsResult = swarmDetailsResult[i * 2 + 1]?.result as
        | readonly bigint[]
        | undefined;

      if (!detailsResult || !agentsResult) continue;

      const [threadId, agentCount, createdAt] = detailsResult;
      const swarmId = swarmIds[i];

      const swarmAgents = agentsResult
        .map((id) => {
          const agent = agents.find((a) => a.num === Number(id));
          return agent ? agent.id : null;
        })
        .filter(Boolean);

      const createdDate = new Date(Number(createdAt) * 1000);

      userSwarms.push({
        id: swarmId.toString(),
        name: `Swarm ${swarmId}`,
        description: `A dynamic swarm of ${agentCount} specialized agents`,
        agents: swarmAgents as string[],
        lastActive: createdDate.toISOString(),
        created: createdDate.toISOString(),
        threadId,
      });
    }
  }

  const handleCreateSwarm = () => {
    window.location.href = "/createswarm";
  };

  const handleEnterSwarm = (swarmId: string) => {
    window.location.href = `/swarm/${swarmId}`;
  };

  // Show error state if any errors occur
  if (swarmIdsError || swarmDetailsError) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">Error loading swarms</p>
          <p className="text-sm text-gray-400">
            {(swarmIdsError || swarmDetailsError)?.message}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      <OptimizedBackground />

      <header className="border-b border-purple-500/20 bg-black/30 backdrop-blur-sm backdrop-opacity-20 fixed top-0 w-full z-50">
        <div className="container mx-auto px-4 flex justify-between items-center h-16">
          <div className="scale-50 origin-left">
            <LogoComponent />
          </div>
          <DynamicWidget />
        </div>
      </header>

      <main className="container w-4/5 mx-auto px-4 pt-36 relative z-10">
        <Tabs defaultValue="swarms" className="w-full">
          <TabsList className="w-full mb-8 p-1 bg-gradient-to-r from-purple-500/10 via-cyan-500/10 to-purple-500/10 rounded-lg backdrop-blur-sm">
            <TabsTrigger
              value="swarms"
              className="w-full text-base font-medium tracking-wide
                data-[state=active]:bg-gradient-to-r 
                data-[state=active]:from-purple-500/80 
                data-[state=active]:to-cyan-500/80
                data-[state=active]:text-white
                data-[state=inactive]:text-gray-400
                transition-all duration-300"
            >
              Your Swarms
            </TabsTrigger>
            <TabsTrigger
              value="explore"
              className="w-full text-base font-medium tracking-wide
                data-[state=active]:bg-gradient-to-r 
                data-[state=active]:from-purple-500/80 
                data-[state=active]:to-cyan-500/80
                data-[state=active]:text-white
                data-[state=inactive]:text-gray-400
                transition-all duration-300"
            >
              Explore Agents
            </TabsTrigger>
          </TabsList>

          <TabsContent value="swarms" className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="relative group rounded-xl overflow-hidden cursor-pointer"
                onClick={handleCreateSwarm}
              >
                <CreateSwarmCard onClick={handleCreateSwarm} />
              </motion.div>

              {!isConnected ? (
                <div className="col-span-full text-center text-gray-400">
                  Connect your wallet to view your swarms
                </div>
              ) : isLoadingSwarmIds ? (
                <div className="col-span-full flex justify-center items-center min-h-[200px]">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500"></div>
                </div>
              ) : !swarmIds || swarmIds.length === 0 ? (
                <div className="col-span-full text-center text-gray-400">
                  Create a swarm to get started!
                </div>
              ) : isLoadingDetails ? (
                <div className="col-span-full flex justify-center items-center min-h-[200px]">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500"></div>
                </div>
              ) : userSwarms.length > 0 ? (
                userSwarms.map((swarm) => (
                  <SwarmCard
                    key={swarm.id}
                    swarm={swarm}
                    onClick={() => handleEnterSwarm(swarm.id)}
                  />
                ))
              ) : null}
            </div>
          </TabsContent>

          <TabsContent value="explore" className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onClick={(selectedAgent) => {
                    console.log("Selected agent:", selectedAgent);
                  }}
                />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Dashboard;
