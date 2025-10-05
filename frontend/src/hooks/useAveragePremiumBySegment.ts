import { useMemo } from 'react';
import { computeAveragePremiumBySegment, DEFAULT_SEGMENTS, type SegmentAverageMap } from '../utils';

export interface UseAveragePremiumInput<T extends { segment?: string; premium_amount?: number }> {
  profiles: T[] | null | undefined;
  segments?: string[];
}

export function useAveragePremiumBySegment<T extends { segment?: string; premium_amount?: number }>(
  input: UseAveragePremiumInput<T>
): SegmentAverageMap {
  const { profiles, segments } = input;
  return useMemo(() => {
    return computeAveragePremiumBySegment(profiles ?? [], { segments: segments ?? DEFAULT_SEGMENTS });
  }, [profiles, segments]);
}


