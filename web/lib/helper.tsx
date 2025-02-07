import { useWriteContract } from "wagmi";
import { swarm_abi, swarm_contract } from "./deployments";

// Hardcoded ABI and contract address
export function useCreateSwarm() {
  const { data: hash, writeContract } = useWriteContract();

  const createSwarm = async (threadId: string, initialAgentIds: number[]) => {
    try {
      const tx = await writeContract({
        abi: swarm_abi,
        address: swarm_contract,
        functionName: "createSwarm",
        args: [threadId, initialAgentIds],
      });
      console.log("Swarm created successfully:", hash);
      return hash;
    } catch (error) {
      console.error("Error creating swarm:", error);
      throw error;
    }
  };

  return { createSwarm };
}
