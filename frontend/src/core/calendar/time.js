import { cloneState } from '@/core/player/state';

export const TIME_BLOCKS = [
  'morning',
  'commute',
  'school_morning',
  'lunch',
  'school_afternoon',
  'after_school',
  'evening',
  'night',
];

export function advanceTimeBlock(playerState) {
  const nextState = cloneState(playerState);
  const currentIndex = TIME_BLOCKS.indexOf(nextState.time_block);
  const nextIndex = currentIndex + 1;

  if (nextIndex >= TIME_BLOCKS.length) {
    nextState.time_block = TIME_BLOCKS[0];
    nextState.date.day += 1;
  } else {
    nextState.time_block = TIME_BLOCKS[nextIndex];
  }

  return nextState;
}
