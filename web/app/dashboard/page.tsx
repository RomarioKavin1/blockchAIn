"use client";

import React from "react";
import { motion } from "framer-motion";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import CyberButton from "@/components/cyberButton";
import LogoComponent from "@/components/logo";
import OptimizedBackground from "@/components/background";
import AgentCard from "@/components/agent-card";
import SwarmCard from "@/components/swarm-card";
import { agents, swarms } from "@/config/agents";
import CreateSwarmCard from "@/components/createSwarm";

const Dashboard = () => {
  const handleCreateSwarm = () => {
    window.location.href = "/create-swarm";
  };

  const handleEnterSwarm = (swarmId: string) => {
    window.location.href = `/swarm/${swarmId}`;
  };

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      <OptimizedBackground />

      {/* Header */}
      <header className="border-b border-purple-500/20 bg-black/30 backdrop-blur-sm backdrop-opacity-20 fixed top-0 w-full z-50">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <div className="scale-50 origin-left">
            <LogoComponent />
          </div>
          <CyberButton cyberSize="default" variant="outline" className="mr-2">
            Connect Wallet
          </CyberButton>
        </div>
      </header>

      {/* Main Content */}
      <main className=" container  w-4/5  mx-auto px-4 pt-36 relative z-10">
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

          {/* Swarms Tab */}
          <TabsContent value="swarms" className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Create New Swarm Card */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="relative group rounded-xl overflow-hidden cursor-pointer"
                onClick={handleCreateSwarm}
              >
                <CreateSwarmCard onClick={handleCreateSwarm} />
              </motion.div>

              {/* Existing Swarms */}
              {swarms.map((swarm) => (
                <SwarmCard
                  key={swarm.id}
                  swarm={swarm}
                  onClick={() => handleEnterSwarm(swarm.id)}
                />
              ))}
            </div>
          </TabsContent>

          {/* Explore Tab */}
          <TabsContent value="explore" className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.id}
                  agent={agent}
                  onClick={(selectedAgent) => {
                    console.log("Selected agent:", selectedAgent);
                    // Handle agent selection
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
