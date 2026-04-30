// review: skip-failure-path
// review: allow-human-readable-output
const fs = require('fs');
const path = require('path');

function createScreenWatcher({
  screenDir,
  debounceTimers,
  touchActivity,
  onScreenAdded,
  onScreenUpdated,
  onReload,
  logger = console
}) {
  // Track known files to distinguish new screens from updates.
  // macOS fs.watch reports 'rename' for both new files and overwrites,
  // so we can't rely on eventType alone.
  const knownFiles = new Set(
    fs.readdirSync(screenDir).filter((fileName) => fileName.endsWith('.html'))
  );

  const watcher = fs.watch(screenDir, (eventType, filename) => {
    if (!filename || !filename.endsWith('.html')) return;

    if (debounceTimers.has(filename)) clearTimeout(debounceTimers.get(filename));
    debounceTimers.set(filename, setTimeout(() => {
      debounceTimers.delete(filename);
      const filePath = path.join(screenDir, filename);

      if (!fs.existsSync(filePath)) return;
      touchActivity();

      if (!knownFiles.has(filename)) {
        knownFiles.add(filename);
        onScreenAdded(filePath);
      } else {
        onScreenUpdated(filePath);
      }

      onReload();
    }, 100));
  });

  watcher.on('error', (err) => logger.error('fs.watch error:', err.message));
  return watcher;
}

module.exports = { createScreenWatcher };
