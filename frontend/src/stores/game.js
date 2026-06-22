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
  clearPlayerState,
  completeTask,
  createPlayerState,
  getActiveTasks,
  loadPlayerState,
  savePlayerState,
  spendMoney,
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

const LOCATION_ACTIONS = {
  host_home: [
    { id: 'eat_breakfast', label: '吃早饭', de: 'Frühstück', detail: '+体力 +心情', primary: true },
    { id: 'greet_host', label: '向 Schneider 太太问早', de: 'Guten Morgen', detail: '练一句 A1 问候' },
    { id: 'leave_home', label: '出门去学校', de: 'Zur Schule', detail: '进入慕尼黑地图', primary: true },
    { id: 'reply_parent', label: '回复父母消息', de: 'Nachricht', detail: '+父母信任 -压力' },
    { id: 'sleep', label: '睡觉结算', de: 'Schlafen', detail: '结束 Day 1', primary: true },
  ],
  school: [
    { id: 'school_intro', label: '课堂自我介绍', de: 'Vorstellen', detail: '和 Herr Weber 对话', primary: true },
    { id: 'finish_classes', label: '完成第一天课程', de: 'Unterricht', detail: '+学习经验，进入放学后', primary: true },
  ],
  bakery: [
    { id: 'bakery_dialogue', label: '用德语买 Brötchen', de: 'Bestellen', detail: '-€1.20 +德语XP', primary: true },
  ],
  supermarket: [
    { id: 'buy_groceries', label: '买晚餐食材', de: 'Einkaufen', detail: '-€8.40 +生活XP', primary: true },
  ],
  library: [
    { id: 'study_library', label: '安静自习 45 分钟', de: 'Lernen', detail: '+数学XP -体力', primary: true },
  ],
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
  const currentView = ref(playerState.value.location_id === 'host_home' ? 'home' : 'city');  // 'home' | 'city' | 'scene'
  const currentScene = ref(null);   // null | 'host_home' | 'school' | ...
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
  const recentNotices = ref([]);

  const currentLocation = computed(() => scenePoints.value.find((location) => location.id === playerState.value.location_id) || null);
  const completedTaskIds = computed(() => new Set(playerState.value.completed_task_ids));
  const completion = computed(() => ({
    total: taskCatalog.value.length,
    done: playerState.value.completed_task_ids.length,
  }));
  const latestTransactions = computed(() => playerState.value.transactions.slice(-4).reverse());
  const latestLog = computed(() => playerState.value.action_log.slice(-5).reverse());
  const suggestedActions = computed(() => {
    const actions = LOCATION_ACTIONS[playerState.value.location_id] || [];
    return actions.filter((action) => canRunAction(action.id));
  });

  // ===== Actions =====

  /**
   * 推进时间块到下一个时段,触发该时段 + 当前位置的 daily_event
   */
  function advanceTime() {
    const nextState = advanceTimeBlock(playerState.value);
    playerState.value = nextState;
    triggerDailyEvent();
  }

  function pushNotice(title, body = '') {
    recentNotices.value.unshift({
      id: `notice_${Date.now()}_${recentNotices.value.length}`,
      title,
      body,
    });
    recentNotices.value = recentNotices.value.slice(0, 4);
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
      e.location_id === ps.location_id &&
      (e.required_flags || []).every((flag) => ps.flags?.[flag]) &&
      !(e.sets_flags || []).some((flag) => ps.flags?.[flag])
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
   * 家里吃早饭 — 增加体力 + 心情
   */
  function eatBreakfast() {
    if (playerState.value.time_block !== 'morning') return;
    playerState.value = applyEffects(playerState.value, {
      energy: 10,
      mood: 5,
      life_xp: 2,
    }, 'eat_breakfast');
    pushNotice('早餐完成', 'Brötchen 和咖啡让你精神了一些。');
  }

  /**
   * 跟 Schneider 太太打招呼 — 打开 DialogueBox
   */
  function greetHost() {
    currentScene.value = 'host_home';
    currentNpc.value = dialogueScripts.value['host_home'] || null;
    dialogueState.value = {
      open: !!currentNpc.value,
      turnIndex: 0,
      useEnglish: false,
    };
  }

  /**
   * 从寄宿家庭出门 — 推进到 commute 时段 + 切到 city 视图
   */
  function leaveHome() {
    playerState.value = advanceTimeBlock(playerState.value);
    currentView.value = 'city';
    currentScene.value = null;
    currentNpc.value = null;
    playerState.value.location_id = 'host_home';
    triggerDailyEvent();
  }

  /**
   * 回到寄宿家庭(放学后/傍晚) — 推进到 evening 时段 + 切到 home 视图
   */
  function returnHome() {
    playerState.value = advanceTimeBlock(playerState.value);
    currentView.value = 'home';
    triggerDailyEvent();
  }

  /**
   * 进入 POI(从 Phaser CityScene 点击场景点触发)
   * 行为:travel 路线结算 + 切换 currentScene + 自动开 DialogueBox
   * 末尾:触发 daily_event(可能弹窗 + 解锁任务)
   */
  function enterScene(sceneId) {
    let result = travelTo(playerState.value, routePresets.value, sceneId);
    playerState.value = result.playerState;

    if (sceneId === 'school' && playerState.value.active_task_ids.includes('task_day01_get_to_school')) {
      if (playerState.value.time_block === 'commute') {
        playerState.value = advanceTimeBlock(playerState.value);
      }
      completeTaskIfActive('task_day01_get_to_school', '准时到校', '你赶上了第一节课，父母信任上升。');
    }

    currentScene.value = sceneId;
    currentView.value = 'scene';
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
    currentScene.value = null;
    currentNpc.value = null;
    currentView.value = 'city';
    dialogueState.value = { ...dialogueState.value, open: false };
  }

  function returnToHome() {
    currentScene.value = null;
    currentNpc.value = null;
    currentView.value = 'home';
    playerState.value.location_id = 'host_home';
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

  function openDialogue(locationId = playerState.value.location_id) {
    currentScene.value = locationId;
    currentNpc.value = dialogueScripts.value[locationId] || null;
    dialogueState.value = {
      open: !!currentNpc.value,
      turnIndex: 0,
      useEnglish: false,
    };
    if (!currentNpc.value) pushNotice('这里暂时没有对话', '可以先完成地点动作或去下一个地点。');
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
      pushNotice('任务完成', matchingTask.title_zh);
    }
  }

  function completeActiveTask(taskId) {
    playerState.value = completeTask(playerState.value, taskCatalog.value, taskId);
  }

  function completeTaskIfActive(taskId, title, body) {
    if (!playerState.value.active_task_ids.includes(taskId)) return false;
    playerState.value = completeTask(playerState.value, taskCatalog.value, taskId);
    pushNotice(title, body);
    return true;
  }

  function finishClasses() {
    if (playerState.value.location_id !== 'school') return;
    let nextState = playerState.value;
    while (nextState.time_block !== 'after_school') {
      nextState = advanceTimeBlock(nextState);
    }
    playerState.value = applyEffects(nextState, {
      energy: -12,
      stress: 4,
      german_xp: 6,
      math_xp: 8,
      life_xp: 3,
    }, 'finish_first_school_day');
    pushNotice('第一天课程结束', '你记下了作业，也终于可以去面包店练习点单。');
    triggerDailyEvent();
  }

  function buyGroceries() {
    if (playerState.value.location_id !== 'supermarket') return;
    playerState.value = spendMoney(playerState.value, 8.4, 'groceries:dinner');
    playerState.value = applyEffects(playerState.value, { energy: -3, life_xp: 4, mood: 1 }, 'buy_groceries');
    pushNotice('买到晚餐食材', '你开始对欧元预算有一点真实感觉了。');
  }

  function studyLibrary() {
    if (playerState.value.location_id !== 'library') return;
    playerState.value = applyEffects(playerState.value, {
      energy: -8,
      stress: -3,
      mood: 2,
      math_xp: 10,
      german_xp: 3,
    }, 'study_library');
    pushNotice('自习完成', '图书馆很安静，你完成了一页数学桥接题。');
  }

  function replyParent() {
    const canReply = playerState.value.active_task_ids.includes('task_day01_reply_parent');
    if (!canReply) return;
    completeTaskIfActive('task_day01_reply_parent', '已回复父母', '你报了平安，妈妈回了一个放心的表情。');
  }

  function goHome() {
    playerState.value = {
      ...playerState.value,
      location_id: 'host_home',
    };
    while (!['evening', 'night'].includes(playerState.value.time_block)) {
      playerState.value = advanceTimeBlock(playerState.value);
    }
    currentView.value = 'home';
    currentScene.value = null;
    currentNpc.value = null;
    dialogueState.value = { ...dialogueState.value, open: false };
    triggerDailyEvent();
  }

  function canRunAction(actionId) {
    const ps = playerState.value;
    if (actionId === 'eat_breakfast') return ps.location_id === 'host_home' && ps.time_block === 'morning' && !ps.action_log.some((entry) => entry.payload?.reason === 'eat_breakfast');
    if (actionId === 'greet_host') return ps.location_id === 'host_home' && ['morning', 'evening'].includes(ps.time_block);
    if (actionId === 'leave_home') return ps.location_id === 'host_home' && ['morning', 'commute'].includes(ps.time_block);
    if (actionId === 'reply_parent') return ps.location_id === 'host_home' && ps.active_task_ids.includes('task_day01_reply_parent');
    if (actionId === 'sleep') return ps.location_id === 'host_home' && ps.time_block === 'night';
    if (actionId === 'school_intro') return ps.location_id === 'school';
    if (actionId === 'finish_classes') return ps.location_id === 'school' && !['after_school', 'evening', 'night'].includes(ps.time_block);
    if (actionId === 'bakery_dialogue') return ps.location_id === 'bakery';
    if (actionId === 'buy_groceries') return ps.location_id === 'supermarket';
    if (actionId === 'study_library') return ps.location_id === 'library';
    return false;
  }

  function runLocationAction(actionId) {
    if (actionId === 'eat_breakfast') eatBreakfast();
    if (actionId === 'greet_host') greetHost();
    if (actionId === 'leave_home') leaveHome();
    if (actionId === 'reply_parent') replyParent();
    if (actionId === 'sleep') endDay();
    if (actionId === 'school_intro') openDialogue('school');
    if (actionId === 'finish_classes') finishClasses();
    if (actionId === 'bakery_dialogue') openDialogue('bakery');
    if (actionId === 'buy_groceries') buyGroceries();
    if (actionId === 'study_library') studyLibrary();
  }

  /**
   * 结束当天(到 night 后)
   * 应用睡眠恢复:能量补满 / 压力降低 / 心情微升
   * 然后进入 daySummary 结算弹窗
   */
  function endDay() {
    if (playerState.value.time_block !== 'night') {
      while (playerState.value.time_block !== 'night') {
        playerState.value = advanceTimeBlock(playerState.value);
      }
    }
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

  function resetGame() {
    clearPlayerState();
    playerState.value = createPlayerState(playerStart);
    currentView.value = 'home';
    currentScene.value = null;
    currentNpc.value = null;
    currentEvent.value = null;
    daySummary.value = null;
    recentNotices.value = [];
    dialogueState.value = { open: false, turnIndex: 0, useEnglish: false };
    triggerDailyEvent();
  }

  // ===== 自动存档 =====
  triggerDailyEvent();

  watch(playerState, (value) => {
    savePlayerState(value);
  }, { deep: true });

  return {
    // state
    playerState,
    stats,
    activeTasks,
    currentView,
    currentScene,
    currentNpc,
    dialogueState,
    currentTimeBlock,
    currentTimeLabel,
    nextTimeBlock,
    currentEvent,
    daySummary,
    currentLocation,
    completion,
    completedTaskIds,
    latestTransactions,
    latestLog,
    suggestedActions,
    recentNotices,
    // content refs
    scenePoints,
    routePresets,
    taskCatalog,
    dialogueScripts,
    eventCatalog,
    // actions
    enterScene,
    returnToCity,
    returnToHome,
    eatBreakfast,
    greetHost,
    leaveHome,
    returnHome,
    toggleLanguage,
    nextTurn,
    selectOption,
    changeMood,
    completeActiveTask,
    runLocationAction,
    openDialogue,
    finishClasses,
    goHome,
    resetGame,
    advanceTime,
    triggerDailyEvent,
    dismissEvent,
    endDay,
    startNextDay,
  };
});
