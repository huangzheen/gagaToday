import Phaser from 'phaser';

/**
 * 慕尼黑像素地图场景 (FF6 风格)
 *
 * 数据源: OpenStreetMap 真实慕尼黑市中心
 * tileset: 手绘 16×16 像素瓦片 (8 种)
 * 交互: WASD/方向键滚动 + 鼠标拖拽 + 点击 POI
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
    const { cols, rows, tileWidth, tileHeight } = this.cache.json.get('tilemap');
    const layerData = this.cache.json.get('tilemap').layers[0].data;
    const pois = this.cache.json.get('pois');

    this.tileW = tileWidth;
    this.tileH = tileHeight;
    this.mapCols = cols;
    this.mapRows = rows;

    // ── 构建 tilemap (列主序 → 行主序) ──
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

    // ── 地图背景色 ──
    this.cameras.main.setBackgroundColor('#18202a');

    // ── 相机设置 ──
    const mapPixelW = cols * tileWidth;
    const mapPixelH = rows * tileHeight;
    this.cameras.main.setBounds(0, 0, mapPixelW, mapPixelH);
    this.cameras.main.setZoom(2);

    // 居中到 Marienplatz
    const marien = pois.find((p) => p.name === 'Marienplatz');
    if (marien) {
      this.cameras.main.centerOn(
        marien.col * tileWidth + tileWidth / 2,
        marien.row * tileHeight + tileHeight / 2,
      );
    }

    // ── POI 标记 ──
    this.poiGroup = this.add.group();
    pois.forEach((poi) => {
      this.createPOIMarker(poi);
    });

    // ── 按键控制 ──
    this.cursors = this.input.keyboard.createCursorKeys();
    this.wasd = {
      W: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      A: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      S: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      D: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    };

    // ── 鼠标拖拽 ──
    this.input.on('pointermove', (pointer) => {
      if (pointer.isDown) {
        this.cameras.main.scrollX -= (pointer.velocity.x * 0.3);
        this.cameras.main.scrollY -= (pointer.velocity.y * 0.3);
      }
    });

    // ── 滚轮缩放 ──
    this.input.on('wheel', (pointer, gameObjects, deltaX, deltaY) => {
      const zoom = Phaser.Math.Clamp(this.cameras.main.zoom - deltaY * 0.002, 1, 4);
      this.cameras.main.setZoom(zoom);
    });

    // ── 标题 ──
    this.add.text(mapPixelW / 2, 10, 'MÜNCHEN — Altstadt', {
      fontFamily: 'monospace',
      fontSize: '10px',
      color: '#f4d35e',
    }).setOrigin(0.5).setScrollFactor(0).setDepth(100);

    // ── 操作提示 ──
    this.add.text(mapPixelW - 10, mapPixelH - 12, 'WASD/方向键: 移动 | 拖拽/滚轮', {
      fontFamily: 'monospace',
      fontSize: '8px',
      color: '#8aa0a8',
    }).setOrigin(1, 1).setScrollFactor(0).setDepth(100);
  }

  createPOIMarker(poi) {
    const { name, col, row, desc } = poi;
    const cx = col * this.tileW + this.tileW / 2;
    const cy = row * this.tileH + this.tileH / 2;

    // 金色菱形标记
    const marker = this.add.polygon(
      cx, cy - 8,
      [0, -6, 5, 0, 0, 6, -5, 0],
      0xf4d35e, 1,
    );
    marker.setStrokeStyle(1, 0xd4a020, 1);
    this.add.tween({
      targets: marker,
      y: cy - 12,
      scale: { from: 1, to: 0.85 },
      duration: 1200,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    });

    // 背景光晕
    const glow = this.add.circle(cx, cy - 8, 10, 0xf4d35e, 0.12);
    this.add.tween({
      targets: glow,
      alpha: { from: 0.12, to: 0.04 },
      scale: { from: 1, to: 1.6 },
      duration: 1600,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    });

    // 名称标签
    const label = this.add.text(cx, cy - 18, name, {
      fontFamily: 'monospace',
      fontSize: '7px',
      color: '#fff3cf',
      backgroundColor: 'rgba(0,0,0,0.55)',
      padding: { x: 3, y: 1 },
    }).setOrigin(0.5, 1);

    // 点击区域 (不可见的碰撞盒)
    const hit = this.add.rectangle(cx, cy, 32, 32, 0x000000, 0);
    hit.setInteractive({ useHandCursor: true });
    hit.on('pointerover', () => {
      label.setColor('#f4d35e');
      label.setBackgroundColor('rgba(20,30,50,0.85)');
    });
    hit.on('pointerout', () => {
      label.setColor('#fff3cf');
      label.setBackgroundColor('rgba(0,0,0,0.55)');
    });
    hit.on('pointerdown', () => {
      this.showPOIInfo(poi);
    });

    this.poiGroup.addMultiple([marker, glow, label, hit]);
  }

  showPOIInfo(poi) {
    // 用 Phaser 弹窗显示 POI 详情
    const { cols, rows, tileWidth, tileHeight } = this;
    const cx = poi.col * tileWidth + tileWidth / 2;
    const cy = poi.row * tileHeight + tileHeight / 2;

    // 如果已有 infoBox,先移除
    if (this.infoBox) {
      this.infoBox.destroy();
    }

    this.infoBox = this.add.container(cx, cy - 40);

    const bg = this.add.rectangle(0, 0, 160, 36, 0x0a0e1a, 0.92);
    bg.setStrokeStyle(1, 0xc9956b, 0.9);
    this.infoBox.add(bg);

    const title = this.add.text(0, -8, poi.name, {
      fontFamily: 'monospace',
      fontSize: '9px',
      color: '#f4d35e',
    }).setOrigin(0.5);
    this.infoBox.add(title);

    const descText = this.add.text(0, 8, poi.desc + `  [${poi.col},${poi.row}]`, {
      fontFamily: 'monospace',
      fontSize: '7px',
      color: '#aab8bf',
    }).setOrigin(0.5);
    this.infoBox.add(descText);

    // 3 秒后自动消失
    this.time.delayedCall(3000, () => {
      if (this.infoBox) {
        this.infoBox.destroy();
        this.infoBox = null;
      }
    });
  }

  update() {
    const speed = 4;
    let dx = 0;
    let dy = 0;

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
