/**
 * Phase 4: NPC + Dialogue + Quest + KnowledgeCard fixture
 *
 * 目标:让 PoiDialog 的"开始对话"按钮真的能对话(替换 Phase 3 占位 alert)
 *
 * 设计原则:
 * - 1 个 NPC(教堂导览员 Hans)
 * - 1 个 Dialogue tree(3 节点:欢迎 → 提问 → 结束)
 * - 1 个 Quest(了解圣母教堂)
 * - 1 个 KnowledgeCard(完成后发)
 *
 * Phase 4.1 待办:
 * - 后端 exporter 加载这些数据(当前 stub,返回空数组)
 * - 当前前端通过 import 直接使用,后端 bundle.npcs/dialogues/quests 仍是空
 */

import type { Dialogue, KnowledgeCard, Npc, Quest } from '../schemas/content'

// ── NPC ──
export const NPC_HANS_FRAUENKIRCHE: Npc = {
  id: 'npc_hans_frauenkirche',
  poiId: 'frauenkirche',
  name: {
    de: 'Hans Müller',
    zh: '汉斯·穆勒',
  },
  role: {
    de: 'Kirchenführer',
    zh: '教堂导览员',
  },
  imageUrls: {},
  published: true,
}

// ── Dialogue tree ──
// 节点设计:
//   start  → 提问"教堂何时建造?"
//   q_ask  → 3 个选择(2 正确 + 1 错误)
//   q_done → 知识卡发放 + 完成 quest
//   end    → terminal
export const DIALOGUE_HANS_FRAUENKIRCHE: Dialogue = {
  id: 'dlg_hans_frauenkirche',
  npcId: 'npc_hans_frauenkirche',
  startNodeId: 'start',
  nodes: [
    {
      id: 'start',
      npcText: {
        de: 'Willkommen in der Frauenkirche! Ich bin Hans. Möchten Sie etwas über die Geschichte der Kirche erfahren?',
        zh: '欢迎来到圣母教堂!我是汉斯。想了解一下教堂的历史吗?',
      },
      choices: [
        {
          id: 'c_yes',
          text: { de: 'Ja, bitte!', zh: '好的,请讲!' },
          nextNodeId: 'q_ask',
          learningRefs: [],
        },
        {
          id: 'c_bye',
          text: { de: 'Nein danke, auf Wiedersehen.', zh: '不用了,再见。' },
          nextNodeId: 'end',
          learningRefs: [],
        },
      ],
    },
    {
      id: 'q_ask',
      npcText: {
        de: 'Gut! Wissen Sie, wann die Frauenkirche fertig gebaut wurde? (15. Jahrhundert)',
        zh: '好的!您知道圣母教堂是什么时候完工的吗?(15 世纪)',
      },
      choices: [
        {
          id: 'c_correct_15',
          text: { de: 'Im fünfzehnten Jahrhundert.', zh: '十五世纪。' },
          nextNodeId: 'q_done',
          learningRefs: ['lc_frauenkirche_year'],
        },
        {
          id: 'c_wrong_18',
          text: { de: 'Im achtzehnten Jahrhundert.', zh: '十八世纪。' },
          nextNodeId: 'q_retry',
          learningRefs: [],
        },
        {
          id: 'c_wrong_20',
          text: { de: 'Im zwanzigsten Jahrhundert.', zh: '二十世纪。' },
          nextNodeId: 'q_retry',
          learningRefs: [],
        },
      ],
      result: 'neutral',
    },
    {
      id: 'q_retry',
      npcText: {
        de: 'Hmm, nicht ganz. Versuchen Sie es noch einmal. Die Frauenkirche wurde zwischen 1468 und 1488 gebaut.',
        zh: '不太对。再试一次。圣母教堂建于 1468 至 1488 年间。',
      },
      choices: [
        {
          id: 'c_retry_correct',
          text: { de: 'Im fünfzehnten Jahrhundert.', zh: '十五世纪。' },
          nextNodeId: 'q_done',
          learningRefs: ['lc_frauenkirche_year'],
        },
        {
          id: 'c_retry_bye',
          text: { de: 'Danke, ich gehe.', zh: '谢谢,我先走了。' },
          nextNodeId: 'end',
          learningRefs: [],
        },
      ],
    },
    {
      id: 'q_done',
      npcText: {
        de: 'Richtig! Die Frauenkirche wurde im fünfzehnten Jahrhundert fertig gebaut. Hier ist Ihr Wissenszertifikat.',
        zh: '答对了!圣母教堂建于十五世纪。这是您的知识卡。',
      },
      choices: [
        {
          id: 'c_thanks',
          text: { de: 'Vielen Dank!', zh: '非常感谢!' },
          nextNodeId: 'end',
          learningRefs: [],
        },
      ],
      result: 'success',
    },
    {
      id: 'end',
      npcText: {
        de: 'Auf Wiedersehen und vielen Dank für Ihren Besuch!',
        zh: '再见,感谢您的参观!',
      },
      choices: [],
      terminal: true,
    },
  ],
  published: true,
}

// ── Quest ──
export const QUEST_LEARN_FRAUENKIRCHE: Quest = {
  id: 'quest_learn_frauenkirche',
  title: {
    de: 'Lerne die Frauenkirche kennen',
    zh: '了解圣母教堂',
  },
  description: {
    de: 'Sprich mit Hans und beantworte seine Frage zur Geschichte der Frauenkirche.',
    zh: '跟汉斯对话并回答关于圣母教堂历史的问题。',
  },
  poiId: 'frauenkirche',
  dialogueIds: ['dlg_hans_frauenkirche'],
  prerequisites: [],
  reward: {
    germanXp: 10,
    moneyCents: -100,  // 象征性收费,真实游戏可改为入场费
    energy: -5,
    unlockPoiIds: [],
    itemGrants: {},
  },
  published: true,
}

// ── KnowledgeCard(完成后发) ──
export const KC_FRAUENKIRCHE: KnowledgeCard = {
  id: 'kc_frauenkirche',
  title: {
    de: 'Die Frauenkirche (München)',
    zh: '圣母教堂(慕尼黑)',
  },
  body: {
    de: 'Die Frauenkirche (Kirche Unserer Lieben Frau) ist die Kathedrale des Erzbistums München und Freising. Sie wurde zwischen 1468 und 1488 im spätgotischen Stil erbaut und ist das Wahrzeichen der Stadt München.',
    zh: '圣母教堂(我们亲爱的夫人教堂)是慕尼黑和弗赖辛总教区的主教座堂,建于 1468 至 1488 年,采用晚期哥特式风格,是慕尼黑市的象征。',
  },
  refs: ['lc_frauenkirche_year'],
  published: true,
}

// ── Bundle export(供 App.vue / player store 使用) ──
export const PHASE4_FIXTURE = {
  npcs: [NPC_HANS_FRAUENKIRCHE],
  dialogues: [DIALOGUE_HANS_FRAUENKIRCHE],
  quests: [QUEST_LEARN_FRAUENKIRCHE],
  knowledgeCards: [KC_FRAUENKIRCHE],
} as const