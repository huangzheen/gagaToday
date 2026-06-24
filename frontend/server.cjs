const http = require('http');
const fs = require('fs');
const path = require('path');
const PORT = 8081;
const PUBLIC = __dirname;
const MIME = {'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.css':'text/css','.pmtiles':'application/octet-stream','.geojson':'application/json','.ico':'image/x-icon'};
function serve(req,res,fp,stat){const e=path.extname(fp),m=MIME[e]||'application/octet-stream',r=req.headers.range;if(r){const p=r.replace('bytes=','').split('-'),s=+p[0],e=p[1]?+p[1]:stat.size-1;res.writeHead(206,{'Content-Range':'bytes '+s+'-'+e+'/'+stat.size,'Accept-Ranges':'bytes','Content-Length':e-s+1,'Content-Type':m,'Access-Control-Allow-Origin':'*'});fs.createReadStream(fp,{start:s,end:e}).pipe(res)}else{res.writeHead(200,{'Content-Length':stat.size,'Content-Type':m,'Accept-Ranges':'bytes','Access-Control-Allow-Origin':'*'});fs.createReadStream(fp).pipe(res)}}
http.createServer((req,res)=>{
  let url=req.url.split('?')[0];
  let fp;
  if(url.startsWith('/assets/')){
    fp=path.join(PUBLIC,'..',url);
  }else{
    fp=path.join(PUBLIC,url);
  }
  fp=path.normalize(fp);
  fs.stat(fp,(err,stat)=>{if(err){res.writeHead(404);res.end();return}if(stat.isDirectory()){fp=path.join(fp,'index.html');return fs.stat(fp,(e2,s2)=>{if(e2){res.writeHead(404);res.end();return}serve(req,res,fp,s2)})}serve(req,res,fp,stat)})
}).listen(PORT,()=>console.log('http://127.0.0.1:'+PORT+' (Range: yes)'));
