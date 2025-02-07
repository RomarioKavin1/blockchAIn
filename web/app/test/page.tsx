"use client";
import { swarm_abi, swarm_contract } from "@/lib/deployments";
import { useWriteContract, useWaitForTransactionReceipt } from "wagmi";

export default function CreateSwarm() {
  const { data: hash, error, isPending, writeContract } = useWriteContract();

  // Create the swarm with the provided threadId and initialAgentIds
  const createSwarm = async (threadId: string, initialAgentIds: number[]) => {
    try {
      const tx = await writeContract({
        abi: swarm_abi,
        address: swarm_contract,
        functionName: "createSwarm",
        args: [threadId, initialAgentIds],
      });
      console.log("Swarm created successfully:");
      return tx; // Return the transaction hash
    } catch (err) {
      console.error("Error creating swarm:", err);
      throw err;
    }
  };

  // Handle form submission and call createSwarm
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    const threadId = formData.get("threadId") as string;
    const initialAgentIds = JSON.parse(formData.get("agentIds") as string); // Parsing agent IDs as an array of numbers
    await createSwarm(threadId, initialAgentIds);
  };
  const { isLoading: isConfirming, isSuccess: isConfirmed } =
    useWaitForTransactionReceipt({
      hash,
    });

  return (
    <form onSubmit={submit}>
      <input name="threadId" placeholder="Thread ID" required />
      <input
        name="agentIds"
        placeholder="Initial Agent IDs (e.g. [1, 2, 3])"
        required
      />
      <button disabled={isPending} type="submit">
        {isPending ? "Creating Swarm..." : "Create Swarm"}
      </button>

      {/* Show the transaction hash */}
      {hash && <div>Transaction Hash: {hash}</div>}

      {/* Show confirmation status */}
      {isConfirming && <div>Waiting for confirmation...</div>}
      {isConfirmed && <div>Swarm created and transaction confirmed!</div>}

      {/* Show error if something went wrong */}
      {error && <div>Error: {error.message}</div>}
    </form>
  );
}
