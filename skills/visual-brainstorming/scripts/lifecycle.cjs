// review: skip-failure-path
// review: allow-human-readable-output
function ownerAlive(ownerPid) {
  if (!ownerPid) return true;
  try {
    process.kill(ownerPid, 0);
    return true;
  } catch (e) {
    return false;
  }
}

function createLifecycleMonitor({
  ownerPid,
  idleTimeoutMs,
  getLastActivity,
  onShutdown,
  intervalMs = 60 * 1000
}) {
  const timer = setInterval(() => {
    if (!ownerAlive(ownerPid)) {
      onShutdown('owner process exited');
    } else if (Date.now() - getLastActivity() > idleTimeoutMs) {
      onShutdown('idle timeout');
    }
  }, intervalMs);

  timer.unref();
  return timer;
}

module.exports = { createLifecycleMonitor, ownerAlive };
