const { exec } = require('child_process');

function showDrawingError(msg) {
  const drawing = document.querySelector('.drawing');
  const sub = document.querySelector('.sub2');
  if (drawing) drawing.textContent = msg;
  if (sub) sub.textContent = '5초 후 시작화면으로 돌아갑니다';
  setTimeout(() => {
    sessionStorage.removeItem('capturedImage');
    window.location.href = 'index.html';
  }, 5000);
}

function runPython() {
  appendLog('drawing', 'start');
  const pathMod = require('path');
  const fsMod = require('fs');
  const rawRoot = pathMod.resolve(__dirname, '..');
  const cwd = rawRoot.includes('app.asar') && !rawRoot.includes('app.asar.unpacked')
    ? rawRoot.replace('app.asar', 'app.asar.unpacked')
    : rawRoot;
  const scriptPath = pathMod.join(cwd, 'python', 'em_mainauto.py');
  const env = Object.assign({}, process.env, { PYTHONIOENCODING: 'utf-8' });
  const logPath = 'C:/drawing_data/drawing_debug.log';

  exec(`python "${scriptPath}"`, { cwd, env, maxBuffer: 1024 * 1024 * 50 }, (error, stdout, stderr) => {
    try {
      fsMod.mkdirSync(pathMod.dirname(logPath), { recursive: true });
      fsMod.writeFileSync(
        logPath,
        `=== ${new Date().toISOString()} ===\ncwd: ${cwd}\nscript: ${scriptPath}\n` +
        `error: ${error ? `${error.code || ''} ${error.message}` : 'null'}\n` +
        `--- stdout ---\n${stdout || ''}\n--- stderr ---\n${stderr || ''}\n`,
        'utf-8'
      );
    } catch (_) {}

    console.log('[drawing stdout]', stdout);
    if (stderr) console.log('[drawing stderr]', stderr);

    if (stdout && stdout.includes('[end]')) {
      console.log('그림 종료');
      appendLog('drawing', 'end');
      handleVolumePreview2();
      return;
    }

    const haystack = `${stdout || ''}\n${stderr || ''}`;
    const m = haystack.match(/\[error: (.+?)\]/);
    let reason;
    if (m) reason = m[1];
    else if (error) reason = (error.message || '').split('\n')[0].slice(0, 120);
    else reason = '알 수 없는 오류';
    appendLog('drawing', 'error', reason);
    showDrawingError(`그리기 실패: ${reason}`);
  });
}

const path = require('path');
console.log(path)
// 오디오 파일의 절대 경로 생성
const soundPath = path.join(__dirname, 'assets', 'sounds', 'DraingEnd.mp3');

// 브라우저에서 재생 가능한 형식으로 변환
const audioPath = `file://${soundPath.replace(/\\/g, '/')}`;  // 윈도우 경로 대응
const previewSound = new Audio(audioPath);

function handleVolumePreview2() {
  const saved = parseFloat(persistentStorage.getItem('appVolume'));
  const value = isFinite(saved) ? Math.max(0, Math.min(1, saved)) : 0.5;
  previewSound.volume = value;
  try {
    previewSound.currentTime = 0;
    previewSound.play();
  } catch (e) {
    console.warn('미리듣기 사운드 재생 실패:', e);
  }
  setTimeout(() => {
    sessionStorage.removeItem('capturedImage');
    window.location.href = 'index.html';
  }, 3000);
}

window.addEventListener('load', runPython);