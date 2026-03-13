import { SIGNAL_BUCKETS } from "../signals/signalBuckets";

export function extractTitleSignals(title: string): string[] {
  const lower = title.toLowerCase();
  const signals: string[] = [];

  Object.entries(SIGNAL_BUCKETS).forEach(([bucket, keywords]) => {
    if (keywords.some((keyword) => lower.includes(keyword))) {
      signals.push(bucket);
    }
  });

  if (lower.includes("senior")) signals.push("senior");
  if (lower.includes("staff")) signals.push("staff");
  if (lower.includes("principal")) signals.push("principal");
  if (lower.includes("lead")) signals.push("lead");

  return signals;
}
