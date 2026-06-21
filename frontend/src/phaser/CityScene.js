import Phaser from 'phaser';

/**
 * 柏林城市顶视图 RPG 场景
 * 展示 Berlin 三个场景点 + 玩家可点击进入对话
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

    // 顶部:柏林城市标题
    this.add.text(width / 2, 32, '✦ BERLIN ✦', {
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

    // 三个场景点 — 用场景缩略图 + 标签
    const points = [
      {
        id: 'hauptbahnhof',
        x: 180,
        y: 230,
        texture: 'scene_hauptbahnhof',
        name: 'Hauptbahnhof',
        npc: 'Peter',
        difficulty: 'A1',
        english: 100,
      },
      {
        id: 'cafe_einstein',
        x: 512,
        y: 350,
        texture: 'scene_cafe',
        name: 'Café Einstein',
        npc: 'Anna',
        difficulty: 'A1',
        english: 50,
      },
      {
        id: 'kreuzberg',
        x: 840,
        y: 260,
        texture: 'scene_kreuzberg',
        name: 'Kreuzberg',
        npc: 'Street Vendor',
        difficulty: 'A2',
        english: 70,
      },
    ];

    points.forEach((p) => {
      this.createScenePoint(p);
    });

    // 底部提示
    this.add.text(width / 2, height - 30, '点击场景点进入对话', {
      fontFamily: 'Courier New, monospace',
      fontSize: '13px',
      color: '#6a5a40',
    }).setOrigin(0.5);

    // 连线 — 三个点之间的"走遍德国"路径
    const graphics = this.add.graphics();
    graphics.lineStyle(3, 0x4a3a2a, 0.5);
    graphics.beginPath();
    graphics.moveTo(180, 230);
    graphics.lineTo(512, 350);
    graphics.lineTo(840, 260);
    graphics.strokePath();
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

    // 交互区
    container.setInteractive(
      new Phaser.Geom.Rectangle(-110, -72, 220, 145),
      Phaser.Geom.Rectangle.Contains
    );

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