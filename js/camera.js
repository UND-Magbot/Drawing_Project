async function startCamera() {
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(device => device.kind === 'videoinput');

    if (videoDevices.length === 0) {
      console.error("사용 가능한 카메라가 없습니다.");
      showCameraError("카메라를 찾을 수 없습니다. 연결을 확인해주세요.");
      return;
    }

    const targetDeviceId = videoDevices[0].deviceId; // 0번 카메라

    const constraints = {
      video: {
        deviceId: { exact: targetDeviceId }
      }
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    const video = document.getElementById('camera');
    video.srcObject = stream;

    // 비디오 로딩 완료 후 5초 타이머 시작
    let snapshotTaken = false;
    video.onloadedmetadata = () => {
      setTimeout(() => {
        if (!snapshotTaken) {
          snapshotTaken = true;
          takeSnapshot(video);
        }
      }, 5000);
    };

  } catch (err) {
    console.error("카메라 오류:", err);
    showCameraError("카메라 접근에 실패했습니다. 권한을 확인해주세요.");
  }
}

function showCameraError(msg) {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) {
    overlay.style.display = 'flex';
    const text = overlay.querySelector('.loadingText');
    if (text) text.textContent = msg + ' (5초 후 시작화면으로 돌아갑니다)';
  }
  setTimeout(() => {
    window.location.href = 'index.html';
  }, 5000);
}

function takeSnapshot(video) {
  document.getElementById('loadingOverlay').style.display = 'flex';
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;

  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);



  // 3. 이미지 저장
  const imageURL = canvas.toDataURL('image/png');
  sessionStorage.setItem('capturedImage', imageURL);

  const fs = require('fs');
  const path = require('path');

  // 저장할 디렉토리
  const saveDir = path.join('C:/drawing_data', 'FaceImages');
  if (!fs.existsSync(saveDir)) {
    fs.mkdirSync(saveDir, { recursive: true });
  }

  // sessionStorage에서 이미지 가져오기
  const base64Url = sessionStorage.getItem('capturedImage'); // data:image/png;base64,...

  if (!base64Url || !base64Url.startsWith('data:image')) {
    alert("올바른 이미지 데이터가 없습니다.");
    throw new Error("base64 이미지 형식이 잘못되었습니다.");
  }

  // 확장자 추출 (png, jpeg 등)
  const extMatch = base64Url.match(/^data:image\/(png|jpeg|jpg);base64,/);
  const extension = extMatch ? extMatch[1] : 'png'; // 기본은 png

  // base64 데이터만 추출
  const base64Data = base64Url.split(',')[1];

  // 파일명 생성
  const now = new Date();
  const pad = (n) => n.toString().padStart(2, '0');
  const fileName = `face.${extension}`;

  const savePath = path.join(saveDir, fileName);

  // 파일 저장
  fs.writeFile(savePath, base64Data, { encoding: 'base64' }, (err) => {
    if (err) {
      console.error("이미지 저장 실패:", err);
      // alert("이미지 저장 중 오류 발생!");
    } else {
      console.log("이미지 저장 성공:", savePath);
      // alert("이미지가 정상 저장되었습니다.");
      runPython();
    }
  });

}


function generateFilename() {
  const now = new Date();
  const pad = (n) => n.toString().padStart(2, '0');

  const year = now.getFullYear();
  const month = pad(now.getMonth() + 1);
  const day = pad(now.getDate());
  const hour = pad(now.getHours());
  const minute = pad(now.getMinutes());
  const second = pad(now.getSeconds());

  return `snapshot_${year}-${month}-${day}_${hour}-${minute}-${second}.png`;
}

window.addEventListener('load', startCamera);


const { exec } = require('child_process');

function runPython() {
  exec('python python/remove_bg.py', { maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
    const overlay = document.getElementById('loadingOverlay');
    if (error) {
      console.error('remove_bg 오류:', error.message, stderr);
      showCameraError('이미지 처리 실패. 다시 촬영해주세요.');
      return;
    }
    console.log(stdout);
    if (stdout.includes('[end]')) {
      console.log('저장완료');
      if (overlay) overlay.style.display = 'none';
      window.location.href = '../html/select_img.html';
    } else {
      const m = stdout.match(/\[error: (.+?)\]/);
      showCameraError(m ? `처리 실패: ${m[1]}` : '이미지 처리 실패');
    }
  });
}
