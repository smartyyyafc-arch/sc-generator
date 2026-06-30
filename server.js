#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = 3000;
const DOWNLOADS_DIR = path.join(__dirname, 'downloads');

// Ensure downloads directory exists
if (!fs.existsSync(DOWNLOADS_DIR)) {
  fs.mkdirSync(DOWNLOADS_DIR, { recursive: true });
}

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // Root path - serve download test page
  if (pathname === '/' || pathname === '/index.html') {
    const htmlContent = fs.readFileSync(path.join(__dirname, 'download-test.html'), 'utf8');
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(htmlContent);
    return;
  }

  // Download VBS files
  if (pathname.startsWith('/download/')) {
    const filename = pathname.replace('/download/', '');
    const filepath = path.join(__dirname, filename);

    // Security check: prevent directory traversal
    if (!filepath.startsWith(__dirname)) {
      res.writeHead(403, { 'Content-Type': 'text/plain' });
      res.end('Access denied');
      return;
    }

    // Check if file exists
    if (!fs.existsSync(filepath)) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('File not found');
      return;
    }

    // Determine MIME type based on file extension
    const ext = path.extname(filepath).toLowerCase();
    let contentType = 'application/octet-stream';
    let shouldDownload = true;

    if (ext === '.vbs') {
      contentType = 'text/vbscript'; // Standard MIME type for VBS
      shouldDownload = true;
    } else if (ext === '.hta') {
      contentType = 'application/x-mshta'; // MIME type for HTA
      shouldDownload = true;
    } else if (ext === '.html') {
      contentType = 'text/html';
      shouldDownload = false;
    }

    // Set headers for download
    const fileSize = fs.statSync(filepath).size;
    const headers = {
      'Content-Type': contentType,
      'Content-Length': fileSize,
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    };

    // Force download behavior for executable files
    if (shouldDownload) {
      headers['Content-Disposition'] = `attachment; filename="${path.basename(filepath)}"`;
    }

    try {
      res.writeHead(200, headers);
      const stream = fs.createReadStream(filepath);
      stream.pipe(res);
      stream.on('error', (err) => {
        console.error('Stream error:', err);
        res.writeHead(500);
        res.end('Internal server error');
      });
    } catch (err) {
      console.error('Download error:', err);
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Download failed');
    }
    return;
  }

  // API endpoint to list available files
  if (pathname === '/api/files') {
    try {
      const files = fs.readdirSync(__dirname).filter(f =>
        f.endsWith('.vbs') || f.endsWith('.hta')
      );

      const fileList = files.map(f => {
        const filepath = path.join(__dirname, f);
        const stats = fs.statSync(filepath);
        return {
          name: f,
          size: stats.size,
          type: path.extname(f).toLowerCase(),
          url: `/download/${f}`
        };
      });

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(fileList, null, 2));
    } catch (err) {
      console.error('API error:', err);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  // Serve static files from public directory
  const publicPath = path.join(__dirname, 'public', pathname);
  if (fs.existsSync(publicPath) && fs.statSync(publicPath).isFile()) {
    const ext = path.extname(publicPath).toLowerCase();
    const contentTypes = {
      '.html': 'text/html',
      '.css': 'text/css',
      '.js': 'application/javascript',
      '.json': 'application/json',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.gif': 'image/gif',
      '.svg': 'image/svg+xml'
    };
    const contentType = contentTypes[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(fs.readFileSync(publicPath));
    return;
  }

  // 404
  res.writeHead(404, { 'Content-Type': 'text/plain' });
  res.end('Not found');
});

server.listen(PORT, 'localhost', () => {
  console.log(`Server running at http://localhost:${PORT}/`);
  console.log(`Download test page: http://localhost:${PORT}/index.html`);
  console.log(`File list API: http://localhost:${PORT}/api/files`);
});
