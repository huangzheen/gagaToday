#!/usr/bin/env node
/**
 * OSM 数据提取器
 * 从 PMTiles 查询指定坐标的 OpenStreetMap 特征数据
 *
 * 用法: node osm_extractor.mjs <lat> <lng> [tile_url]
 * 示例: node osm_extractor.mjs 48.1385 11.5737
 *
 * tile_url 默认: http://127.0.0.1:8081/public/assets/munich_map/pmtiles/germany-zoom16.pmtiles
 */

import { PMTiles } from '/Volumes/NewDisk/GermanLearning/frontend/node_modules/pmtiles/dist/esm/index.js';
import { VectorTile } from '/Volumes/NewDisk/GermanLearning/frontend/node_modules/@mapbox/vector-tile/index.js';
import { PbfReader } from '/Volumes/NewDisk/GermanLearning/frontend/node_modules/pbf/index.js';

const TILE_URL = process.argv[4] || 'http://127.0.0.1:8081/public/assets/munich_map/pmtiles/germany-zoom16.pmtiles';
const LAT = parseFloat(process.argv[2]);
const LNG = parseFloat(process.argv[3]);

if (isNaN(LAT) || isNaN(LNG)) {
  console.error(JSON.stringify({ error: 'Usage: node osm_extractor.mjs <lat> <lng>' }));
  process.exit(1);
}

function tileXY(lat, lng, z) {
  const n = 1 << z;
  return {
    x: Math.floor((lng + 180) / 360 * n),
    y: Math.floor((1 - Math.log(Math.tan(lat * Math.PI / 180) + 1 / Math.cos(lat * Math.PI / 180)) / Math.PI) / 2 * n),
  };
}

function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function tileCenter(tx, ty, z) {
  const n = 1 << z;
  const lng = tx / n * 360 - 180;
  const lat = Math.atan(Math.sinh(Math.PI * (1 - 2 * ty / n))) * 180 / Math.PI;
  return { lat, lng };
}

async function main() {
  const p = new PMTiles(TILE_URL);
  await p.getHeader();

  const centerTile = tileXY(LAT, LNG, 16);
  const results = [];

  // 搜索 5x5 瓦片网格
  for (let dx = -2; dx <= 2; dx++) {
    for (let dy = -2; dy <= 2; dy++) {
      const st = { z: 16, x: centerTile.x + dx, y: centerTile.y + dy };
      if (st.x < 0 || st.y < 0) continue;
      try {
        const r = await p.getZxy(st.z, st.x, st.y);
        if (!r || !r.data) continue;
        const vt = new VectorTile(new PbfReader(r.data));

        for (const layerName of Object.keys(vt.layers)) {
          const layer = vt.layers[layerName];
          for (let i = 0; i < layer.length; i++) {
            try {
              const feat = layer.feature(i);
              const props = feat.properties || {};
              const gj = feat.toGeoJSON(st.x, st.y, st.z);
              const coords = gj.geometry?.coordinates;

              // 计算中心距离
              let dist = null;
              if (coords && coords.length) {
                const first = coords[0];
                // Point: [lng, lat] → first is a number
                // Polygon/MultiPoint: [[lng,lat], ...] → first is an array
                let pt;
                if (typeof first === 'number') {
                  pt = coords; // Point: coords = [lng, lat]
                } else if (Array.isArray(first)) {
                  const c2 = Array.isArray(first[0]) ? first[0] : first;
                  pt = c2;
                } else {
                  pt = first;
                }
                if (pt.length >= 2) {
                  dist = haversineKm(LAT, LNG, pt[1], pt[0]) * 1000;
                }
              } else {
                const tc = tileCenter(st.x, st.y, st.z);
                dist = haversineKm(LAT, LNG, tc.lat, tc.lng) * 1000;
              }

              results.push({
                layer: layerName,
                properties: props,
                distance_m: Math.round(dist),
                tile: `z${st.z}/${st.x}/${st.y}`,
              });
            } catch (e) {
              // skip feature errors
            }
          }
        }
      } catch (e) {
        // skip tile errors
      }
    }
  }

  // ── 整理输出 ──

  // 1. 找到距离最近的 POI 作为"主 POI"
  const pois = results
    .filter(r => r.layer === 'poi' && r.distance_m < 300)
    .sort((a, b) => a.distance_m - b.distance_m);

  // 2. 找到最近的 building
  const buildings = results
    .filter(r => r.layer === 'building' && r.distance_m < 200)
    .sort((a, b) => a.distance_m - b.distance_m);

  // 3. 地址信息
  const housenumbers = results
    .filter(r => r.layer === 'housenumber' && r.distance_m < 100)
    .sort((a, b) => a.distance_m - b.distance_m);

  // 4. 交通信息
  const transport = results
    .filter(r => (r.layer === 'poi' || r.layer === 'transportation_name') &&
      r.properties?.class === 'railway' && r.distance_m < 500)
    .sort((a, b) => a.distance_m - b.distance_m);

  // 5. 周边的 POI（rank < 100，排除主 POI）
  const nearbyPois = results
    .filter(r => r.layer === 'poi' && r.distance_m < 400 && r.distance_m > 20)
    .sort((a, b) => (a.properties?.rank || 999) - (b.properties?.rank || 999))
    .slice(0, 20);

  // 6. 道路名称
  const roads = results
    .filter(r => r.layer === 'transportation_name' && r.distance_m < 200)
    .sort((a, b) => a.distance_m - b.distance_m);

  // ── 提取多语言名称 ──
  const primary = pois[0]?.properties || {};
  const nameFields = {};
  for (const key of Object.keys(primary)) {
    if (key.startsWith('name:') || key === 'name' || key === 'name_de' || key === 'name_en') {
      nameFields[key] = primary[key];
    }
  }

  console.log(JSON.stringify({
    success: true,
    lat: LAT,
    lng: LNG,
    primary_poi: pois[0] ? {
      name: primary.name || null,
      name_de: primary.name_de || primary.name || null,
      name_zh: primary['name:zh'] || null,
      name_en: primary.name_en || null,
      all_names: nameFields,
      class: primary.class || null,
      subclass: primary.subclass || null,
      rank: primary.rank || null,
      distance_m: pois[0].distance_m,
    } : null,
    building: buildings[0] ? {
      render_height: buildings[0].properties.render_height || null,
      render_min_height: buildings[0].properties.render_min_height || null,
      colour: buildings[0].properties.colour || null,
      distance_m: buildings[0].distance_m,
    } : null,
    address: housenumbers.map(h => ({
      housenumber: h.properties.housenumber,
      distance_m: h.distance_m,
    })),
    transport: transport.slice(0, 8).map(t => ({
      name: t.properties.name || t.properties.name_de || null,
      class: t.properties.subclass || t.properties.class || null,
      distance_m: t.distance_m,
    })),
    roads: roads.slice(0, 6).map(r => ({
      name: r.properties.name || null,
      name_de: r.properties.name_de || null,
      class: r.properties.subclass || null,
      distance_m: r.distance_m,
    })),
    nearby_pois: nearbyPois.map(p => ({
      name: p.properties.name || p.properties.name_de || null,
      class: p.properties.class || null,
      subclass: p.properties.subclass || null,
      rank: p.properties.rank || null,
      distance_m: p.distance_m,
    })),
    all_layers: [...new Set(results.map(r => r.layer))],
    total_features: results.length,
  }));
}

main().catch(e => console.error(JSON.stringify({ error: e.message })));
