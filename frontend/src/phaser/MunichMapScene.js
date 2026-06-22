import Phaser from 'phaser';

/**
 * 慕尼黑 Altstadt 像素地图 (16-bit RPG 风格)
 *
 * tileset: 32×32 像素瓦片 (17 种变体)
 * 交互: WASD/方向键 移动 · 拖拽 · 滚轮缩放 · 点击 POI
 * 配色: 羊皮纸底色 + 深蓝金 UI
 */
export default class MunichMapScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MunichMapScene' });
  }

  preload() {
    this.load.image('munich_tileset', '/assets/munich_map/tileset.png');
    this.load.json('tilemap', '/assets/munich_map/tilemap.json');
    this.load.json('pois', '/assets/munich_map/pois.json');
  }

  create() {
    const tilemapData = this.cache.json.get('tilemap');
    const { cols, rows, tileWidth, tileHeight } = tilemapData;
    const layerData = tilemapData.layers[0].data;
    const pois = this.cache.json.get('pois');

    this.tileW = tileWidth;
    this.tileH = tileHeight;

    // 地图总像素尺寸
    const mapW = cols * tileWidth;
    const mapH = rows * tileHeight;

    // 构建 tilemap (列主序 → 行主序)
    const rowData = [];
    for (let r = 0; r < rows; r++) {
      rowData[r] = [];
      for (let c = 0; c < cols; c++) {
        rowData[r][c] = layerData[c][r];
      }
    }

    const map = this.make.tilemap({ data: rowData, tileWidth, tileHeight });
    const tileset = map.addTilesetImage('munich_tileset', 'munich_tileset', tileWidth, tileHeight, 0, 0);
    this.layer = map.createLayer(0, tileset, 0, 0);

    // 羊皮纸底色
    this.cameras.main.setBackgroundColor('#f0deb8');

    // 相机
    this.cameras.main.setBounds(0, 0, mapW, mapH);
    this.cameras.main.setZoom(2);

    // 定位到 Marienplatz
    const marien = pois.find((p) => p.name === 'Marienplatz');
    if (marien) {
      this.cameras.main.centerOn(
        marien.col * tileWidth + tileWidth / 2,
        marien.row * tileHeight + tileHeight / 2,
      );
    }

    // POI 标记 (RPG 风格任务标记)
    pois.forEach((poi) => this.createQuestMarker(poi));

    // 按键控制
    this.cursors = this.input.keyboard.createCursorKeys();
    this.wasd = {
      W: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      A: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      S: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      D: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    };

    // 鼠标拖拽
    this.input.on('pointermove', (pointer) => {
      if (pointer.isDown) {
        this.cameras.main.scrollX -= pointer.velocity.x * 0.3;
        this.cameras.main.scrollY -= pointer.velocity.y * 0.3;
      }
    });

    // 滚轮缩放
    this.input.on('wheel', (pointer, gObj, dx, dy) => {
      const z = Phaser.Math.Clamp(this.cameras.main.zoom - dy * 0.003, 1, 4);
      this.cameras.main.setZoom(z);
    });

    // ── HUD (深蓝+金) ──
    const hud = this.add.container(0, 0).setScrollFactor(0).setDepth(200);

    // 顶栏
    const titleBg = this.add.rectangle(this.scale.width / 2, 0, 360, 36, 0x0a1428, 0.9);
    titleBg.setOrigin(0.5, 0).setStrokeStyle(1, 0xc9956b, 0.7);
    hud.add(titleBg);

    const title = this.add.text(this.scale.width / 2, 18,
      'MÜNCHEN · Altstadt  |  ' + pois.length + ' Orte',
      { fontFamily: '"Courier New", monospace', fontSize: '12px', color: '#f4d35e' }
    ).setOrigin(0.5);
    hud.add(title);

    // 底栏
    const hintBg = this.add.rectangle(this.scale.width / 2, this.scale.height, 520, 28, 0x0a1428, 0.85);
    hintBg.setOrigin(0.5, 1).setStrokeStyle(1, 0x2a4a6a, 0.6);
    hud.add(hintBg);

    const hint = this.add.text(this.scale.width / 2, this.scale.height - 14,
      'W A S D / 方向键  移动  ·  鼠标拖拽 / 滚轮  缩放  ·  ⭐ 点击标记查看详情',
      { fontFamily: '"Courier New", monospace', fontSize: '9px', color: '#6a8aaa' }
    ).setOrigin(0.5);
    hud.add(hint);
  }

  createQuestMarker(poi) {
    const cx = poi.col * this.tileW + this.tileW / 2;
    const cy = poi.row * this.tileH + this.tileH / 2;

    // RPG 任务感叹号
    const excla = this.add.text(cx, cy - 14, '!', {
      fontFamily: 'Arial Black, Impact, sans-serif',
      fontSize: '18px',
      fontStyle: 'bold',
      color: '#f4d35e',
      stroke: '#000000',
      strokeThickness: 3,
    }).setOrigin(0.5).setDepth(10);
    this.tweens.add({
      targets: excla,
      y: cy - 20,
      duration: 900,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    });

    // 脉冲光圈
    const ring = this.add.circle(cx, cy, 8, 0xf4d35e, 0.2).setDepth(9);
    this.tweens.add({
      targets: ring,
      scale: { from: 0.8, to: 1.8 },
      alpha: { from: 0.2, to: 0 },
      duration: 1500,
      repeat: -1,
      ease: 'Sine.easeInOut',
    });

    // 名称标签 (悬停显示)
    const label = this.add.text(cx, cy - 24, poi.name, {
      fontFamily: '"Courier New", monospace',
      fontSize: '10px',
      color: '#0a1428',
      backgroundColor: 'rgba(244, 211, 94, 0.75)',
      padding: { x: 5, y: 2 },
    }).setOrigin(0.5, 1).setDepth(10);
    label.setAlpha(0);

    // 金色菱形底标
    const diamond = this.add.polygon(cx, cy - 6,
      [0, -6, 6, 0, 0, 6, -6, 0],
      0xc9956b, 1,
    ).setDepth(9).setStrokeStyle(1, 0x8a6a3a, 1);

    // 点击热区
    const hit = this.add.rectangle(cx, cy, 40, 40, 0x000000, 0).setDepth(11);
    hit.setInteractive({ useHandCursor: true });
    hit.on('pointerover', () => {
      label.setAlpha(1);
      diamond.setFillStyle(0xf4d35e, 1);
      excla.setColor('#ffffff');
    });
    hit.on('pointerout', () => {
      label.setAlpha(0);
      diamond.setFillStyle(0xc9956b, 1);
      excla.setColor('#f4d35e');
    });
    hit.on('pointerdown', () => this.showQuestInfo(poi));
  }

  showQuestInfo(poi) {
    if (this.infoBox) { this.infoBox.destroy(); this.infoBox = null; }

    const cam = this.cameras.main;
    const cx = poi.col * this.tileW + this.tileW / 2;
    const cy = poi.row * this.tileH + this.tileH / 2;
    const sx = cx - cam.scrollX;
    const sy = cy - cam.scrollY - 32;

    this.infoBox = this.add.container(0, 0).setScrollFactor(0).setDepth(300);

    const bw = 220, bh = 64;
    const bg = this.add.rectangle(bw / 2, bh / 2, bw, bh, 0x0a1428, 0.94);
    bg.setStrokeStyle(2, 0xc9956b, 0.9).setOrigin(0.5);
    this.infoBox.add(bg);

    this.infoBox.add(
      this.add.text(0, -16, poi.name, {
        fontFamily: '"Courier New", monospace', fontSize: '13px',
        fontStyle: 'bold', color: '#f4d35e',
      }).setOrigin(0.5)
    );
    this.infoBox.add(
      this.add.text(0, 6, poi.desc, {
        fontFamily: '"Courier New", monospace', fontSize: '10px', color: '#aab8bf',
      }).setOrigin(0.5)
    );
    this.infoBox.add(
      this.add.text(0, 22, 'Altstadt · 慕尼黑', {
        fontFamily: '"Courier New", monospace', fontSize: '8px', color: '#4a6a8a',
      }).setOrigin(0.5)
    );

    this.infoBox.setPosition(sx, sy);

    this.time.delayedCall(4000, () => {
      if (this.infoBox) {
        this.tweens.add({
          targets: this.infoBox, alpha: 0, duration: 300,
          onComplete: () => { if (this.infoBox) { this.infoBox.destroy(); this.infoBox = null; } },
        });
      }
    });
  }

  update() {
    const speed = 5;
    let dx = 0, dy = 0;
    if (this.cursors.left.isDown || this.wasd.A.isDown) dx -= speed;
    if (this.cursors.right.isDown || this.wasd.D.isDown) dx += speed;
    if (this.cursors.up.isDown || this.wasd.W.isDown) dy -= speed;
    if (this.cursors.down.isDown || this.wasd.S.isDown) dy += speed;
    if (dx !== 0 || dy !== 0) {
      this.cameras.main.scrollX += dx;
      this.cameras.main.scrollY += dy;
    }
  }
}
