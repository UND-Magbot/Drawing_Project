const { exec } = require('child_process');

function showDrawingError(msg) {
  const drawing = document.querySelector('.drawing');
  const sub = document.querySelector('.sub2');
  if (drawing) drawing.textContent = msg;
  if (sub) sub.textContent = '5초 후 시작화면으로 돌아갑니다';
  setTimeout(() => {
    sessionStorage.removeItem('capturedImage');
    sessionStorage.removeItem('orderNum');
    window.location.href = 'index.html';
  }, 5000);
}

function runPython() {
  exec('python python/em_mainauto.py', { maxBuffer: 1024 * 1024 * 20 }, (error, stdout, stderr) => {
    if (error) {
      console.error('그리기 오류:', error.message, stderr);
      showDrawingError('로봇 그리기 실패');
      return;
    }
    console.log(stdout);
    if (stdout.includes('[end]')) {
      console.log('그림 종료');
      const orderNum = sessionStorage.getItem('orderNum');
      if (orderNum) {
        handleVolumePreview2();
      } else {
        // 주문번호 없으면 그냥 시작화면으로
        setTimeout(() => {
          window.location.href = 'index.html';
        }, 2000);
      }
    } else {
      const m = stdout.match(/\[error: (.+?)\]/);
      showDrawingError(m ? `그리기 실패: ${m[1]}` : '로봇 그리기 실패');
    }
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
  console.log('소리끝2')
  const value = parseFloat(localStorage.getItem('appVolume'));
  previewSound.volume = value;
  console.log('소리끝')
  try {
    previewSound.currentTime = 0;
    previewSound.play();
  } catch (e) {
    console.warn('미리듣기 사운드 재생 실패:', e);
  }
  setTimeout(() => {
    const orderNum2 = sessionStorage.getItem('orderNum');
    sendFinishStatus(orderNum2);
  }, 2000);
}


async function sendFinishStatus(orderNum) {
  const url = "https://boorsue.co.kr/Admin/TOstatechangeYN.php";
  const formData = new URLSearchParams({
    ID: 'dsdc',             // ← 실제 ID
    PassWord: '12345',       // ← 실제 PW
    YNt: 'finish',
    reason: '로봇 클리어',
    zzimnum: orderNum
  });

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    const resultText = await response.text();
    if (resultText.includes("성공")) {
      console.log("주문 상태 변경 성공");
      sessionStorage.setItem('completedOrderNum', orderNum);
    } else {
      console.warn("주문 상태 변경 실패:", resultText);
    }
  } catch (error) {
    console.error("API 호출 실패:", error);
  } finally {
    // 성공/실패 상관없이 항상 시작화면으로 복귀
    sessionStorage.removeItem('capturedImage');
    sessionStorage.removeItem('orderNum');
    window.location.href = 'index.html';
  }
}

window.addEventListener('load', runPython);