const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { createLifecycleMonitor } = require('./lifecycle.cjs');
const { createScreenRenderer } = require('./screen-renderer.cjs');
const { createScreenWatcher } = require('./screen-watcher.cjs');
const { computeAcceptKey, encodeFrame, decodeFrame, OPCODES } = require('./ws-protocol.cjs');

// ========== Configuration ==========

const PORT = process.env.BRAINSTORM_PORT || (49152 + Math.floor(Math.random() * 16383));
const HOST = process.env.BRAINSTORM_HOST || '127.0.0.1';
const URL_HOST = process.env.BRAINSTORM_URL_HOST || (HOST === '127.0.0.1' ? 'localhost' : HOST);
const SCREEN_DIR = process.env.BRAINSTORM_DIR || path.join(os.tmpdir(), 'brainstorm');
const OWNER_PID = process.env.BRAINSTORM_OWNER_PID ? Number(process.env.BRAINSTORM_OWNER_PID) : null;

const MIME_TYPES = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript',
  '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml'
};
const renderer = createScreenRenderer({ scriptsDir: __dirname });
const IDLE_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

function createRuntime() {
  let lastActivity = Date.now();
  return {
    clients: new Set(),
    debounceTimers: new Map(),
    touchActivity() {
      lastActivity = Date.now();
    },
    getLastActivity() {
      return lastActivity;
    }
  };
}

function handleRequest(req, res, runtime) {
  runtime.touchActivity();
  if (req.method === 'GET' && req.url === '/') {
    const html = renderer.renderCurrentScreen(SCREEN_DIR);
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(html);
    return;
  }

  if (req.method === 'GET' && req.url.startsWith('/files/')) {
    const fileName = req.url.slice(7);
    const filePath = path.join(SCREEN_DIR, path.basename(fileName));
    if (!fs.existsSync(filePath)) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(fs.readFileSync(filePath));
    return;
  }

  res.writeHead(404);
  res.end('Not found');
}

function handleMessage(text, runtime) {
  let event;
  try {
    event = JSON.parse(text);
  } catch (e) {
    console.error('Failed to parse WebSocket message:', e.message);
    return;
  }
  runtime.touchActivity();
  console.log(JSON.stringify({ source: 'user-event', ...event }));
  if (event.choice) {
    const eventsFile = path.join(SCREEN_DIR, '.events');
    fs.appendFileSync(eventsFile, JSON.stringify(event) + '\n');
  }
}

function broadcast(runtime, msg) {
  const frame = encodeFrame(OPCODES.TEXT, Buffer.from(JSON.stringify(msg)));
  for (const socket of runtime.clients) {
    try {
      socket.write(frame);
    } catch (e) {
      runtime.clients.delete(socket);
    }
  }
}

function handleUpgrade(req, socket, runtime) {
  const key = req.headers['sec-websocket-key'];
  if (!key) {
    socket.destroy();
    return;
  }

  const accept = computeAcceptKey(key);
  socket.write(
    'HTTP/1.1 101 Switching Protocols\r\n' +
    'Upgrade: websocket\r\n' +
    'Connection: Upgrade\r\n' +
    'Sec-WebSocket-Accept: ' + accept + '\r\n\r\n'
  );

  let buffer = Buffer.alloc(0);
  runtime.clients.add(socket);

  socket.on('data', (chunk) => {
    buffer = Buffer.concat([buffer, chunk]);
    while (buffer.length > 0) {
      let result;
      try {
        result = decodeFrame(buffer);
      } catch (e) {
        socket.end(encodeFrame(OPCODES.CLOSE, Buffer.alloc(0)));
        runtime.clients.delete(socket);
        return;
      }
      if (!result) break;
      buffer = buffer.slice(result.bytesConsumed);

      switch (result.opcode) {
        case OPCODES.TEXT:
          handleMessage(result.payload.toString(), runtime);
          break;
        case OPCODES.CLOSE:
          socket.end(encodeFrame(OPCODES.CLOSE, Buffer.alloc(0)));
          runtime.clients.delete(socket);
          return;
        case OPCODES.PING:
          socket.write(encodeFrame(OPCODES.PONG, result.payload));
          break;
        case OPCODES.PONG:
          break;
        default: {
          const closeBuf = Buffer.alloc(2);
          closeBuf.writeUInt16BE(1003);
          socket.end(encodeFrame(OPCODES.CLOSE, closeBuf));
          runtime.clients.delete(socket);
          return;
        }
      }
    }
  });

  socket.on('close', () => runtime.clients.delete(socket));
  socket.on('error', () => runtime.clients.delete(socket));
}

// ========== Server Startup ==========

function startServer() {
  if (!fs.existsSync(SCREEN_DIR)) fs.mkdirSync(SCREEN_DIR, { recursive: true });
  const runtime = createRuntime();

  const server = http.createServer((req, res) => handleRequest(req, res, runtime));
  server.on('upgrade', (req, socket) => handleUpgrade(req, socket, runtime));

  const watcher = createScreenWatcher({
    screenDir: SCREEN_DIR,
    debounceTimers: runtime.debounceTimers,
    touchActivity: runtime.touchActivity,
    onScreenAdded(filePath) {
      const eventsFile = path.join(SCREEN_DIR, '.events');
      if (fs.existsSync(eventsFile)) fs.unlinkSync(eventsFile);
      console.log(JSON.stringify({ type: 'screen-added', file: filePath }));
    },
    onScreenUpdated(filePath) {
      console.log(JSON.stringify({ type: 'screen-updated', file: filePath }));
    },
    onReload() {
      broadcast(runtime, { type: 'reload' });
    }
  });

  let shuttingDown = false;
  let lifecycleCheck = null;

  function shutdown(reason) {
    if (shuttingDown) return;
    shuttingDown = true;
    console.log(JSON.stringify({ type: 'server-stopped', reason }));
    const infoFile = path.join(SCREEN_DIR, '.server-info');
    if (fs.existsSync(infoFile)) fs.unlinkSync(infoFile);
    fs.writeFileSync(
      path.join(SCREEN_DIR, '.server-stopped'),
      JSON.stringify({ reason, timestamp: Date.now() }) + '\n'
    );
    watcher.close();
    if (lifecycleCheck) clearInterval(lifecycleCheck);
    server.close(() => process.exit(0));
  }

  lifecycleCheck = createLifecycleMonitor({
    ownerPid: OWNER_PID,
    idleTimeoutMs: IDLE_TIMEOUT_MS,
    getLastActivity: runtime.getLastActivity,
    onShutdown: shutdown
  });

  server.listen(PORT, HOST, () => {
    const info = JSON.stringify({
      type: 'server-started', port: Number(PORT), host: HOST,
      url_host: URL_HOST, url: 'http://' + URL_HOST + ':' + PORT,
      screen_dir: SCREEN_DIR
    });
    console.log(info);
    fs.writeFileSync(path.join(SCREEN_DIR, '.server-info'), info + '\n');
  });
}

if (require.main === module) {
  startServer();
}

module.exports = { computeAcceptKey, encodeFrame, decodeFrame, OPCODES };
