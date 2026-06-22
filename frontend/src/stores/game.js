import { defineStore } from 'pinia';
import { computed, ref, watch } from 'vue';
import locations from '@/content/munich/locations.json';
import dialogues from '@/content/munich/dialogues.json';
import routes from '@/content/munich/routes.json';
import tasks from '@/content/munich/tasks.json';
import playerStart from '@/content/munich/player_start.json';
import dailyEvents from '@/content/munich/daily_events.json';
import {
  applyEffects,
  completeTask,
  createPlayerState,
  getActiveTasks,
  loadPlayerState,
  savePlayerState,
  toStatusBarStats,
  travelTo,
  unlockTask,
} from '@/core';
import { advanceTimeBlock, TIME_BLOCKS } from '@/core/calendar/time';

const TIME_BLOCK_LABEL = {
  morning: '早晨 · Zuhause',
  commute: '通勤 · Unterwegs',
  school_morning: '上午课 · Schule',
  lunch: '午餐 · Mittagspause',
  school_afternoon: '下午课 · Schule',
  after_school: '放学后 · Freizeit',
  evening: '傍晚 · Zuhause',
  night: '夜晚 · Schlafen',
};

/**
 * 主游戏状态 store
 * 管理:主角属性 / 当前位置 / 当前 NPC / 对话状态 / 时间推进 / 每日事件
 */
