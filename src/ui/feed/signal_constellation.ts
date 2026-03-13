export type ConstellationGroup =
  | "ai_ml"
  | "engineering"
  | "data"
  | "product"
  | "security";

export const CONSTELLATION_GROUP_SIGNALS: Record<ConstellationGroup, string[]> = {
  ai_ml: ["ai", "machine_learning", "ml", "genai", "llm"],
  engineering: ["backend", "frontend", "platform"],
  data: ["data"],
  product: ["product"],
  security: ["security"],
};

type Job = {
  id: string;
  signals?: string[];
};

export function buildSignalConstellation(jobs: Job[]): Record<ConstellationGroup, Job[]> {
  const grouped: Record<ConstellationGroup, Job[]> = {
    ai_ml: [],
    engineering: [],
    data: [],
    product: [],
    security: [],
  };

  const seenByGroup: Record<ConstellationGroup, Set<string>> = {
    ai_ml: new Set<string>(),
    engineering: new Set<string>(),
    data: new Set<string>(),
    product: new Set<string>(),
    security: new Set<string>(),
  };

  for (const job of jobs) {
    const normalizedSignals = new Set((job.signals ?? []).map((signal) => signal.toLowerCase()));

    (Object.keys(CONSTELLATION_GROUP_SIGNALS) as ConstellationGroup[]).forEach((group) => {
      const groupSignals = CONSTELLATION_GROUP_SIGNALS[group];
      const matchesGroup = groupSignals.some((signal) => normalizedSignals.has(signal));
      if (!matchesGroup) return;

      const jobKey = job.id;
      if (seenByGroup[group].has(jobKey)) return;

      seenByGroup[group].add(jobKey);
      grouped[group].push(job);
    });
  }

  return grouped;
}
