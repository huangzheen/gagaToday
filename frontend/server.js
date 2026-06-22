const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8081;
const PUBLIC = path.join(__dirname, '.');

const MIME = {
  '.html':'text/html','.js':'text/javascript','.mjs':'text/javascript',
  '.json':'application/json','.png':'image/png','.svg':'image/svg+xml',
  '.css':'text/css','.pmtiles':'application/octet-stream','.geojson':'application/json',
};

http.createServer((req, res) => {
  let filePath = path.join(PUBLIC, req.url.split('?')[0]);
  // Handle symlinks properly
  let realPath = fs.realpathSync.native(filePath);
  
  fs.stat(realPath, (err, stat) => {
    if (err) { res.writeHead(404); res.end('Not Found'); return; }
    
    const ext = path.extname(realPath);
    const mime = MIME[ext] || 'application/octet-stream';
    const fileSize = stat.size;
    
    // Handle Range requests (needed for PMTiles)
    const range = req.headers.range;
    if (range) {
      const parts = range.replace('bytes=', '').split('-');
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
      const chunkSize = end - start + 1;
      
      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${fileSize}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunkSize,
        'Content-Type': mime,
        'Access-Control-Allow-Origin': '*',
      });
      
      const stream = fs.createReadStream(realPath, { start, end });
      stream.pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': fileSize,
        'Content-Type': mime,
        'Accept-Ranges': 'bytes',
        'Access-Control-Allow-Origin': '*',
      });
      fs.createReadStream(realPath).pipe(res);
    }
  });
}).listen(PORT, () => {
  console.log(`Server on http://127.0.0.1:${PORT} (Range support: yes)`);
});
