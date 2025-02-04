import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const AISwarmManagerModule = buildModule("AISwarmManagerModule", (m) => {
  const aiswarmManager = m.contract("AISwarmManager", []);

  return { aiswarmManager };
});

export default AISwarmManagerModule;
