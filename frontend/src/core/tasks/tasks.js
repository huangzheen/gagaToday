import { applyEffects } from '@/core/events/effects';
import { spendMoney } from '@/core/economy/wallet';
import { cloneState } from '@/core/player/state';

export function getActiveTasks(playerState, tasks) {
  return tasks.filter((task) => playerState.active_task_ids.includes(task.id));
}

export function unlockTask(playerState, taskId) {
  const nextState = cloneState(playerState);
  if (!nextState.active_task_ids.includes(taskId) && !nextState.completed_task_ids.includes(taskId)) {
    nextState.active_task_ids.push(taskId);
  }
  return nextState;
}

export function completeTask(playerState, tasks, taskId) {
  const task = tasks.find((item) => item.id === taskId);
  if (!task) return playerState;

  let nextState = cloneState(playerState);

  if (task.cost_eur) {
    nextState = spendMoney(nextState, task.cost_eur, `task:${taskId}`);
  }

  nextState = applyEffects(nextState, task.rewards, `task:${taskId}`);
  nextState.active_task_ids = nextState.active_task_ids.filter((id) => id !== taskId);

  if (!nextState.completed_task_ids.includes(taskId)) {
    nextState.completed_task_ids.push(taskId);
  }

  return nextState;
}
