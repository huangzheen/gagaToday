const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8081;
const PUBLIC = __dirname;

const MIME = {
  '.html':'text/html','.js':'text/javascript','.mjs':'text/javascript',
  '.json':'application/json','.png':'image/png','.svg':'image/svg+xml',
  '.css':'text/css','.pmtiles':'application/octet-stream','.geojson':'application/json',
  '.ico':'image/x-icon',
};

http.createServer((req, res) => {
  let fp = path.join(PUBLIC, req.url.split('?')[0]);
  fs.stat(fp, (err, stat) => {
    if (err) { res.writeHead(404); res.end(); return; }
    const ext = path.extname(fp);
    const mime = MIME[ext] || 'application/octet-stream';
    const range = req.headers.range;
    if (range) {
      const p = range.replace('bytes=','').split('-');
      const s = parseInt(p[0]);
      const e = p[1] ? parseInt(p[1]) : stat.size - 1;
      res.writeHead(206, {
        'Content-Range': `bytes ${s}-${e}/${stat.size}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': e - s + 1,
        'Content-Type': mime,
        'Access-Control-Allow-Origin': '*',
      });
      fs.createReadStream(fp, { start: s, end: e }).pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': stat.size,
        'Content-Type': mime,
        'Accept-Ranges': 'bytes',
        'Access-Control-Allow-Origin': '*',
      });
      fs.createReadStream(fp).pipe(res);
    }
  });
}).listen(PORT, () => console.log('http://127.0.0.1:' + PORT + ' (Range: yes)'));
