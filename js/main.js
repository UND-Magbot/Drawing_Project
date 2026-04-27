const settingsBtn = document.getElementById('settings-button');
const robotPowerOnBtn = document.getElementById('robotPowerOnBtn');
const robotPowerOffBtn = document.getElementById('robotPowerOffBtn');
const modal = document.getElementById('settings-modal');
const closeBtn = document.getElementById('close-settings');
const robotMoveChangeBtn = document.getElementById('robotMoveChangeBtn');
const robotMoveHomeBtn = document.getElementById('robotMoveHomeBtn');
const volumeSlider = document.getElementById('volume-slider');
const volumeSlider2 = document.getElementById('volume-slider2');

// 전체 오디오/비디오 요소 (페이지 로딩 시 수집)
const mediaElements = document.querySelectorAll('audio, video');
const extraSounds = []; // 동적 Audio() 객체는 여기에 등록

window.addEventListener('DOMContentLoaded', () => {
    const savedVolume = localStorage.getItem('appVolume');

    if (savedVolume !== null) {
        const value = parseFloat(savedVolume);

        // 슬라이더 위치 반영
        volumeSlider.value = value;

        // 전체 볼륨 적용
        mediaElements.forEach(el => el.volume = value);
        extraSounds.forEach(el => {
            if (el) el.volume = value;
        });
    }

    const savedVolume2 = localStorage.getItem('musicVolume');

    if (savedVolume2 !== null) {
        const value = parseFloat(savedVolume2);

        // 슬라이더 위치 반영
        volumeSlider2.value = value;

        // 음악 윈도우에 IPC로만 전달 (효과음에는 영향 없음)
        try {
            const { ipcRenderer } = require('electron');
            ipcRenderer.send('volume-change', value);
        } catch (e) {
            console.warn('IPC 음악 볼륨 동기화 실패:', e);
        }
    }

});



// 설정창 열기
settingsBtn.addEventListener('click', () => {
    modal.style.display = 'flex';
});

// 설정창 닫기
closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

// 모달 외부 클릭 시 닫기
window.addEventListener('click', (e) => {
    if (e.target === modal) modal.style.display = 'none';
});


const path = require('path');
console.log(path)
// 오디오 파일의 절대 경로 생성
const soundPath = path.join(__dirname, 'assets', 'sounds', 'soundcheck.mp3');

// 브라우저에서 재생 가능한 형식으로 변환
const audioPath = `file://${soundPath.replace(/\\/g, '/')}`;  // 윈도우 경로 대응
console.log(audioPath)
const previewSound = new Audio(audioPath);
// 볼륨 슬라이더 조작
volumeSlider.addEventListener('input', function () {
    const value = parseFloat(this.value);

    // 전체 볼륨 적용
    mediaElements.forEach(el => el.volume = value);
    extraSounds.forEach(el => {
        if (el) el.volume = value;
    });

    // ✅ 저장
    localStorage.setItem('appVolume', value);


});

function handleVolumePreview() {
    const value = parseFloat(volumeSlider.value);
    previewSound.volume = value;

    try {
        previewSound.currentTime = 0;
        previewSound.play();
    } catch (e) {
        console.warn('미리듣기 사운드 재생 실패:', e);
    }

}

volumeSlider2.addEventListener('input', function () {
    const value = parseFloat(this.value);

    // 음악 윈도우에만 전달 (효과음에는 영향 없음)
    // index.html에서 이미 IPC를 보내므로 여기서는 저장만
    localStorage.setItem('musicVolume', value);


});

function handleVolumePreview2() {
    const value = parseFloat(volumeSlider2.value);
    previewSound.volume = value;

    try {
        previewSound.currentTime = 0;
        previewSound.play();
    } catch (e) {
        console.warn('미리듣기 사운드 재생 실패:', e);
    }

}

volumeSlider.addEventListener('mouseup', handleVolumePreview);
volumeSlider.addEventListener('touchend', handleVolumePreview);
volumeSlider2.addEventListener('mouseup', handleVolumePreview2);
volumeSlider2.addEventListener('touchend', handleVolumePreview2);

function setRobotPower(turnOn) {
    const isOn = robotPowerOnBtn.classList.contains('active');
    if (turnOn === isOn) return;

    if (turnOn) {
        document.getElementById('RobotloadingText').textContent = '로봇 실행중'
        document.getElementById('RobotloadingBox').style.color = 'rgb(0, 196, 0)';
        document.getElementById('Robotspinner').style.borderTop = '5px solid rgb(0, 196, 0)';
        document.getElementById('RobotloadingOverlay').style.display = 'flex';
        runPython('on');
    } else {
        document.getElementById('RobotloadingOverlay').style.display = 'flex';
        document.getElementById('RobotloadingText').textContent = '로봇 종료중'
        document.getElementById('RobotloadingBox').style.color = 'rgb(201, 64, 0)';
        document.getElementById('Robotspinner').style.borderTop = '5px solid rgb(201, 64, 0)';
        runPython('off');
    }
}

let isFirst = false;
function updatePowerButton(state) {
    if (state) {
        robotPowerOnBtn.classList.add('active');
        robotPowerOffBtn.classList.remove('active');
    } else {
        robotPowerOnBtn.classList.remove('active');
        robotPowerOffBtn.classList.add('active');
    }
    if (isFirst) {
        RobotSound(state)
        localStorage.setItem('robotPowerState', state);
        document.getElementById('RobotloadingOverlay').style.display = 'none';
    }
    else {
        isFirst = true;
    }

}


