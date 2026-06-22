import Phaser from 'phaser';

/**
 * 寄宿家庭内部场景(慕尼黑 Gastfamilie)
 * 玩家每天从这里开始:吃早饭 / 跟 Schneider 太太打招呼 / 出门
 */
export default class HomeScene extends Phaser.Scene {
  constructor() {
    super({ key: 'HomeScene' });
  }

  preload() {
    // 寄宿家庭内部背景(从慕尼黑场景图复用)
    this.load.image('host_home_bg', '/assets/scenes/munich/host_home.png');
    // Frau Schneider 立绘(用 anna 立绘占位)
    this.load.image('frau_schneider', '/assets/characters/anna/anna_neutral.png');
    this.load.image('frau_schneider_smile', '/assets/characters/anna/anna_smile.png');
  }

  create() {
    const { width, height } = this.scale;

    // ===== 背景图 =====
    const bg = this.add.image(width / 2, height / 2, 'host_home_bg');
    const scale = Math.max(width / bg.width, height / bg.height);
    bg.setScale(scale);

    // ===== 顶部标题 =====
    this.add.text(width / 2, 32, '🏠 GASTFAMILIE SCHNEIDER', {
      fontFamily: 'Courier New, monospace',
      fontSize: '24px',
      color: '#f4d35e',
      stroke: '#000',
      strokeThickness: 4,
    }).setOrigin(0.5);

    this.add.text(width / 2, 60, '🏠 寄宿家庭 · Lena 的慕尼黑新家', {
      fontFamily: 'Courier New, monospace',
      fontSize: '13px',
      color: '#c9956b',
    }).setOrigin(0.5);

    // ===== 早餐桌(左下,可点击吃早饭) =====
    this.createBreakfastTable(width, height);

    // ===== Frau Schneider NPC(右侧,可点击打招呼) =====
    this.createHostNpc(width, height);

    // ===== 出门按钮(底部中央) =====
    this.createLeaveButton(width, height);

    // ===== 底部提示 =====
    this.add.text(width / 2, height - 14, '☀️ 早安,Lena。点击桌上的早餐、NPC 或下方出门按钮开始新的一天。', {
      fontFamily: 'Courier New, monospace',
      fontSize: '11px',
      color: '#8a7a60',
      fontStyle: 'italic',
    }).setOrigin(0.5);
  }

  createBreakfastTable(width, height) {
    // 早餐桌 rectangle(代表"早餐"交互点)
    const tableX = width * 0.22;
    const tableY = height * 0.78;
    const tableW = 200;
    const tableH = 100;

    const table = this.add.rectangle(tableX, tableY, tableW, tableH, 0x6a4a2a, 0.5);
    table.setStrokeStyle(3, 0xc9956b, 0.8);

    // 标签
    const label = this.add.text(tableX, tableY - 70, '🍞 Frühstück', {
      fontFamily: 'Courier New, monospace',
      fontSize: '18px',
      color: '#f4d35e',
      stroke: '#000',
      strokeThickness: 3,
    }).setOrigin(0.5);

    const hint = this.add.text(tableX, tableY + 10, '吃早饭\nBrötchen + Kaffee', {
      fontFamily: 'Courier New, monospace',
      fontSize: '13px',
      color: '#e8d5b0',
      align: 'center',
    }).setOrigin(0.5);

    // 交互
    table.setInteractive({ useHandCursor: true });
    table.on('pointerover', () => {
      table.setFillStyle(0x8a6a3a, 0.7);
      table.setStrokeStyle(3, 0xf4d35e, 1);
      this.tweens.add({ targets: [table, label, hint], scaleX: 1.05, scaleY: 1.05, duration: 100 });
    });
    table.on('pointerout', () => {
      table.setFillStyle(0x6a4a2a, 0.5);
      table.setStrokeStyle(3, 0xc9956b, 0.8);
      this.tweens.add({ targets: [table, label, hint], scaleX: 1, scaleY: 1, duration: 100 });
    });
    table.on('pointerdown', () => {
      this.game.events.emit('homeAction', 'eat_breakfast');
    });
  }

  createHostNpc(width, height) {
    const npcX = width * 0.78;
    const npcY = height * 0.7;

    const npc = this.add.image(npcX, npcY, 'frau_schneider');
    npc.setDisplaySize(180, 280);

    const nameTag = this.add.text(npcX, npcY - 160, 'Frau Schneider', {
      fontFamily: 'Courier New, monospace',
      fontSize: '16px',
      color: '#f4d35e',
      stroke: '#000',
      strokeThickness: 3,
    }).setOrigin(0.5);

    const roleTag = this.add.text(npcX, npcY + 155, 'Gastmutter · 寄宿妈妈', {
      fontFamily: 'Courier New, monospace',
      fontSize: '11px',
      color: '#c9956b',
    }).setOrigin(0.5);

    npc.setInteractive({ useHandCursor: true });
    npc.on('pointerover', () => {
      npc.setTexture('frau_schneider_smile');
      this.tweens.add({ targets: npc, scaleX: 1.05, scaleY: 1.05, duration: 100 });
    });
    npc.on('pointerout', () => {
      npc.setTexture('frau_schneider');
      this.tweens.add({ targets: npc, scaleX: 1, scaleY: 1, duration: 100 });
    });
    npc.on('pointerdown', () => {
      this.game.events.emit('homeAction', 'greet_host');
    });
  }

  createLeaveButton(width, height) {
    const btnX = width / 2;
    const btnY = height - 70;
    const btnW = 320;
    const btnH = 56;

    const btn = this.add.rectangle(btnX, btnY, btnW, btnH, 0x4a3a2a, 1);
    btn.setStrokeStyle(3, 0xc9956b, 1);

    const btnLabel = this.add.text(btnX, btnY, '🚪 Haus verlassen · 出门', {
      fontFamily: 'Courier New, monospace',
      fontSize: '18px',
      color: '#f4d35e',
      stroke: '#000',
      strokeThickness: 2,
      fontStyle: 'bold',
    }).setOrigin(0.5);

    btn.setInteractive({ useHandCursor: true });
    btn.on('pointerover', () => {
      btn.setFillStyle(0x6a5a4a, 1);
      btn.setStrokeStyle(3, 0xf4d35e, 1);
      this.tweens.add({ targets: btn, scaleX: 1.04, scaleY: 1.04, duration: 100 });
    });
    btn.on('pointerout', () => {
      btn.setFillStyle(0x4a3a2a, 1);
      btn.setStrokeStyle(3, 0xc9956b, 1);
      this.tweens.add({ targets: btn, scaleX: 1, scaleY: 1, duration: 100 });
    });
    btn.on('pointerdown', () => {
      this.game.events.emit('homeAction', 'leave_home');
    });
  }
}