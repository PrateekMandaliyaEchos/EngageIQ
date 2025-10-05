import { useMemo } from 'react';
import { computeAveragePoliciesBySegment, DEFAULT_SEGMENTS, type SegmentAverageMap } from '../utils';

export interface UseAveragePoliciesInput<T extends { segment?: string; policies_sold?: number }> {
  profiles: T[] | null | undefined;
  segments?: string[];
}

export function useAveragePoliciesBySegment<T extends { segment?: string; policies_sold?: number }>(
  input: UseAveragePoliciesInput<T>
): SegmentAverageMap {
  const { profiles, segments } = input;
  return useMemo(() => {
    return computeAveragePoliciesBySegment(profiles ?? [], { segments: segments ?? DEFAULT_SEGMENTS });
  }, [profiles, segments]);
}


