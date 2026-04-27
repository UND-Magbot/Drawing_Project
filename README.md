# 얼굴 그려주는 로봇 (Drawing Robot)

카메라로 사용자의 얼굴을 촬영하면, 협동로봇(코봇)이 종이에 얼굴을 그려주는 키오스크형 데스크톱 애플리케이션입니다.

Electron 기반 프론트엔드(키오스크 UI)와 Python 기반 영상처리/로봇 제어 백엔드로 구성되어 있습니다.

---

## 주요 기능

- **얼굴 촬영**: 웹캠으로 얼굴 사진을 촬영 (5초 카운트다운)
- **배경 제거 & 외곽선 추출**: `rembg`로 배경 제거 후 OpenCV Canny + Skeletonization으로 펜 경로 좌표 생성
- **얼굴 랜드마크 보정**: MediaPipe FaceMesh로 얼굴 영역 정렬
- **로봇 제어**: 협동로봇(NRMK 코봇) TCP 제어로 종이 위에 그림 그리기
- **키오스크 UI**: 시작 → 안내 → 촬영 → 변환 미리보기 → 그리기 대기 화면 흐름
- **배경 음악/효과음**: 숨김 BrowserWindow에서 BGM 재생, 볼륨 조절 가능
- **설정 패널**: 로봇 전원 ON/OFF, 펜 교체 위치 이동, 볼륨, 시스템 종료

---

## 폴더 구조

```
Drawing/
├── index.js                  # Electron 메인 프로세스 진입점
├── package.json              # Electron / electron-builder 설정
├── icon.ico                  # 앱 아이콘
│
├── html/                     # 키오스크 화면 (페이지 단위)
│   ├── index.html            # 시작 화면
│   ├── camera_ready.html     # 촬영 안내
│   ├── camera_shot.html      # 카메라 촬영(5초 타이머)
│   ├── select_img.html       # 사진 선택
│   ├── image_transform.html  # 변환 미리보기
│   ├── paper_info.html       # 종이 안내
│   ├── wait_drwaing.html     # 그리기 진행 화면
│   └── music-player.html     # 백그라운드 BGM 플레이어
│
├── css/style.css             # 전체 스타일
│
├── js/                       # 렌더러 프로세스 스크립트
│   ├── main.js               # 설정 모달, 볼륨, 로봇 전원 제어
│   ├── camera.js             # 카메라 캡처 로직
│   ├── save_img.js           # 촬영 이미지 저장
│   ├── transform_image.js    # Python 변환 호출
│   └── Drawing_image.js      # 로봇 그리기 트리거
│
├── python/                   # 영상처리 + 로봇 제어
│   ├── em_main.py            # PyQt5 메인(테스트/디버그용)
│   ├── em_mainauto.py        # 자동 실행 메인
│   ├── cobot.py              # 코봇 통신 라이브러리(NRMK)
│   ├── cobot_power.py        # 전원 제어
│   ├── ChangePen.py          # 펜 교체 위치 이동
│   ├── remove_bg.py          # rembg 배경 제거
│   ├── transform_face_ver1.py
│   ├── transform_face_ver2.py
│   └── transform_face_ver3.py  # 최신 변환 파이프라인 (MediaPipe + Canny + Skeleton)
│
├── images/                   # UI 이미지 리소스
├── MusicFolder/              # BGM 파일(mp3)
├── drawing_data/FaceImages/  # 촬영/처리 이미지 저장 위치(런타임)
└── UsersZoeyDrawing/         # 사용자 결과 보관 위치
```

---

## 동작 흐름

```
[index.html] 시작하기 클릭
    ↓
[camera_ready.html] 촬영 안내
    ↓
[camera_shot.html] 5초 카운트다운 후 사진 촬영
    ↓ (face.png 저장)
[select_img.html] 사진 확인
    ↓
[image_transform.html] Python 호출 → 배경 제거 + 외곽선 추출
    ↓ (points.txt 좌표 파일 생성)
[paper_info.html] 종이 세팅 안내
    ↓
[wait_drwaing.html] 코봇이 좌표대로 그리기 시작
    ↓
완료 후 처음 화면으로 복귀
```

좌표 파일은 `C:/drawing_data/points.txt` 에 `x, y, z, rx, ry, rz` 형식으로 저장되어 코봇이 읽어들입니다.

---

## 요구 사항

### 공통
- Windows 10 / 11
- 웹캠 (USB 카메라 권장)

### 프론트엔드 (Electron)
- Node.js 18 이상
- npm

### 백엔드 (Python)
- Python 3.9 이상
- 주요 패키지:
  - `opencv-python`
  - `numpy`
  - `Pillow`
  - `rembg`
  - `mediapipe`
  - `PyQt5`
  - `multipledispatch`

```bash
pip install opencv-python numpy Pillow rembg mediapipe PyQt5 multipledispatch
```

### 로봇
- NRMK 협동로봇 (코봇)
- 기본 IP: `10.0.2.7` (코드 내 변경 가능)

---

## 설치 및 실행

### 1) 의존성 설치
```bash
npm install
```

### 2) 개발 모드 실행
```bash
npm start
```
풀스크린 키오스크 모드로 실행됩니다.

### 3) 윈도우 인스톨러 빌드
```bash
npm run dist
```
`dist/얼굴그리기로봇 Setup 1.0.0.exe` 가 생성됩니다.

---

## 설정 단축 동작

- 우측 상단 톱니바퀴 아이콘으로 설정 모달 열기
  - 효과음/노래 볼륨 슬라이더
  - 로봇 전원 ON / OFF
  - 펜 교체 / 홈 위치 이동
  - 시스템 종료

---

## 좌표 변환 파라미터

`python/transform_face_ver3.py` 에서 종이 영역에 매핑되는 좌표 범위를 설정합니다.

```python
X_MIN, X_MAX = 530, 665
Y_MIN, Y_MAX = 350, 530
```

펜 높이(Z 값)는 그리기 시 라인 시작/중간/끝마다 다른 값을 사용해 펜을 들어올리고 내립니다.

---

## 알려진 주의 사항

- 카메라 권한이 차단되면 시작 버튼이 비활성화됩니다.
- `drawing_data/FaceImages/` 경로가 없으면 변환 단계에서 오류가 발생할 수 있어, 최초 실행 전 자동으로 생성됩니다.
- 코봇 IP가 다를 경우 `python/em_main.py`, `python/cobot_power.py` 등에서 `10.0.2.7` 부분을 수정해야 합니다.

---

## 라이선스

ISC

## 작성자

UND-Magbot