function RobotSound(state) {

    if (state) {
        const soundPath = path.join(__dirname, 'assets', 'sounds', 'RobotOn.mp3');
        // 브라우저에서 재생 가능한 형식으로 변환
        const audioPath = `file://${soundPath.replace(/\\/g, '/')}`;  // 윈도우 경로 대응
        const previewSound = new Audio(audioPath);
        const value = parseFloat(volumeSlider.value);
        console.log(value);
        previewSound.volume = value;

        try {
            previewSound.currentTime = 0;
            previewSound.play();
        } catch (e) {
            console.warn('미리듣기 사운드 재생 실패:', e);
        }
    }
    else {
        const soundPath = path.join(__dirname, 'assets', 'sounds', 'RobotOff.mp3');
        // 브라우저에서 재생 가능한 형식으로 변환
        const audioPath = `file://${soundPath.replace(/\\/g, '/')}`;  // 윈도우 경로 대응
        const previewSound = new Audio(audioPath);
        const value = parseFloat(volumeSlider.value);
        previewSound.volume = value;

        try {
            previewSound.currentTime = 0;
            previewSound.play();
        } catch (e) {
            console.warn('미리듣기 사운드 재생 실패:', e);
        }
    }

}

function setPenPosition(target) {
    const isChangeActive = robotMoveChangeBtn.classList.contains('active');
    const isHomeActive = robotMoveHomeBtn.classList.contains('active');
    if (target === 'change' && isChangeActive) return;
    if (target === 'home' && isHomeActive) return;

    if (target === 'change') {
        document.getElementById('RobotloadingText').textContent = '로봇 교체 위치로 이동중'
        document.getElementById('RobotloadingBox').style.color = 'rgb(0, 196, 0)';
        document.getElementById('Robotspinner').style.borderTop = '5px solid rgb(0, 196, 0)';
        document.getElementById('RobotloadingOverlay').style.display = 'flex';
        changePen('change');
    } else {
        document.getElementById('RobotloadingText').textContent = '로봇 홈위치로 이동중'
        document.getElementById('RobotloadingBox').style.color = 'rgb(41, 62, 252)';
        document.getElementById('Robotspinner').style.borderTop = '5px solid rgb(41, 62, 252)';
        document.getElementById('RobotloadingOverlay').style.display = 'flex';
        changePen('home');
    }
}

function updatePenButton(state) {
    if (state) {
        robotMoveChangeBtn.classList.add('active');
        robotMoveHomeBtn.classList.remove('active');
    } else {
        robotMoveChangeBtn.classList.remove('active');
        robotMoveHomeBtn.classList.add('active');
    }
    localStorage.setItem('penPositionState', state);
    document.getElementById('RobotloadingOverlay').style.display = 'none';
}

const { exec } = require('child_process');

function showRobotError(msg) {
    const overlay = document.getElementById('RobotloadingOverlay');
    const text = document.getElementById('RobotloadingText');
    const box = document.getElementById('RobotloadingBox');
    const spinner = document.getElementById('Robotspinner');
    if (text) text.textContent = msg;
    if (box) box.style.color = 'rgb(201, 64, 0)';
    if (spinner) spinner.style.borderTop = '5px solid rgb(201, 64, 0)';
    if (overlay) overlay.style.display = 'flex';
    setTimeout(() => {
        if (overlay) overlay.style.display = 'none';
    }, 3000);
}

function runPython(value) {
    const cmd = value == 'on' ? 'python python/cobot_power.py on' : 'python python/cobot_power.py off';
    const expectToken = value == 'on' ? '[power_on_ok]' : '[power_off_ok]';
    const targetState = value == 'on';
    exec(cmd, { maxBuffer: 1024 * 1024 * 5 }, (error, stdout, stderr) => {
        if (error) {
            console.error('전원 명령 오류:', error.message, stderr);
            showRobotError('로봇 응답 없음. 연결을 확인하세요.');
            return;
        }
        console.log(stdout);
        if (stdout.includes(expectToken)) {
            updatePowerButton(targetState);
        } else {
            const m = stdout.match(/\[error: (.+?)\]/);
            showRobotError(m ? `실패: ${m[1]}` : '로봇 명령 실패');
        }
    });
}

function changePen(value) {
    const cmd = value == 'change' ? 'python python/ChangePen.py change' : 'python python/ChangePen.py home';
    const targetState = value == 'change';
    exec(cmd, { maxBuffer: 1024 * 1024 * 5 }, (error, stdout, stderr) => {
        if (error) {
            console.error('펜 이동 오류:', error.message, stderr);
            showRobotError('로봇 응답 없음. 연결을 확인하세요.');
            return;
        }
        console.log(stdout);
        if (stdout.includes('[pen_ok]')) {
            updatePenButton(targetState);
        } else {
            const m = stdout.match(/\[error: (.+?)\]/);
            showRobotError(m ? `이동 실패: ${m[1]}` : '펜 이동 실패');
        }
    });
}

function SystemOff() {
    console.log("인")
    const { ipcRenderer } = require('electron');
    ipcRenderer.send('app-quit');
}




