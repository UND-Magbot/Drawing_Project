(function () {
  const fs = require('fs');
  const path = require('path');

  const LOG_DIR = 'C:/drawing_data/logs';

  function appendLog(stage, event, detail) {
    try {
      fs.mkdirSync(LOG_DIR, { recursive: true });
      const now = new Date();
      const pad = (n) => String(n).padStart(2, '0');
      const date = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
      const time = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
      const line = `[${date} ${time}] [${stage}] [${event}]${detail ? ' ' + detail : ''}\n`;
      fs.appendFileSync(path.join(LOG_DIR, `${date}.log`), line, 'utf-8');
    } catch (e) {
      console.warn('로그 저장 실패:', e);
    }
  }

  window.appendLog = appendLog;
})();