export const useGameStore = defineStore('game', () => {
  const playerState = ref(loadPlayerState() || createPlayerState(playerStart));
  const stats = computed(() => toStatusBarStats(playerState.value));
  const activeTasks = computed(() => getActiveTasks(playerState.value, tasks));

  // ===== 时间状态 =====
  const currentTimeBlock = computed(() => playerState.value.time_block);
  const currentTimeLabel = computed(() => TIME_BLOCK_LABEL[playerState.value.time_block] || playerState.value.time_block);
  const nextTimeBlock = computed(() => {
    const idx = TIME_BLOCKS.indexOf(playerState.value.time_block);
    return idx >= 0 && idx < TIME_BLOCKS.length - 1 ? TIME_BLOCKS[idx + 1] : null;
  });

  // ===== 场景状态 =====
  const currentScene = ref('city');   // 'city' | 'host_home' | 'school' | ...
  const currentNpc = ref(null);

  // ===== 对话状态 =====
  const dialogueState = ref({
    open: false,
    turnIndex: 0,
    useEnglish: false,
  });

  // ===== 每日事件弹窗 =====
  const currentEvent = ref(null);

  // ===== 日结算弹窗 =====
  const daySummary = ref(null);

  // ===== 内容数据 =====
  const scenePoints = ref(locations);
  const routePresets = ref(routes);
  const taskCatalog = ref(tasks);
  const dialogueScripts = ref(dialogues);
  const eventCatalog = ref(dailyEvents);

  // ===== Actions =====

  /**
   * 推进时间块到下一个时段,触发该时段 + 当前位置的 daily_event
   */
  function advanceTime() {
    const nextState = advanceTimeBlock(playerState.value);
    playerState.value = nextState;
    triggerDailyEvent();
  }

  /**
   * 检查当前位置 + 当前 time_block + 当前 day 是否匹配一个 daily_event
   * 匹配则:set_flags + unlock_task + 显示弹窗
   */
  function triggerDailyEvent() {
    const ps = playerState.value;
    const event = eventCatalog.value.find((e) => (
      e.day === ps.date.day &&
      e.time_block === ps.time_block &&
      e.location_id === ps.location_id
    ));
    if (!event) return null;

    // 1. set flags
    if (event.sets_flags?.length) {
      const flags = { ...ps.flags };
      event.sets_flags.forEach((flag) => { flags[flag] = true; });
      playerState.value = { ...ps, flags };
    }

    // 2. unlock tasks
    (event.actions || []).forEach((action) => {
      if (action.type === 'unlock_task' && action.task_id) {
        playerState.value = unlockTask(playerState.value, action.task_id);
      }
    });

    // 3. 显示弹窗(如果有标题)
    if (event.title_zh) {
      currentEvent.value = event;
    }

    return event;
  }

  function dismissEvent() {
    currentEvent.value = null;
  }

  /**
   * 进入 POI(从 Phaser CityScene 点击场景点触发)
   * 行为:travel 路线结算 + 切换 currentScene + 自动开 DialogueBox
   * 末尾:触发 daily_event(可能弹窗 + 解锁任务)
   */
  function enterScene(sceneId) {
    const result = travelTo(playerState.value, routePresets.value, sceneId);
    playerState.value = result.playerState;
    currentScene.value = sceneId;
    currentNpc.value = dialogueScripts.value[sceneId] || null;
    dialogueState.value = {
      open: !!currentNpc.value,
      turnIndex: 0,
      useEnglish: false,
    };
    // 位置变化后,检查 daily_event
    triggerDailyEvent();
  }

  function returnToCity() {
    currentScene.value = 'city';
    currentNpc.value = null;
    dialogueState.value = { ...dialogueState.value, open: false };
  }

  function toggleLanguage() {
    dialogueState.value.useEnglish = !dialogueState.value.useEnglish;
  }

  function nextTurn() {
    const turnCount = currentNpc.value?.turns?.length || 0;
    const nextIndex = dialogueState.value.turnIndex + 1;
    if (nextIndex >= turnCount) {
      completeCurrentDialogueTask();
      returnToCity();
      return;
    }
    dialogueState.value.turnIndex = nextIndex;
  }

  /**
   * 玩家选了一个对话选项 — 触发小奖励(鼓励尝试)
   * 真正的任务奖励在最后一轮 nextTurn → completeCurrentDialogueTask 里结算
   */
  function selectOption(optionIndex) {
    playerState.value = applyEffects(playerState.value, {
      mood: 1,
      life_xp: 1,
    }, `dialogue_option:${currentScene.value}#${optionIndex}`);
  }

  function changeMood(delta) {
    playerState.value = applyEffects(playerState.value, { mood: delta }, 'manual_mood_change');
  }

  function completeCurrentDialogueTask() {
    const matchingTask = activeTasks.value.find((task) => (
      task.type === 'dialogue' &&
      (task.dialogue_id === currentScene.value || task.target_location_id === currentScene.value)
    ));
    if (matchingTask) {
      playerState.value = completeTask(playerState.value, taskCatalog.value, matchingTask.id);
    }
  }

  function completeActiveTask(taskId) {
    playerState.value = completeTask(playerState.value, taskCatalog.value, taskId);
  }

  /**
   * 结束当天(到 night 后)
   * 应用睡眠恢复:能量补满 / 压力降低 / 心情微升
   * 然后进入 daySummary 结算弹窗
   */
  function endDay() {
    if (playerState.value.time_block !== 'night') return;
    playerState.value = applyEffects(playerState.value, {
      energy: 100 - playerState.value.status.energy,
      stress: -10,
      mood: 5,
      health: 2,
    }, 'end_day_sleep');

    daySummary.value = {
      day: playerState.value.date.day,
      date: { ...playerState.value.date },
      energy: playerState.value.status.energy,
      mood: playerState.value.status.mood,
      stress: playerState.value.status.stress,
      health: playerState.value.status.health,
      money: playerState.value.wallet.cash_eur,
      parent_trust: playerState.value.parent_trust.score,
      completed_tasks: playerState.value.completed_task_ids.length,
      transactions_count: playerState.value.transactions.length,
      skills: {
        german_xp: playerState.value.skills.german.xp,
        english_xp: playerState.value.skills.english.xp,
        life_xp: playerState.value.skills.life.xp,
      },
    };
  }

  /**
   * 开始下一天(从 daySummary 弹窗确认)
   * 时间跳到新一天的 morning + 检查 daily_event
   */
  function startNextDay() {
    playerState.value = advanceTimeBlock(playerState.value); // morning of next day
    daySummary.value = null;
    currentEvent.value = null;
    triggerDailyEvent();
  }

  // ===== 自动存档 =====
  watch(playerState, (value) => {
    savePlayerState(value);
  }, { deep: true });

  return {
    // state
    playerState,
    stats,
    activeTasks,
    currentScene,
    currentNpc,
    dialogueState,
    currentTimeBlock,
    currentTimeLabel,
    nextTimeBlock,
    currentEvent,
    daySummary,
    // content refs
    scenePoints,
    routePresets,
    taskCatalog,
    dialogueScripts,
    eventCatalog,
    // actions
    enterScene,
    returnToCity,
    toggleLanguage,
    nextTurn,
    selectOption,
    changeMood,
    completeActiveTask,
    advanceTime,
    triggerDailyEvent,
    dismissEvent,
    endDay,
    startNextDay,
  };
});