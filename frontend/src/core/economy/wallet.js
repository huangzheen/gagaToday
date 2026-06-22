import { appendActionLog } from '@/core/events/effects';
import { cloneState } from '@/core/player/state';

export function spendMoney(playerState, amountEur, reason) {
  const nextState = cloneState(playerState);
  const amount = Number(amountEur || 0);
  nextState.wallet.cash_eur = Number((nextState.wallet.cash_eur - amount).toFixed(2));
  nextState.transactions.push({
    id: `tx_${String(nextState.transactions.length + 1).padStart(5, '0')}`,
    amount_eur: -amount,
    reason,
    day: nextState.date.day,
    time_block: nextState.time_block,
  });
  appendActionLog(nextState, {
    action_type: 'spend_money',
    payload: { reason, amount_eur: amount },
    effects: { money: -amount },
  });
  return nextState;
}
