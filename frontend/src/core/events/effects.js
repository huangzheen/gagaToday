import { clamp, cloneState } from '@/core/player/state';

export function applyEffects(playerState, effects = {}, reason = 'effect') {
  const nextState = cloneState(playerState);

  if (typeof effects.energy === 'number') {
    nextState.status.energy = clamp(nextState.status.energy + effects.energy);
  }

  if (typeof effects.mood === 'number') {
    nextState.status.mood = clamp(nextState.status.mood + effects.mood);
  }

  if (typeof effects.stress === 'number') {
    nextState.status.stress = clamp(nextState.status.stress + effects.stress);
  }

  if (typeof effects.health === 'number') {
    nextState.status.health = clamp(nextState.status.health + effects.health);
  }

  if (typeof effects.parent_trust === 'number') {
    nextState.parent_trust.score = clamp(nextState.parent_trust.score + effects.parent_trust);
  }

  if (typeof effects.german_xp === 'number') {
    nextState.skills.german.xp += effects.german_xp;
  }

  if (typeof effects.english_xp === 'number') {
    nextState.skills.english.xp += effects.english_xp;
  }

  if (typeof effects.math_xp === 'number') {
    nextState.skills.math.xp += effects.math_xp;
  }

  if (typeof effects.life_xp === 'number') {
    nextState.skills.life.xp += effects.life_xp;
  }

  appendActionLog(nextState, {
    action_type: 'apply_effects',
    payload: { reason },
    effects,
  });

  return nextState;
}

export function appendActionLog(playerState, entry) {
  const index = playerState.action_log.length + 1;
  playerState.action_log.push({
    id: `log_${String(index).padStart(6, '0')}`,
    day: playerState.date.day,
    time_block: playerState.time_block,
    ...entry,
    created_at: new Date().toISOString(),
  });
}
