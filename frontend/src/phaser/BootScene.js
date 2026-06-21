import Phaser from 'phaser';

/**
 * 资源加载场景:加载所有游戏素材
 */
export default class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' });
  }

  preload() {
    // 进度条
    const progressBar = this.add.graphics();
    const progressBox = this.add.graphics();
    progressBox.fillStyle(0x222222, 0.8);
    progressBox.fillRect(240, 270, 320, 50);

    this.load.on('progress', (value) => {
      progressBar.clear();
      progressBar.fillStyle(0xc9956b, 1);
      progressBar.fillRect(250, 280, 300 * value, 30);
    });

    this.load.on('complete', () => {
      progressBar.destroy();
      progressBox.destroy();
    });

    // 加载柏林 3 场景
    this.load.image('scene_hauptbahnhof', '/assets/scenes/berlin/hauptbahnhof_interior.png');
    this.load.image('scene_cafe', '/assets/scenes/berlin/cafe_einstein.png');
    this.load.image('scene_kreuzberg', '/assets/scenes/berlin/street_kreuzberg.png');

    // 加载 NPC 立绘
    this.load.image('anna_neutral', '/assets/characters/anna/anna_neutral.png');
    this.load.image('anna_smile', '/assets/characters/anna/anna_smile.png');
    this.load.image('peter_neutral', '/assets/characters/peter/peter_neutral.png');
    this.load.image('peter_smile', '/assets/characters/peter/peter_smile.png');

    // UI 元素
    this.load.image('ui_dialogue', '/assets/ui/dialogue_box.png');
    this.load.image('ui_button', '/assets/ui/button_normal.png');
    this.load.image('ui_badge_berlin', '/assets/ui/city_badge_berlin.png');
    this.load.image('ui_mic', '/assets/ui/mic_button.png');
  }

  create() {
    // 加载完成后切到城市场景
    this.scene.start('CityScene');
  }
}