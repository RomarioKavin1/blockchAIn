"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import CyberButton from "@/components/cyberButton";
import LogoComponent from "@/components/logo";

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,#2c1250_0%,#000000_100%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f10_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f10_1px,transparent_1px)] bg-[size:32px_32px]">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f10_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f10_1px,transparent_1px)] bg-[size:16px_16px] opacity-50" />
        </div>
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={i}
            className={`absolute w-1 h-1 ${
              i % 2 === 0 ? "bg-purple-400" : "bg-cyan-400"
            } rounded-full`}
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              opacity: 0.1,
            }}
            animate={{
              y: [null, -window.innerHeight],
              opacity: [0.1, 0.5, 0.1],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
        <svg
          className="absolute inset-0 w-full h-full opacity-10"
          xmlns="http://www.w3.org/2000/svg"
        >
          <pattern
            id="hexagons"
            width="50"
            height="43.4"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M25 0L50 14.4v28.8L25 43.4L0 43.4V14.4z"
              fill="none"
              stroke="rgba(139, 92, 246, 0.5)"
            />
          </pattern>
          <rect width="100%" height="100%" fill="url(#hexagons)" />
        </svg>
        <motion.div
          className="absolute top-1/4 -left-32 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.3, 0.2],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-1/4 -right-32 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.3, 0.2],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 4,
          }}
        />
        <div className="absolute inset-0 bg-[repeating-linear-gradient(0deg,#00000015,#00000015_1px,transparent_1px,transparent_2px)]" />
      </div>
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
      <main className="container mx-auto px-4 pt-36 relative z-10">
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
                className="relative group rounded-xl overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-cyan-600/10 group-hover:from-purple-600/20 group-hover:to-cyan-600/20 transition-colors duration-300" />
                <div className="relative p-6 backdrop-blur-sm border border-purple-500/10 rounded-xl h-[300px] flex flex-col justify-center items-center space-y-4">
                  <div className="text-5xl mb-4">🤖</div>
                  <h3 className="text-xl font-semibold tracking-wide mb-2">
                    Create New Swarm
                  </h3>
                  <p className="text-gray-400 text-center text-sm mb-4">
                    Combine multiple agents to create a powerful AI swarm
                  </p>
                  <CyberButton
                    cyberSize="lg"
                    onClick={() => (window.location.href = "/create-swarm")}
                  >
                    Create Swarm
                  </CyberButton>
                </div>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.02 }}
                className="relative group rounded-xl overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-cyan-600/10 group-hover:from-purple-600/20 group-hover:to-cyan-600/20 transition-colors duration-300" />
                <div className="relative p-6 backdrop-blur-sm border border-purple-500/10 rounded-xl">
                  <div className="flex justify-center items-end h-48 mb-4 relative">
                    {[1, 2, 3].map((_, i) => (
                      <div
                        key={i}
                        className="w-1/3 h-full relative px-1"
                        style={{ transform: `translateX(${i * 5}px)` }}
                      >
                        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
                        <div className="w-full h-full bg-purple-500/20 rounded-lg" />
                      </div>
                    ))}
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold tracking-wide">
                      Finance Squad
                    </h3>
                    <div className="flex justify-between items-center">
                      <div className="text-sm text-gray-400">
                        3 Agents • Last active: 2h ago
                      </div>
                      <CyberButton cyberSize="default">Enter Swarm</CyberButton>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </TabsContent>

          <TabsContent value="explore" className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="relative group rounded-xl overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-cyan-600/10 group-hover:from-purple-600/20 group-hover:to-cyan-600/20 transition-colors duration-300" />
                <div className="relative p-6 backdrop-blur-sm border border-purple-500/10 rounded-xl">
                  <div className="w-full h-48 mb-4 relative rounded-lg overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/50" />
                    <div className="w-full h-full bg-purple-500/20" />
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold tracking-wide mb-1">
                        Personal Accountant
                      </h3>
                      <p className="text-sm text-gray-400">
                        Financial management & analysis
                      </p>
                    </div>

                    <div className="space-y-2">
                      <div className="text-sm font-medium text-gray-300">
                        Capabilities
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <span className="text-xs px-2 py-1 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                          Balance
                        </span>
                        <span className="text-xs px-2 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                          Transfer
                        </span>
                        <span className="text-xs px-2 py-1 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                          NFT Balance
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Dashboard;
