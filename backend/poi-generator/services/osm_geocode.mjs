#!/usr/bin/env node
/**
 * OSM POI 反向地理编码 — 按名字搜 PMTiles 找坐标
 *
 * 用法: node osm_geocode.mjs <query> [bbox_lat_min] [bbox_lat_max] [bbox_lng_min] [bbox_lng_max]
 * 示例: node osm_geocode.mjs "München Hauptbahnhof"
 *       node osm_geocode.mjs "Hauptbahnhof"
 *
 * tile_url 默认: http://127.0.0.1:8081/public/assets/munich_map/pmtiles/germany-zoom16.pmtiles
 *
 * 返回: { success, query, matches: [{name, lat, lng, class, subclass, rank, score, ...}] }
 */

import { PMTiles } from '/Volumes/NewDisk/GermanLearning/frontend/node_modules/pmtiles/dist/esm/index.js';
import { VectorTile } from '/Volumes/NewDisk/GermanLearning/frontend/node_modules/@mapbox/vector-tile/index.js';
import { PbfReader } from '/Volumes/NewDisk/GermanLearning/frontend/node_modules/pbf/index.js';

const TILE_URL = process.argv[7] || 'http://127.0.0.1:8081/public/assets/munich_map/pmtiles/germany-zoom16.pmtiles';
const QUERY = process.argv[2];

// 默认 Munich bbox
const BBOX = {
  lat_min: parseFloat(process.argv[3]) || 48.06,
  lat_max: parseFloat(process.argv[4]) || 48.25,
  lng_min: parseFloat(process.argv[5]) || 11.36,
  lng_max: parseFloat(process.argv[6]) || 11.75,
};

if (!QUERY) {
  console.error(JSON.stringify({ success: false, error: 'Usage: node osm_geocode.mjs <query> [lat_min] [lat_max] [lng_min] [lng_max]' }));
  process.exit(1);
}

// ── Tile 计算 ──
function tileXY(lat, lng, z) {
  const n = 1 << z;
  return {
    x: Math.floor((lng + 180) / 360 * n),
    y: Math.floor((1 - Math.log(Math.tan(lat * Math.PI / 180) + 1 / Math.cos(lat * Math.PI / 180)) / Math.PI) / 2 * n),
  };
}

function bboxTiles(bbox, z) {
  const tl = tileXY(bbox.lat_max, bbox.lng_min, z);
  const br = tileXY(bbox.lat_min, bbox.lng_max, z);
  const tiles = [];
  for (let x = tl.x; x <= br.x; x++) {
    for (let y = tl.y; y <= br.y; y++) tiles.push({ z, x, y });
  }
  return tiles;
}

