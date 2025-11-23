import { EventRecord, RoadChainBlock } from "../types/api";

const BASE_HEIGHT = 1000;

function buildMockBlocks(): RoadChainBlock[] {
  const now = Date.now();
  return Array.from({ length: 5 }).map((_, idx) => {
    const height = BASE_HEIGHT + idx;
    const timestamp = new Date(now - idx * 60000).toISOString();
    return {
      height,
      hash: `mock-hash-${height}`,
      prevHash: `mock-hash-${height - 1}`,
      timestamp,
      eventIds: [`evt-${height}-1`, `evt-${height}-2`],
    };
  });
}

function buildMockEvents(blockHeight: number): EventRecord[] {
  const block = blockHeight || BASE_HEIGHT;
  const timestamp = new Date().toISOString();
  return [
    {
      id: `evt-${block}-1`,
      timestamp,
      source: "operator",
      type: "job.completed",
      summary: `Job completed in block ${block}`,
      psShaInfinity: "ps-sha-∞-example",
      severity: "info",
    },
    {
      id: `evt-${block}-2`,
      timestamp,
      source: "core",
      type: "ledger.append",
      summary: `Ledger entry added for block ${block}`,
      severity: "warning",
    },
  ];
}

export async function fetchRoadChainBlocks(): Promise<RoadChainBlock[]> {
  // TODO: Replace with real RoadChain backend call when available.
  return buildMockBlocks();
}

export async function fetchBlockEvents(blockHeight: number): Promise<EventRecord[]> {
  // TODO: Replace with real RoadChain backend call when available.
  return buildMockEvents(blockHeight);
}
