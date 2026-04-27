const { exec } = require('child_process');

let transformDone = false;

function showTransformError(msg) {
  const text = document.querySelector('.loading-text');
  if (text) text.textContent = msg + ' (5초 후 시작화면으로)';
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 5000);
}

function runPython() {
  exec('python python/transform_face_ver3.py', { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
    if (error) {
      console.error('변환 오류:', error.message, stderr);
      showTransformError('이미지 변환 실패');
      return;
    }
    console.log(stdout);
    if (stdout.includes('[end]')) {
      transformDone = true;
      window.location.href = 'wait_drwaing.html';
    } else {
      const m = stdout.match(/\[error: (.+?)\]/);
      showTransformError(m ? `변환 실패: ${m[1]}` : '이미지 변환 실패');
    }
  });
}

// 30초 안에 [end] 못 받으면 안전하게 시작화면으로 복귀
setTimeout(() => {
  if (!transformDone) {
    console.warn('변환 타임아웃');
    showTransformError('이미지 변환이 너무 오래 걸립니다');
  }
}, 30000);

window.addEventListener('load', runPython);