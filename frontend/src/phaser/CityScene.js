import Phaser from 'phaser';
import locations from '@/content/munich/locations.json';
import routes from '@/content/munich/routes.json';

/**
 * 慕尼黑城市顶视图 RPG 场景
 * 展示 MVP 场景点 + 玩家可点击进入对话
 */
export default class CityScene extends Phaser.Scene {
  constructor() {
    super({ key: 'CityScene' });
  }

  create() {
    const width = this.scale.width;
    const height = this.scale.height;

    // 背景 — 用深棕色模拟 RPG Maker 风格地图
    this.cameras.main.setBackgroundColor('#2d261d');

    // 顶部:慕尼黑城市标题
    this.add.text(width / 2, 32, '✦ MÜNCHEN ✦', {
      fontFamily: 'Courier New, monospace',
      fontSize: '32px',
      color: '#f4d35e',
      stroke: '#000',
      strokeThickness: 4,
    }).setOrigin(0.5);

    this.add.text(width / 2, 60, 'Year 12 · September · Woche 1', {
      fontFamily: 'Courier New, monospace',
      fontSize: '14px',
      color: '#8a7a60',
    }).setOrigin(0.5);

    const points = locations.map((location) => ({
      id: location.id,
      x: Math.round(location.x * width),
      y: Math.round(location.y * height),
      texture: location.asset,
      name: location.name_de,
      npc: location.npc,
      difficulty: location.difficulty,
      english: location.englishAvailable,
    }));

    this.drawRoutes(width, height);

    points.forEach((p) => {
      this.createScenePoint(p);
    });

    this.add.text(width / 2, height - 30, '点击场景点进入对话', {
      fontFamily: 'Courier New, monospace',
      fontSize: '13px',
      color: '#6a5a40',
    }).setOrigin(0.5);

  }

  drawRoutes(width, height) {
    const pointsById = new Map(locations.map((location) => [
      location.id,
      {
        x: Math.round(location.x * width),
        y: Math.round(location.y * height),
      },
    ]));

    const graphics = this.add.graphics();
    graphics.lineStyle(3, 0x4a3a2a, 0.5);

    routes.forEach((route) => {
      const from = pointsById.get(route.from);
      const to = pointsById.get(route.to);
      if (!from || !to) return;
      graphics.beginPath();
      graphics.moveTo(from.x, from.y);
      graphics.lineTo(to.x, to.y);
      graphics.strokePath();
    });
  }

  createScenePoint(point) {
    const container = this.add.container(point.x, point.y);
    container.setSize(220, 200);

    // 缩略图(用 Phaser 缩放)
    const thumb = this.add.image(0, 0, point.texture);
    thumb.setDisplaySize(200, 130);
    container.add(thumb);

    // 场景名称
    const nameText = this.add.text(0, 80, point.name, {
      fontFamily: 'Courier New, monospace',
      fontSize: '14px',
      color: '#f4d35e',
      stroke: '#000',
      strokeThickness: 2,
    }).setOrigin(0.5);
    container.add(nameText);

    // NPC + 难度 + 英文可用度
    const infoText = this.add.text(0, 96, `${point.npc} · ${point.difficulty} · EN ${point.english}%`, {
      fontFamily: 'Courier New, monospace',
      fontSize: '10px',
      color: '#c9956b',
    }).setOrigin(0.5);
    container.add(infoText);

    // 边框(像素艺术风格)
    const frame = this.add.rectangle(0, 0, 220, 145, 0x000000, 0);
    frame.setStrokeStyle(2, 0xc9956b, 1);
    container.add(frame);

    // 交互区:用默认 hitArea(整个 container size),让 Phaser 用 Rectangle.contains
    container.setInteractive({ useHandCursor: true });

    container.on('pointerover', () => {
      frame.setStrokeStyle(3, 0xf4d35e, 1);
      this.tweens.add({
        targets: container,
        scale: 1.05,
        duration: 100,
      });
    });

    container.on('pointerout', () => {
      frame.setStrokeStyle(2, 0xc9956b, 1);
      this.tweens.add({
        targets: container,
        scale: 1,
        duration: 100,
      });
    });

    container.on('pointerdown', () => {
      // 发送事件给 Vue
      this.game.events.emit('scenePointClicked', point.id);
    });
  }
}
