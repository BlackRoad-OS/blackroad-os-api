const http = require('http');

const PORT = 3000;
http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('blackroad origin online\n');
}).listen(PORT, '0.0.0.0', () => {
  console.log(`listening on ${PORT}`);
});
