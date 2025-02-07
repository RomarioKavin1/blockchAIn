"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { AtSign, Send, Users } from "lucide-react";
import { agents } from "@/config/agents";
import LogoComponent from "@/components/logo";
import CyberButton from "@/components/cyberButton";
import { useRouter } from "next/router";
interface Message {
  id: string;
  content: string;
  senderId: string;
  timestamp: Date;
  targetAgents?: string[];
  isDirectMessage?: boolean;
}

interface SwarmChatPageProps {
  params: {
    id: string;
  };
}

interface MessageBubbleProps {
  message: Message;
}

interface AgentSelectorProps {
  isOpen: boolean;
  selectedAgents: string[];
  onToggle: (agentId: string) => void;
}

const DEFAULT_SWARM_MEMBERS = [
  "personal-accountant",
  "financial-advisor",
  "degen",
  "risk-manager",
];

export default function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [isAgentSelectOpen, setAgentSelectOpen] = useState(false);
  const [slug, setSlug] = useState("");
  useEffect(() => {
    params.then((data) => {
      setSlug(data.slug);
    });
  }, []);
  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      senderId: "user",
      timestamp: new Date(),
      targetAgents: selectedAgents.length > 0 ? selectedAgents : undefined,
      isDirectMessage: selectedAgents.length > 0,
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue("");
    setSelectedAgents([]);
    setAgentSelectOpen(false);

    // Simulate agent responses
    if (selectedAgents.length > 0) {
      selectedAgents.forEach((agentId) => {
        setTimeout(() => {
          const agent = agents.find((a) => a.id === agentId);
          if (agent) {
            const response: Message = {
              id: Date.now().toString(),
              content: `Response from ${agent.name} regarding your question...`,
              senderId: agentId,
              timestamp: new Date(),
              targetAgents: ["user"],
              isDirectMessage: true,
            };
            setMessages((prev) => [...prev, response]);
          }
        }, Math.random() * 2000 + 1000);
      });
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col overflow-hidden">
      <SwarmHeader swarmId={slug} />

      <div className="flex-1 flex">
        <div className="flex flex-1 overflow-hidden">
          <AgentsSidebar swarmMembers={DEFAULT_SWARM_MEMBERS} />

          <main className="flex-1 flex flex-col h-screen pt-20 pb-16">
            <div className="flex-1 overflow-y-auto px-4">
              <ChatMessages messages={messages} />
            </div>
            <ChatInput
              inputValue={inputValue}
              setInputValue={setInputValue}
              selectedAgents={selectedAgents}
              setSelectedAgents={setSelectedAgents}
              isAgentSelectOpen={isAgentSelectOpen}
              setAgentSelectOpen={setAgentSelectOpen}
              onSendMessage={handleSendMessage}
              swarmMembers={DEFAULT_SWARM_MEMBERS}
            />
          </main>

          <SwarmInfoSidebar swarmId={slug} />
        </div>
      </div>
    </div>
  );
}

const SwarmHeader: React.FC<{ swarmId: string }> = ({ swarmId }) => (
  <header className="fixed top-0 w-full z-50 border-b border-purple-500/20 bg-black/30 backdrop-blur-sm">
    <div className="container mx-auto px-4 h-16 flex justify-between items-center">
      <div className="flex items-center gap-4">
        <div className="scale-50 origin-left">
          <LogoComponent />
        </div>
        <div className="h-8 w-px bg-purple-500/20" />
      </div>
      <CyberButton cyberSize="default" variant="outline">
        Connect Wallet
      </CyberButton>
    </div>
  </header>
);

