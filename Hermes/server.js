const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const PORT = 9119;
const HERMES_INTERNAL_PORT = 9120; // Hermes Python (uvicorn) fica aqui

const server = express();

// Proxy tudo — HTTP + WebSocket — para o Hermes Python
const hermesProxy = createProxyMiddleware({
  target: `http://localhost:${HERMES_INTERNAL_PORT}`,
  changeOrigin: true,
  ws: true, // habilita upgrade de WebSocket
  on: {
    error: (err, req, res) => {
      console.error('[hermes-proxy] error:', err.message);
      if (res && typeof res.status === 'function' && !res.headersSent) {
        res.status(502).json({ error: 'Hermes unavailable' });
      }
    },
  },
});

server.use('/', hermesProxy);

const httpServer = server.listen(PORT, () => {
  console.log(`[hermes-proxy] Proxying :${PORT} → :${HERMES_INTERNAL_PORT} (WS enabled)`);
});

// Necessário para o http-proxy-middleware fazer upgrade de WebSocket
httpServer.on('upgrade', hermesProxy.upgrade);
