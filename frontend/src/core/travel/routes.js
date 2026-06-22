import { applyEffects, appendActionLog } from '@/core/events/effects';
import { spendMoney } from '@/core/economy/wallet';
import { cloneState } from '@/core/player/state';

export function findRoute(routes, fromId, toId) {
  return routes.find((route) => (
    (route.from === fromId && route.to === toId) ||
    (route.from === toId && route.to === fromId)
  ));
}

export function travelTo(playerState, routes, locationId) {
  const route = findRoute(routes, playerState.location_id, locationId);
  let nextState = cloneState(playerState);

  if (route) {
    nextState = applyEffects(nextState, { energy: -route.energy_cost }, 'travel_energy');
    if (route.cost_eur > 0) {
      nextState = spendMoney(nextState, route.cost_eur, `travel:${route.mode}`);
    }
  }

  nextState.location_id = locationId;
  appendActionLog(nextState, {
    action_type: 'travel',
    payload: {
      from: playerState.location_id,
      to: locationId,
      mode: route?.mode || 'unknown',
      minutes: route?.minutes || null,
    },
    effects: route ? {
      energy: -route.energy_cost,
      money: -route.cost_eur,
    } : {},
  });

  return { playerState: nextState, route };
}
