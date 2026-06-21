import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

/**
 * 主游戏状态 store
 * 管理:主角属性 / 当前位置 / 当前 NPC / 对话状态 / 语言切换
 */
export const useGameStore = defineStore('game', () => {
  // ===== 主角 stats (RPG 角色属性) =====
  const stats = ref({
    name: 'Lena',
    age: 16,
    language: {
      german: 'A0',      // CEFR: A0/A1/A2/B1/B2/C1
      english: 'B1',
    },
    mood: 75,             // 0-100
    energy: 80,           // 0-100
    money: 500,           // EUR
    date: { year: 1, month: 9, day: 1 },  // Year 12 开学
    location: 'berlin',   // 当前城市
  });

  // ===== 当前场景状态 =====
  const currentScene = ref('city');  // 'city' | 'cafe' | 'bahnhof' | 'street' | 'home'
  const currentNpc = ref(null);      // 当前对话的 NPC
  const dialogueState = ref({
    open: false,
    turnIndex: 0,
    useEnglish: false,    // 是否切换到英文
  });

  // ===== 柏林三个场景点 =====
  const scenePoints = ref([
    {
      id: 'hauptbahnhof',
      name_de: 'Berlin Hauptbahnhof',
      name_zh: '柏林中央车站',
      type: 'train_station',
      difficulty: 'A1',
      englishAvailable: 100,
      npc: 'Peter (Bahnhofsangestellter)',
      x: 0.18, y: 0.30,  // 地图坐标 (0-1)
    },
    {
      id: 'cafe_einstein',
      name_de: 'Café Einstein',
      name_zh: '爱因斯坦咖啡馆',
      type: 'cafe',
      difficulty: 'A1',
      englishAvailable: 50,
      npc: 'Anna Kellnerin',
      x: 0.55, y: 0.65,
    },
    {
      id: 'kreuzberg',
      name_de: 'Kreuzberg Straße',
      name_zh: '克罗伊茨贝格街头',
      type: 'street',
      difficulty: 'A2',
      englishAvailable: 70,
      npc: '街头小贩 / 路人',
      x: 0.82, y: 0.42,
    },
  ]);

  // ===== NPC 对话剧本(MVP 演示用) =====
  const dialogueScripts = ref({
    hauptbahnhof: {
      npc_name_de: 'Peter Schmidt',
      npc_name_zh: 'Peter 施密特',
      npc_role: 'Bahnhofsangestellter',
      npc_portrait: '/assets/characters/peter/peter_smile.png',
      lang_pref: 'mixed',
      turns: [
        {
          de: 'Guten Tag! Wie kann ich Ihnen helfen?',
          zh: '下午好!请问有什么可以帮您的?',
          en: 'Good afternoon! How can I help you?',
          options_de: ['Ich möchte... | 我想要...', 'Wo ist... ? | ... 在哪里?'],
        },
      ],
    },
    cafe_einstein: {
      npc_name_de: 'Anna Kellnerin',
      npc_name_zh: 'Anna 服务员',
      npc_role: 'Kellnerin',
      npc_portrait: '/assets/characters/anna/anna_smile.png',
      lang_pref: 'de',
      turns: [
        {
          de: 'Hallo! Herzlich willkommen im Café Einstein. Was darf\'s sein?',
          zh: '你好!欢迎光临爱因斯坦咖啡馆。请问要点什么?',
          en: 'Hello! Welcome to Café Einstein. What can I get you?',
          options_de: ['Einen Kaffee, bitte. | 一杯咖啡,谢谢。', 'Was empfehlen Sie? | 您推荐什么?'],
        },
      ],
    },
    kreuzberg: {
      npc_name_de: 'Straßenhändler',
      npc_name_zh: '街头小贩',
      npc_role: 'Verkäufer',
      npc_portrait: '/assets/characters/peter/peter_neutral.png',
      lang_pref: 'de',
      turns: [
        {
          de: 'Hey! Döner? Nur drei Euro!',
          zh: '嘿!要 Döner 吗?只要三欧!',
          en: 'Hey! Döner? Only three euros!',
          options_de: ['Ja, bitte. | 好的,谢谢。', 'Nein, danke. | 不用了,谢谢。'],
        },
      ],
    },
  });

  // ===== Actions =====
  function enterScene(sceneId) {
    currentScene.value = sceneId;
    currentNpc.value = dialogueScripts.value[sceneId];
    dialogueState.value = {
      open: true,
      turnIndex: 0,
      useEnglish: false,
    };
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
    dialogueState.value.turnIndex++;
  }

  function changeMood(delta) {
    stats.value.mood = Math.max(0, Math.min(100, stats.value.mood + delta));
  }

  return {
    stats,
    currentScene,
    currentNpc,
    dialogueState,
    scenePoints,
    dialogueScripts,
    enterScene,
    returnToCity,
    toggleLanguage,
    nextTurn,
    changeMood,
  };
});