// ── Query 归一化 ──
function normalizeQuery(q) {
  const orig = q.trim();
  const norm = simplifyChs(orig).toLowerCase()
    // 去掉各种"慕尼黑"城市前缀
    .replace(/münchen|munchen|munich/g, '')
    .replace(/慕尼黑|明興/g, '')
    // 去掉"中央站/总站/火车站"等中文通用后缀(避免 query 全空),但保留 hauptbahnhof/dom/platz 等具体德语名词
    .replace(/central\s*station|总站|中央站|火车站|主教堂/g, '')
    .replace(/[^\w\s\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  // 如果 normalize 把 query 吃光了(全城市前缀/通用词),退回原 query
  return norm.length >= 2 ? norm : orig.toLowerCase();
}

// ── 中文繁简 → 简体 (覆盖常用地名) ──
function simplifyChs(s) {
  const map = {
    '聖': '圣', '偉': '伟', '漢': '汉', '國': '国', '學': '学', '術': '术',
    '會': '会', '長': '长', '華': '华', '門': '门', '時': '时', '東': '东',
    '車': '车', '興': '兴', '衛': '卫', '飛': '飞', '麥': '麦', '麗': '丽',
    '業': '业', '開': '开', '關': '关', '園': '园', '廣': '广', '場': '场',
    '臺': '台', '灣': '湾', '島': '岛', '舊': '旧', '區': '区', '廳': '厅',
    '體': '体', '館': '馆', '廟': '庙', '醫': '医', '黨': '党', '鄉': '乡',
    '畫': '画', '術': '术', '銀': '银', '橋': '桥', '鐘': '钟', '鐵': '铁',
    '兒': '儿', '專': '专', '寫': '写', '賓': '宾', '萊': '莱', '蘭': '兰',
    '蘇': '苏', '薩': '萨', '達': '达', '頓': '顿', '盧': '卢', '魯': '鲁',
    '謝': '谢', '貝': '贝', '賓': '宾', '紐': '纽', '約': '约', '邁': '迈',
    '賓': '宾', '塞': '塞', '維': '维', '納': '纳',
  };
  return s.replace(/[\u4e00-\u9fff]/g, ch => map[ch] || ch);
}

// ── 评分: 越高越好 ──
// 注意: 对中文做繁简归一,避免 OSM 繁体名 匹不到 简体 query
function scoreMatch(name, queryNorm) {
  let nameNorm = name.toLowerCase()
    .replace(/münchen|munchen|munich/g, '')
    .replace(/[^\w\s\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  // 繁体 → 简体
  nameNorm = simplifyChs(nameNorm);
  if (!nameNorm) return 0;

  // 完全匹配(忽略城市前缀)
  if (nameNorm === queryNorm) return 1000;
  // 完全包含 query
  if (nameNorm.includes(queryNorm)) {
    // 名字越短越具体,加分
    const lenPenalty = Math.max(0, nameNorm.length - queryNorm.length);
    return 500 - lenPenalty;
  }
  // query 完全包含 name
  if (queryNorm.includes(nameNorm) && nameNorm.length >= 4) {
    return 200 - Math.max(0, nameNorm.length - queryNorm.length);
  }
  // 单词级别匹配(至少一个核心词命中)
  const queryWords = queryNorm.split(/\s+/).filter(w => w.length >= 3);
  const nameWords = nameNorm.split(/\s+/);
  let wordHits = 0;
  for (const qw of queryWords) {
    if (nameWords.some(nw => nw === qw || nw.includes(qw) || qw.includes(nw))) {
      wordHits++;
    }
  }
  if (wordHits > 0) return 50 * wordHits;
  return 0;
}

// ── Munich 中心距离 (km) ── 用于 proximity bias,优先返回主城区 POI
function munichCenterDistKm(lat, lng) {
  const R = 6371;
  const dLat = (lat - 48.14) * Math.PI / 180;
  const dLng = (lng - 11.58) * Math.PI / 180;
  const a = Math.sin(dLat/2)**2 + Math.cos(lat * Math.PI / 180) * Math.cos(48.14 * Math.PI / 180) * Math.sin(dLng/2)**2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
}
function proximityBonus(km) {
  if (km < 5) return 50;
  if (km < 10) return 20;
  if (km < 20) return 5;
  return 0;
}

// ── 主流程 ──
async function main() {
  const tiles = bboxTiles(BBOX, 14);
  const queryNorm = normalizeQuery(QUERY);

  const p = new PMTiles(TILE_URL);
  await p.getHeader();

  const matches = [];

  await Promise.all(tiles.map(async (st) => {
    try {
      const r = await p.getZxy(st.z, st.x, st.y);
      if (!r?.data) return;
      const vt = new VectorTile(new PbfReader(r.data));
      const poiLayer = vt.layers.poi;
      if (!poiLayer) return;

      for (let i = 0; i < poiLayer.length; i++) {
        const feat = poiLayer.feature(i);
        const props = feat.properties || {};
        // 收集所有语言的名字
        const allNameFields = {};
        // bestName 优先取德语/英语/通用 name,而非 MVT 解码顺序的第一个(可能是 name_int 等不稳定字段)
        for (const key of Object.keys(props)) {
          if (key.startsWith('name:') || key === 'name' || key === 'name_de' || key === 'name_en') {
            allNameFields[key] = props[key];
          }
        }
        // 优先级: name_de > name:de > name > name_en > name:en > 第一个非空
        const bestName = props.name_de || props['name:de'] || props.name || props.name_en || props['name:en']
          || Object.values(allNameFields).find(v => v) || '';
        if (!bestName) continue;

        const gj = feat.toGeoJSON(st.x, st.y, st.z);
        const coords = gj.geometry?.coordinates;
        if (!coords) continue;
        let lng, lat;
        if (typeof coords[0] === 'number') {
          lng = coords[0]; lat = coords[1];
        } else {
          const c = Array.isArray(coords[0][0]) ? coords[0][0] : coords[0];
          lng = c[0]; lat = c[1];
        }

        // 匹配所有语言名字(取最高分)
        let bestScore = 0;
        let scoredName = '';
        for (const name of Object.values(allNameFields)) {
          if (!name) continue;
          const s = scoreMatch(name, queryNorm);
          if (s > bestScore) { bestScore = s; scoredName = name; }
        }
        // 也用 bestName 试(兜底)
        if (bestName) {
          const s2 = scoreMatch(bestName, queryNorm);
          if (s2 > bestScore) { bestScore = s2; scoredName = bestName; }
        }
        // DEBUG: 第一个 München Hauptbahnhof 打印一下
        if (bestName === 'München Hauptbahnhof' && process.env.DEBUG_GEO) {
          console.error('DEBUG bestName=', JSON.stringify(bestName), 'queryNorm=', JSON.stringify(queryNorm));
          console.error('  allNameFields=', JSON.stringify(allNameFields));
          console.error('  bestScore=', bestScore, 'scoredName=', JSON.stringify(scoredName));
        }

        if (bestScore > 0) {
          matches.push({
            name: bestName,
            name_de: props.name_de || props['name:de'] || null,
            name_en: props.name_en || props['name:en'] || null,
            name_zh: props['name:zh'] || null,
            all_names: allNameFields,
            lat, lng,
            class: props.class || null,
            subclass: props.subclass || null,
            rank: props.rank || 999,
            score: bestScore,
          });
        }
      }
    } catch (e) {
      // skip tile errors
    }
  }));

  // 去重: 同坐标 (lat+lng) 视为同一 POI,合并多语言名字 + 取最高 score
  const seen = new Map();
  for (const m of matches) {
    const key = `${m.lat.toFixed(5)}_${m.lng.toFixed(5)}`;
    const existing = seen.get(key);
    if (!existing) {
      seen.set(key, { ...m, all_names: { ...m.all_names } });
    } else {
      // 合并多语言名字
      Object.assign(existing.all_names, m.all_names);
      if (m.score > existing.score) existing.score = m.score;
      // 填充缺失的语言名
      if (m.name_de && !existing.name_de) existing.name_de = m.name_de;
      if (m.name_en && !existing.name_en) existing.name_en = m.name_en;
      if (m.name_zh && !existing.name_zh) existing.name_zh = m.name_zh;
      // 优先用德语名作为默认显示
      if (!existing.name && m.name) existing.name = m.name;
    }
  }
  const deduped = [...seen.values()];

  // ── 排序 + 选 best ──
  // 优先级: score desc → proximity bonus (距离慕尼黑中心近优先) → rank asc → class 重要性
  const CLASS_PRIORITY = {
    'place/square': 200,
    'place/locality': 150,
    'leisure/park': 150,
    'railway/station': 100,
    'place_of_worship': 100,
    'tourism/museum': 120,
    'tourism/attraction': 80,
    'historic': 80,
    'railway/subway': 50,
    'railway/tram_stop': 30,
    'railway/halt': 20,
    'amenity': 60,
    'shop': 40,
    'building': 20,
    'entrance/subway_entrance': 5,
  };
  function classPriority(m) {
    const key = `${m.class || ''}/${m.subclass || ''}`;
    return CLASS_PRIORITY[key] || (m.class ? 10 : 0);
  }
  deduped.forEach(m => {
    m.class_priority = classPriority(m);
    m.proximity_bonus = proximityBonus(munichCenterDistKm(m.lat, m.lng));
    m.combined_score = m.score + m.proximity_bonus;
    // display_name: 德语 > 英语 > 任意
    m.display_name = m.name_de || m.name_en || m.name;
    // 中文名也带上,前端做候选用
    m.display_name_zh = m.name_zh || null;
  });
  deduped.sort((a, b) => {
    // score 主导: 高分(精确匹配)压低分(单词命中)
    // 差距 1000 vs 50 时,即使低分 class 更高,精确匹配还是优先
    if (b.score !== a.score) return b.score - a.score;
    // 同分 → class 重要性主导 (防止名字短的 subway_entrance 排前)
    if (a.class_priority !== b.class_priority) return b.class_priority - a.class_priority;
    // 同 class → 城市中心近优先
    if (b.combined_score !== a.combined_score) return b.combined_score - a.combined_score;
    return (a.rank || 999) - (b.rank || 999);
  });

  // 取 top 20
  const top = deduped.slice(0, 20);

  // best_match: 第一个 score >= 100 (有意义的匹配) 且 class 看起来像"主地标"
  // 否则取第一个非空结果
  const bestMatch = top.find(m => m.score >= 100 && classPriority(m) >= 50)
    || top.find(m => m.score > 0)
    || null;

  console.log(JSON.stringify({
    success: true,
    query: QUERY,
    query_normalized: queryNorm,
    bbox: BBOX,
    tiles_scanned: tiles.length,
    matches_found: deduped.length,
    best_match: bestMatch,
    results: top,
  }, null, 2));
}

main().catch(e => console.error(JSON.stringify({ success: false, error: e.message, stack: e.stack })));