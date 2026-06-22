# gagaToday Content Schema

版本：v0.1  
日期：2026-06-21  
适用范围：MVP 内容 JSON

---

## 1. 设计原则

内容数据是 gagaToday 的长期资产。MVP 阶段使用 JSON 文件，未来可以迁移到数据库或 CMS，但字段语义应保持稳定。

原则：

- 内容与代码分离；
- 所有 ID 稳定、可引用；
- 真实世界数据必须有来源；
- Agent 生成内容必须可审核；
- 游戏逻辑只依赖 schema，不依赖具体城市；
- MVP 内容优先服务 30 天慕尼黑闭环。

---

## 2. 通用字段

推荐所有可审核内容包含：

```json
{
  "id": "stable_snake_case_id",
  "review_status": "draft",
  "content_version": "mvp-0.1",
  "source": {
    "type": "manual",
    "label": "Human-authored MVP content",
    "url": null,
    "retrieved_at": null,
    "confidence": 1.0
  },
  "notes": ""
}
```

### 2.1 `review_status`

允许值：

- `draft`：草稿；
- `needs_review`：需要人工审核；
- `reviewed`：已人工看过；
- `approved`：可进入测试；
- `published`：可进入正式内容。

MVP 手写内容可以是 `approved`，Agent 生成内容默认只能是 `draft` 或 `needs_review`。

### 2.2 `source.type`

允许值：

- `manual`；
- `official_site`；
- `open_data`；
- `osm`；
- `public_document`；
- `agent_generated`；
- `estimated`;
- `placeholder`。

### 2.3 ID 命名

使用 snake_case：

```text
munich_bakery
munich_route_home_school_walk
npc_frau_schneider
dlg_bakery_order_a1
event_day01_first_school_morning
```

---

## 3. PlayerState

文件建议：

```text
frontend/src/content/munich/player_start.json
```

示例：

```json
{
  "player_id": "local_player",
  "cohort_id": null,
  "content_version": "mvp-0.1",
  "name": "Lena",
  "age": 16,
  "date": { "year": 1, "month": 9, "day": 1, "weekday": "monday" },
  "time_block": "morning",
  "location_id": "host_home",
  "wallet": { "cash_eur": 500, "monthly_support_eur": 650 },
  "status": {
    "energy": 80,
    "mood": 75,
    "stress": 20,
    "health": 90
  },
  "skills": {
    "german": { "cefr": "A0", "xp": 0 },
    "english": { "cefr": "B1", "xp": 0 },
    "math": { "level": "igcse_bridge", "xp": 0 },
    "life": { "xp": 0 }
  },
  "parent_trust": {
    "level": 2,
    "score": 60
  },
  "flags": {},
  "action_log": []
}
```

---

## 4. Location

文件：

```text
locations.json
```

必填字段：

```json
{
  "id": "bakery",
  "name_de": "Bäckerei am Platz",
  "name_zh": "广场面包店",
  "type": "bakery",
  "difficulty": "A1",
  "englishAvailable": 40,
  "npc": "Anna",
  "x": 0.55,
  "y": 0.56,
  "asset": "scene_bakery",
  "mvpRole": "ai_speech_task"
}
```

字段说明：

- `id`：地点稳定 ID；
- `type`：地点类型；
- `difficulty`：语言难度；
- `englishAvailable`：英文可用度，0-100；
- `x`, `y`：游戏地图相对坐标，0-1；
- `asset`：Phaser 资源 key；
- `mvpRole`：该地点在 MVP 中承担的玩法功能。

推荐 `type`：

- `home`;
- `school`;
- `bakery`;
- `grocery`;
- `library`;
- `station`;
- `museum`;
- `cafe`;
- `sports`;
- `square`。

---

## 5. Route

文件：

```text
routes.json
```

示例：

```json
{
  "from": "host_home",
  "to": "school",
  "mode": "walking",
  "minutes": 18,
  "cost_eur": 0,
  "energy_cost": 5,
  "route_points": [[160, 392], [260, 320], [370, 196]]
}
```

字段说明：

