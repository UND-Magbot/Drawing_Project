const { exec } = require('child_process');
const path = require('path');
const fsMod = require('fs');

let transformDone = false;

function showTransformError(msg) {
  const text = document.querySelector('.loading-text');
  if (text) text.textContent = msg + ' (5초 후 시작화면으로)';
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 5000);
}

function runPython() {
  appendLog('transform', 'start');
  const rawRoot = path.resolve(__dirname, '..');
  const cwd = rawRoot.includes('app.asar') && !rawRoot.includes('app.asar.unpacked')
    ? rawRoot.replace('app.asar', 'app.asar.unpacked')
    : rawRoot;
  const scriptPath = path.join(cwd, 'python', 'transform_face_ver3.py');
  const env = Object.assign({}, process.env, { PYTHONIOENCODING: 'utf-8' });
  const logPath = 'C:/drawing_data/transform_debug.log';

  exec(`python "${scriptPath}"`, { cwd, env, maxBuffer: 1024 * 1024 * 50 }, (error, stdout, stderr) => {
    try {
      fsMod.mkdirSync(path.dirname(logPath), { recursive: true });
      fsMod.writeFileSync(
        logPath,
        `=== ${new Date().toISOString()} ===\ncwd: ${cwd}\nscript: ${scriptPath}\n` +
        `error: ${error ? `${error.code || ''} ${error.message}` : 'null'}\n` +
        `--- stdout ---\n${stdout || ''}\n--- stderr ---\n${stderr || ''}\n`,
        'utf-8'
      );
    } catch (_) {}

    console.log('[transform stdout]', stdout);
    if (stderr) console.log('[transform stderr]', stderr);

    if (stdout && stdout.includes('[end]')) {
      transformDone = true;
      appendLog('transform', 'end');
      window.location.href = 'wait_drwaing.html';
      return;
    }

    const haystack = `${stdout || ''}\n${stderr || ''}`;
    const m = haystack.match(/\[error: (.+?)\]/);
    let reason;
    if (m) reason = m[1];
    else if (error) reason = (error.message || '').split('\n')[0].slice(0, 120);
    else reason = '알 수 없는 오류';
    appendLog('transform', 'error', reason);
    showTransformError(`변환 실패: ${reason}`);
  });
}

// 30초 안에 [end] 못 받으면 안전하게 시작화면으로 복귀
setTimeout(() => {
  if (!transformDone) {
    console.warn('변환 타임아웃');
    appendLog('transform', 'timeout');
    showTransformError('이미지 변환이 너무 오래 걸립니다');
  }
}, 30000);

window.addEventListener('load', runPython);