const AgentsSidebar: React.FC<{ swarmMembers: string[] }> = ({
  swarmMembers,
}) => (
  <aside className="w-64 border-r border-purple-500/20 bg-black/30 backdrop-blur-sm hidden lg:block pt-20">
    <div className="p-4">
      <h2 className="text-sm font-semibold text-gray-400 mb-4">Swarm Agents</h2>
      <div className="space-y-2">
        {swarmMembers.map((memberId) => {
          const agent = agents.find((a) => a.id === memberId);
          if (!agent) return null;
          return (
            <div
              key={agent.id}
              className="flex items-center gap-3 p-2 rounded-lg hover:bg-purple-500/10 transition-colors"
            >
              <div className="relative w-10 h-10 rounded-full overflow-hidden">
                <Image
                  src={agent.avatarUrl}
                  alt={agent.name}
                  fill
                  className="object-contain"
                />
              </div>
              <div>
                <div className="text-sm font-medium">{agent.name}</div>
                <div className="text-xs text-gray-400">{agent.type}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  </aside>
);

const SwarmInfoSidebar: React.FC<{ swarmId: string }> = ({ swarmId }) => (
  <aside className="w-80 border-l border-purple-500/20 bg-black/30 backdrop-blur-sm hidden xl:block pt-20">
    <div className="p-4">
      <h2 className="text-sm font-semibold text-gray-400 mb-4">
        Swarm Details
      </h2>
      {/* Add swarm details here */}
    </div>
  </aside>
);

const ChatMessages: React.FC<{ messages: Message[] }> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="space-y-2 py-4">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const sender =
    message.senderId === "user"
      ? { name: "You", avatarUrl: "/avatars/user.png" }
      : agents.find((a) => a.id === message.senderId);

  if (!sender) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex ${
        message.senderId === "user" ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`flex ${
          message.senderId === "user" ? "flex-row-reverse" : "flex-row"
        } items-start gap-2 max-w-2xl`}
      >
        <div className="relative w-24 h-24 rounded-full overflow-hidden flex-shrink-0">
          <Image
            src={sender.avatarUrl}
            alt={sender.name}
            width={500}
            height={500}
          />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-medium text-gray-400">
              {sender.name}
            </span>
            {message.isDirectMessage && (
              <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full">
                DM
              </span>
            )}
          </div>
          <div
            className={`rounded-lg p-3 ${
              message.senderId === "user"
                ? "bg-purple-500/20 text-purple-100"
                : "bg-cyan-500/20 text-cyan-100"
            }`}
          >
            {message.content}
          </div>
          {message.targetAgents && (
            <div className="mt-1 flex items-center gap-1 text-xs text-gray-400">
              <AtSign className="w-3 h-3" />
              {message.targetAgents.map((targetId) => {
                const target =
                  targetId === "user"
                    ? { name: "You" }
                    : agents.find((a) => a.id === targetId);
                return (
                  target?.name && <span key={targetId}>{target.name}</span>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

interface ChatInputProps {
  inputValue: string;
  setInputValue: (value: string) => void;
  selectedAgents: string[];
  setSelectedAgents: (agents: string[]) => void;
  isAgentSelectOpen: boolean;
  setAgentSelectOpen: (open: boolean) => void;
  onSendMessage: () => void;
  swarmMembers: string[];
}

const ChatInput: React.FC<ChatInputProps> = ({
  inputValue,
  setInputValue,
  selectedAgents,
  setSelectedAgents,
  isAgentSelectOpen,
  setAgentSelectOpen,
  onSendMessage,
  swarmMembers,
}) => {
  const toggleAgentSelection = (agentId: string) => {
    setSelectedAgents(
      selectedAgents.includes(agentId)
        ? selectedAgents.filter((id) => id !== agentId)
        : [...selectedAgents, agentId]
    );
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-black/80 border-t border-purple-500/20 backdrop-blur-sm">
      <div className="container mx-auto px-4 py-3">
        <div className="relative max-w-5xl mx-auto">
          <AgentSelector
            isOpen={isAgentSelectOpen}
            selectedAgents={selectedAgents}
            onToggle={toggleAgentSelection}
            swarmMembers={swarmMembers}
          />

          <div className="flex gap-2">
            <button
              onClick={() => setAgentSelectOpen(!isAgentSelectOpen)}
              className={`p-2 rounded-lg ${
                isAgentSelectOpen || selectedAgents.length > 0
                  ? "bg-cyan-500/20 text-cyan-300"
                  : "bg-purple-500/20 text-purple-300"
              }`}
            >
              <Users className="w-5 h-5" />
            </button>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && onSendMessage()}
              placeholder={
                selectedAgents.length > 0
                  ? `Message ${selectedAgents.length} selected agents...`
                  : "Message your swarm..."
              }
              className="flex-1 bg-purple-500/10 border border-purple-500/20 rounded-lg px-4 py-2
                text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
            />
            <CyberButton
              onClick={onSendMessage}
              cyberSize="default"
              className="px-4"
            >
              <Send className="w-5 h-5" />
            </CyberButton>
          </div>
        </div>
      </div>
    </div>
  );
};

interface AgentSelectorProps {
  isOpen: boolean;
  selectedAgents: string[];
  onToggle: (agentId: string) => void;
  swarmMembers: string[];
}

const AgentSelector: React.FC<AgentSelectorProps> = ({
  isOpen,
  selectedAgents,
  onToggle,
  swarmMembers,
}) => (
  <AnimatePresence>
    {isOpen && (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        className="absolute bottom-full mb-2 w-full bg-black/90 rounded-lg border border-purple-500/20 p-3"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {swarmMembers.map((memberId) => {
            const agent = agents.find((a) => a.id === memberId);
            if (!agent) return null;
            const isSelected = selectedAgents.includes(agent.id);

            return (
              <button
                key={agent.id}
                onClick={() => onToggle(agent.id)}
                className={`p-2 rounded-lg border ${
                  isSelected
                    ? "border-cyan-500 bg-cyan-500/20"
                    : "border-purple-500/20 bg-purple-500/10 hover:bg-purple-500/20"
                } transition-colors`}
              >
                <div className="flex items-center gap-2">
                  <div className="relative w-8 h-8">
                    <Image
                      src={agent.avatarUrl}
                      alt={agent.name}
                      fill
                      className="object-contain"
                    />
                  </div>
                  <span className="text-sm">{agent.name}</span>
                </div>
              </button>
            );
          })}
        </div>
      </motion.div>
    )}
  </AnimatePresence>
);
