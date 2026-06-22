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

    this.cameras.main.setBackgroundColor('#18202a');
    this.drawMapBase(width, height);

    this.add.text(width / 2, 30, 'MÜNCHEN · DAY 1', {
      fontFamily: 'Arial, sans-serif',
      fontSize: '28px',
      fontStyle: 'bold',
      color: '#fff3cf',
    }).setOrigin(0.5);

    this.add.text(width / 2, 58, '寄宿家庭、学校、面包店、超市、图书馆构成第一天闭环', {
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
      color: '#aab8bf',
    }).setOrigin(0.5);

    const points = locations.map((location) => ({
      id: location.id,
      x: Phaser.Math.Clamp(Math.round(location.x * width), 140, width - 180),
      y: Phaser.Math.Clamp(Math.round(location.y * height), 120, height - 120),
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

    this.add.text(width / 2, height - 24, '点击地点进入生活场景 · 路线会消耗时间、体力和欧元', {
      fontFamily: 'Arial, sans-serif',
      fontSize: '13px',
      color: '#8aa0a8',
    }).setOrigin(0.5);

  }

  drawMapBase(width, height) {
    const graphics = this.add.graphics();

    graphics.fillStyle(0x202936, 1);
    graphics.fillRect(0, 0, width, height);

    graphics.fillStyle(0x263344, 1);
    graphics.fillRoundedRect(70, 95, width - 140, height - 155, 18);

    graphics.lineStyle(18, 0x3a6e83, 0.4);
    graphics.beginPath();
    graphics.moveTo(0, height * 0.62);
    graphics.lineTo(width * 0.28, height * 0.54);
    graphics.lineTo(width * 0.56, height * 0.66);
    graphics.lineTo(width, height * 0.58);
    graphics.strokePath();

    graphics.lineStyle(5, 0x59636c, 0.55);
    for (let x = 110; x < width - 120; x += 120) {
      graphics.beginPath();
      graphics.moveTo(x, 120);
      graphics.lineTo(x + 60, height - 105);
      graphics.strokePath();
    }
    for (let y = 135; y < height - 110; y += 86) {
      graphics.beginPath();
      graphics.moveTo(90, y);
      graphics.lineTo(width - 90, y + 30);
      graphics.strokePath();
    }

    graphics.fillStyle(0x1d513f, 0.5);
    graphics.fillRoundedRect(width * 0.61, height * 0.16, 240, 120, 22);
    graphics.fillRoundedRect(width * 0.09, height * 0.58, 220, 110, 22);
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
    graphics.lineStyle(4, 0xf1c36a, 0.42);

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
    container.setSize(150, 128);

    const shadow = this.add.ellipse(0, 40, 104, 24, 0x000000, 0.24);
    container.add(shadow);

    const card = this.add.rectangle(0, 0, 128, 96, 0x111821, 0.92);
    card.setStrokeStyle(2, 0xe6c16c, 0.95);
    container.add(card);

    const thumb = this.add.image(0, -10, point.texture);
    thumb.setDisplaySize(112, 58);
    container.add(thumb);

    const pin = this.add.circle(-52, -38, 12, 0x7fd1b9, 1);
    pin.setStrokeStyle(2, 0xffffff, 0.9);
    container.add(pin);

    const nameText = this.add.text(0, 35, point.name, {
      fontFamily: 'Arial, sans-serif',
      fontSize: '13px',
      fontStyle: 'bold',
      color: '#fff3cf',
    }).setOrigin(0.5);
    container.add(nameText);

    const infoText = this.add.text(0, 52, `${point.npc} · ${point.difficulty} · EN ${point.english}%`, {
      fontFamily: 'Arial, sans-serif',
      fontSize: '10px',
      color: '#aab8bf',
    }).setOrigin(0.5);
    container.add(infoText);

    const emitClick = () => {
      this.game.events.emit('scenePointClicked', point.id);
    };

    container.setInteractive(new Phaser.Geom.Rectangle(-64, -48, 128, 96), Phaser.Geom.Rectangle.Contains);
    card.setInteractive({ useHandCursor: true });
    thumb.setInteractive({ useHandCursor: true });

    container.on('pointerover', () => {
      card.setStrokeStyle(3, 0x7fd1b9, 1);
      card.setFillStyle(0x182839, 0.98);
      this.tweens.add({
        targets: container,
        y: point.y - 5,
        scale: 1.04,
        duration: 100,
      });
    });

    container.on('pointerout', () => {
      card.setStrokeStyle(2, 0xe6c16c, 0.95);
      card.setFillStyle(0x111821, 0.92);
      this.tweens.add({
        targets: container,
        y: point.y,
        scale: 1,
        duration: 100,
      });
    });

    container.on('pointerdown', emitClick);
    card.on('pointerdown', emitClick);
    thumb.on('pointerdown', emitClick);
  }
}