- `from` / `to`：Location ID；
- `mode`：`walking`、`ubahn`、`tram`、`bus`、`bike`、`regional_train`；
- `minutes`：游戏内耗时；
- `cost_eur`：欧元支出；
- `energy_cost`：体力消耗；
- `route_points`：可选，用于路线动画。

MVP 路线人工配置，不调用实时路线 API。

---

## 6. Npc

文件：

```text
npcs.json
```

示例：

```json
{
  "id": "npc_frau_schneider",
  "name_de": "Frau Schneider",
  "name_zh": "Schneider 太太",
  "role": "Gastmutter",
  "location_id": "host_home",
  "portrait": "/assets/characters/anna/anna_neutral.png",
  "lang_pref": { "de": 0.7, "en": 0.3 },
  "can_speak_english": true,
  "english_level": "B1",
  "personality": ["patient", "warm", "practical"],
  "relationship_defaults": {
    "friendship": 20,
    "trust": 40,
    "familiarity": 30,
    "conflict": 0
  },
  "review_status": "approved"
}
```

MVP 目前可把轻量 NPC 信息放在 `dialogues.json` 中；正式扩展时应拆到 `npcs.json`。

---

## 7. DialogueScenario

文件：

```text
dialogues.json
```

当前 MVP 简化结构：

```json
{
  "bakery": {
    "npc_name_de": "Anna",
    "npc_name_zh": "Anna 店长",
    "npc_role": "Bäckerei-Inhaberin",
    "npc_portrait": "/assets/characters/anna/anna_smile.png",
    "lang_pref": "de",
    "turns": [
      {
        "de": "Hallo! Was darf es sein?",
        "zh": "你好！请问要点什么？",
        "en": "Hello! What would you like?",
        "options_de": [
          "Ein Brötchen, bitte. | 一个小面包，谢谢。",
          "Was empfehlen Sie? | 您推荐什么？"
        ]
      }
    ]
  }
}
```

目标正式结构：

```json
{
  "id": "dlg_bakery_order_a1",
  "location_id": "bakery",
  "npc_id": "npc_anna_bakery",
  "type": "scripted_or_ai_assisted",
  "difficulty": "A1",
  "learning_objectives": [
    "kp_deutsch_a1_ordering_001"
  ],
  "ai_enabled": true,
  "turns": [
    {
      "turn_id": "t1",
      "speaker": "npc",
      "de": "Hallo! Was darf es sein?",
      "en": "Hello! What would you like?",
      "zh": "你好！请问要点什么？",
      "expected_player_intents": ["order_bread", "ask_recommendation"]
    }
  ],
  "success_rules": {
    "min_intents_matched": 1,
    "allow_english_fallback": true,
    "german_xp": 10
  },
  "review_status": "approved"
}
```

---

## 8. DailyEvent

文件：

```text
daily_events.json
```

示例：

```json
{
  "id": "event_day01_first_school_morning",
  "day": 1,
  "time_block": "morning",
  "location_id": "host_home",
  "title_zh": "第一天上学",
  "summary_zh": "寄宿家庭提醒你早点出门。",
  "required_flags": [],
  "sets_flags": ["met_host_mother", "day01_started"],
  "actions": [
    {
      "type": "message",
      "message_id": "msg_host_morning_day01"
    },
    {
      "type": "unlock_task",
      "task_id": "task_go_to_school_day01"
    }
  ],
  "review_status": "approved"
}
```

`time_block` 推荐值：

- `morning`;
- `commute`;
- `school_morning`;
- `lunch`;
- `school_afternoon`;
- `after_school`;
- `evening`;
- `night`。

---

## 9. Task

文件可嵌入 daily events，或独立：

```text
tasks.json
```

示例：

```json
{
  "id": "task_go_to_school_day01",
  "title_zh": "准时到学校",
  "description_zh": "从寄宿家庭出发，前往国际学校。",
  "type": "travel",
  "target_location_id": "school",
  "deadline": { "day": 1, "time_block": "school_morning" },
  "rewards": {
    "parent_trust": 2,
    "life_xp": 5
  },
  "failure_effects": {
    "stress": 5,
    "teacher_trust": -2
  }
}
```

---

## 10. Message / Mail / Bill

### 10.1 Message

