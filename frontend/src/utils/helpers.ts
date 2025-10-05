/**
 * General helper utilities
 */

/**
 * Generate a random ID
 */
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9);
};

/**
 * Debounce function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

/**
 * Sleep utility for async operations
 */
export const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Get segment color by name
 */
export const getSegmentColor = (segmentName: string): string => {
  const colors: Record<string, string> = {
    'Emerging Experts': '#4f46e5',
    'Independent Agents': '#059669',
    'High Performers': '#dc2626',
  };
  return colors[segmentName] || '#ea580c';
};

/**
 * Calculate progress percentage
 */
export const calculateProgress = (completed: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
};


/**
 * Compute average policies sold per segment.
 * Accepts any array of items that at least contain `segment` and `policies_sold` fields.
 * You can optionally restrict to a fixed set of segments; any missing segment results in 0.
 */
export type SegmentAverageMap = Record<string, number>;

export interface AveragePoliciesOptions {
  segments?: string[];
}

export const DEFAULT_SEGMENTS: string[] = [
  'Accomplished Professionals',
  'Emerging Experts',
  'Comfortable Retirees',
  'Independent Agents',
];

export function computeAveragePoliciesBySegment<T extends { segment?: string; policies_sold?: number }>(
  profiles: T[],
  options?: AveragePoliciesOptions
): SegmentAverageMap {
  const targetSegments = options?.segments && options.segments.length > 0 ? options.segments : DEFAULT_SEGMENTS;

  const totals: Record<string, { sum: number; count: number }> = {};
  for (const seg of targetSegments) {
    totals[seg] = { sum: 0, count: 0 };
  }

  for (const item of profiles || []) {
    const segmentName = item.segment;
    if (!segmentName || !(segmentName in totals)) continue;
    const policies = typeof item.policies_sold === 'number' && isFinite(item.policies_sold) ? item.policies_sold : 0;
    totals[segmentName].sum += policies;
    totals[segmentName].count += 1;
  }

  const averages: SegmentAverageMap = {};
  for (const seg of targetSegments) {
    const { sum, count } = totals[seg];
    averages[seg] = count === 0 ? 0 : Number((sum / count).toFixed(2));
  }
  return averages;
}

/**
 * Compute average premium amount per segment.
 */
export function computeAveragePremiumBySegment<T extends { segment?: string; premium_amount?: number }>(
  profiles: T[],
  options?: AveragePoliciesOptions
): SegmentAverageMap {
  const targetSegments = options?.segments && options.segments.length > 0 ? options.segments : DEFAULT_SEGMENTS;

  const totals: Record<string, { sum: number; count: number }> = {};
  for (const seg of targetSegments) {
    totals[seg] = { sum: 0, count: 0 };
  }

  for (const item of profiles || []) {
    const segmentName = item.segment;
    if (!segmentName || !(segmentName in totals)) continue;
    const premium = typeof item.premium_amount === 'number' && isFinite(item.premium_amount) ? item.premium_amount : 0;
    totals[segmentName].sum += premium;
    totals[segmentName].count += 1;
  }

  const averages: SegmentAverageMap = {};
  for (const seg of targetSegments) {
    const { sum, count } = totals[seg];
    averages[seg] = count === 0 ? 0 : Number((sum / count).toFixed(2));
  }
  return averages;
}

/**
 * Compute incremental revenue.
 * Formula: (total average premium across segments / average policies sold across segments) * agentCount * 2
 * Notes:
 * - Uses DEFAULT_SEGMENTS unless overridden via options.
 * - Guards against division by zero.
 */
export function computeIncrementalRevenue<T extends { segment?: string; premium_amount?: number; policies_sold?: number }>(
  profiles: T[],
  options?: AveragePoliciesOptions
): number {
  const segments = options?.segments && options.segments.length > 0 ? options.segments : DEFAULT_SEGMENTS;

  const avgPremiumMap = computeAveragePremiumBySegment(profiles, { segments });
  const avgPoliciesMap = computeAveragePoliciesBySegment(profiles, { segments });

  // total average premium across segments (mean of segment averages)
  const totalAvgPremium = segments.length === 0 ? 0 :
    segments.reduce((sum, seg) => sum + (avgPremiumMap[seg] ?? 0), 0) / segments.length;

  // average policies sold across segments (mean of segment averages)
  const avgPolicies = segments.length === 0 ? 0 :
    segments.reduce((sum, seg) => sum + (avgPoliciesMap[seg] ?? 0), 0) / segments.length;

  if (avgPolicies === 0) return 0;

  const agentCount = Array.isArray(profiles) ? profiles.length : 0;
  const incremental = (totalAvgPremium / avgPolicies) * agentCount * 2;
  return Number(incremental.toFixed(2));
}


