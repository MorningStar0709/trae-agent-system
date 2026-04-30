// review: skip-failure-path
// review: allow-human-readable-output
const fs = require('fs');
const path = require('path');

const WAITING_PAGE = `<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Brainstorm Companion</title>
<style>body { font-family: system-ui, sans-serif; padding: 2rem; max-width: 800px; margin: 0 auto; }
h1 { color: #333; } p { color: #666; }</style>
</head>
<body><h1>Brainstorm Companion</h1>
<p>Waiting for the agent to push a screen...</p></body></html>`;

function isFullDocument(html) {
  const trimmed = html.trimStart().toLowerCase();
  return trimmed.startsWith('<!doctype') || trimmed.startsWith('<html');
}

function createScreenRenderer({ scriptsDir }) {
  const frameTemplate = fs.readFileSync(path.join(scriptsDir, 'frame-template.html'), 'utf-8');
  const helperScript = fs.readFileSync(path.join(scriptsDir, 'helper.js'), 'utf-8');
  const helperInjection = '<script>\n' + helperScript + '\n</script>';

  function wrapInFrame(content) {
    return frameTemplate.replace('<!-- CONTENT -->', content);
  }

  function getNewestScreen(screenDir) {
    const files = fs.readdirSync(screenDir)
      .filter((fileName) => fileName.endsWith('.html'))
      .map((fileName) => {
        const filePath = path.join(screenDir, fileName);
        return { path: filePath, mtime: fs.statSync(filePath).mtime.getTime() };
      })
      .sort((a, b) => b.mtime - a.mtime);
    return files.length > 0 ? files[0].path : null;
  }

  function renderCurrentScreen(screenDir) {
    const screenFile = getNewestScreen(screenDir);
    let html = screenFile
      ? fs.readFileSync(screenFile, 'utf-8')
      : WAITING_PAGE;

    if (!isFullDocument(html)) {
      html = wrapInFrame(html);
    }

    if (html.includes('</body>')) {
      return html.replace('</body>', helperInjection + '\n</body>');
    }
    return html + helperInjection;
  }

  return { renderCurrentScreen };
}

module.exports = { createScreenRenderer, isFullDocument, WAITING_PAGE };