```json
{
  "id": "msg_parent_day01_evening",
  "from": "妈妈",
  "channel": "messages",
  "day": 1,
  "time_block": "evening",
  "text_zh": "第一天还顺利吗？记得吃饭，别太晚睡。",
  "requires_reply": true,
  "reply_options": [
    {
      "id": "reply_honest",
      "text_zh": "有点累，但还可以。",
      "effects": { "parent_trust": 1, "mood": 2 }
    }
  ]
}
```

### 10.2 Mail

```json
{
  "id": "mail_math_homework_day01",
  "from": "Herr Brown",
  "subject": "AS Mathematics homework",
  "language": "en",
  "day": 1,
  "time_block": "after_school",
  "body_zh": "数学老师布置了基础代数作业。",
  "linked_task_id": "task_math_homework_day01"
}
```

### 10.3 Bill

```json
{
  "id": "bill_phone_month01",
  "type": "phone_plan",
  "amount_eur": 14.99,
  "due_day": 7,
  "paid": false,
  "late_fee_eur": 2,
  "effects_if_late": {
    "parent_trust": -3,
    "stress": 5
  }
}
```

---

## 11. Lesson / Homework / Test

### 11.1 Lesson

```json
{
  "id": "lesson_de_a1_introduction",
  "track": "deutsch",
  "title_zh": "自我介绍",
  "kp_refs": ["kp_deutsch_a1_intro_001"],
  "estimated_minutes": 20,
  "unlocks_dialogue_id": "dlg_school_intro_a1"
}
```

### 11.2 Homework

```json
{
  "id": "homework_math_day01",
  "track": "alevels",
  "subject": "mathematics",
  "title_zh": "代数衔接练习",
  "kp_refs": ["kp_alevels_mathematics_c1_001"],
  "due_day": 2,
  "estimated_minutes": 30,
  "difficulty": 1
}
```

### 11.3 Test

```json
{
  "id": "test_de_week01_intro",
  "track": "deutsch",
  "title_zh": "A1 自我介绍小测",
  "day": 5,
  "kp_refs": ["kp_deutsch_a1_intro_001"],
  "score_rules": {
    "base": "skill_xp",
    "modifiers": ["energy", "stress", "sleep"]
  }
}
```

---

## 12. Recipe

文件：

```text
recipes.json
```

示例：

```json
{
  "id": "recipe_egg_toast",
  "name_zh": "煎蛋吐司",
  "name_de": "Toast mit Spiegelei",
  "ingredients": [
    { "id": "egg", "quantity": 1 },
    { "id": "toast", "quantity": 2 }
  ],
  "steps": [
    { "type": "click", "target": "pan", "seconds": 3 },
    { "type": "timer", "target": "egg", "seconds": 10 }
  ],
  "effects": {
    "energy": 12,
    "mood": 3,
    "money_saved_estimate_eur": 4
  },
  "difficulty": 1
}
```

---

## 13. Achievement

文件：

```text
achievements.json
```

示例：

```json
{
  "id": "ach_first_brotchen",
  "title_zh": "第一次独自买小面包",
  "description_zh": "用德语在面包店完成一次点餐。",
  "trigger": {
    "type": "dialogue_success",
    "dialogue_id": "dlg_bakery_order_a1"
  },
  "rewards": {
    "german_xp": 10,
    "life_xp": 5
  }
}
```

---

## 14. ActionLogEntry

本地存档和未来云存档都应记录行动日志。

示例：

```json
{
  "id": "log_000001",
  "day": 1,
  "time_block": "morning",
  "action_type": "travel",
  "payload": {
    "from": "host_home",
    "to": "school",
    "mode": "walking"
  },
  "effects": {
    "energy": -5,
    "time_minutes": 18
  },
  "created_at": "2026-06-21T12:00:00Z"
}
```

---

## 15. Schema 变更规则

任何 agent 修改 schema 时必须：

1. 更新本文档；
2. 说明新增字段是必填还是可选；
3. 更新至少一个示例 JSON；
4. 如果已有内容会失效，提供迁移说明；
5. 运行前端构建或内容校验。

MVP 阶段可以保持 JSON 简单，但不要让字段语义漂移。
