const http = require('http');
const max = require('max-api');

const HOST = '127.0.0.1';
const PORT = 8765;
const TIMEOUT_MS = 5000;

max.addHandler('fetch', (filePath) => {
    if (!filePath || typeof filePath !== 'string') {
        max.outlet('result', JSON.stringify({
            error: 'no path provided',
            error_type: 'InputError',
        }));
        return;
    }

    const payload = JSON.stringify({ path: filePath });
    const req = http.request(
        {
            hostname: HOST,
            port: PORT,
            path: '/summary',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(payload),
            },
            timeout: TIMEOUT_MS,
        },
        (res) => {
            let body = '';
            res.on('data', (chunk) => { body += chunk; });
            res.on('end', () => {
                max.outlet('result', body);
                max.post(`c2pa_node: HTTP ${res.statusCode} for ${filePath}`);
            });
        }
    );

    req.on('timeout', () => {
        req.destroy(new Error(`request timed out after ${TIMEOUT_MS}ms`));
    });

    req.on('error', (e) => {
        max.outlet('result', JSON.stringify({
            error: `${e.message}. Is mtl-c2pa-http running on ${HOST}:${PORT}?`,
            error_type: 'NetworkError',
        }));
        max.post(`c2pa_node ERROR: ${e.message}`);
    });

    req.write(payload);
    req.end();
});

max.post(`c2pa_node.js ready, target=http://${HOST}:${PORT}`);
