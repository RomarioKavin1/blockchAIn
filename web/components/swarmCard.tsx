"use client";

import React from "react";
import { motion } from "framer-motion";
import CyberButton from "./cyberButton";

interface SwarmCardProps {
  name: string;
  agents: string[];
  lastActive?: string;
}

const SwarmCard: React.FC<SwarmCardProps> = ({ name, agents, lastActive }) => {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="relative group rounded-xl overflow-hidden"
    >
      {/* Background with gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-cyan-600/20 group-hover:from-purple-600/30 group-hover:to-cyan-600/30 transition-colors duration-300" />

      {/* Content */}
      <div className="relative p-6 backdrop-blur-sm border border-purple-500/20 rounded-xl">
        {/* Swarm visualization */}
        <div className="w-full h-48 mb-4 relative">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/50" />
          <div className="relative w-full h-full flex justify-center items-end gap-2">
            {agents.map((agent, index) => (
              <motion.div
                key={agent}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
                className="relative h-full flex-1"
              >
                <img
                  src={`/agents/${agent
                    .toLowerCase()
                    .replace(/\s+/g, "-")}.png`}
                  alt={agent}
                  className="w-full h-full object-contain"
                />
              </motion.div>
            ))}
          </div>
        </div>

        {/* Swarm info */}
        <div className="space-y-4">
          <h3 className="text-xl font-pixel">{name}</h3>

          <div className="flex justify-between items-center">
            {/* <div className="text-sm text-gray-400">
              {agents.length} Agents • Last active: {lastActive || "Never"}
            </div> */}
            <CyberButton
              cyberSize="default"
              onClick={() => (window.location.href = `/swarm/${name}`)}
            >
              Enter Swarm
            </CyberButton>
          </div>
        </div>

        {/* Hover effect scanlines */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      </div>
    </motion.div>
  );
};

export default SwarmCard;
