import os
import sys
import traceback

# Windows 콘솔(cp949)에서 비-ASCII 출력 시 UnicodeEncodeError로 죽는 것 방지
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from PIL import Image
import numpy as np
import cv2
from rembg import remove
from ultralytics import YOLO

# === 경로 설정 ===
input_path = 'C:/drawing_data/FaceImages/face.png'
output_path = 'C:/drawing_data/FaceImages/face1.png'

# 스크립트 위치 기준으로 모델 절대 경로 계산 (cwd 무관 동작)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_YOLO_MODEL_PATH = os.path.join(_PROJECT_ROOT, 'yolov8n.pt')

try:
    if not os.path.exists(_YOLO_MODEL_PATH):
        print(f"[error: YOLO 모델 파일을 찾을 수 없습니다: {_YOLO_MODEL_PATH}]")
        sys.exit(1)

    # === YOLO 모델 로드 ===
    model = YOLO(_YOLO_MODEL_PATH)

    # === 이미지 로드 및 좌우반전 ===
    image_bgr = cv2.imread(input_path)
    if image_bgr is None:
        print(f"[error: 이미지를 찾을 수 없습니다: {input_path}]")
        sys.exit(1)

    image_bgr = cv2.flip(image_bgr, 1)  # 좌우 반전
    h, w = image_bgr.shape[:2]
    image_center = np.array([w / 2, h / 2])

    # === 사람 탐지 ===
    results = model.predict(source=image_bgr, classes=[0], conf=0.4)
    boxes = results[0].boxes.xyxy.cpu().numpy()

    if len(boxes) == 0:
        print("[error: 사람이 탐지되지 않았습니다]")
        sys.exit(1)

    # === 중앙에 가장 가까운 사람 박스 선택 ===
    min_dist = float('inf')
    target_box = None
    for box in boxes:
        x1, y1, x2, y2 = box[:4]
        center = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
        dist = np.linalg.norm(center - image_center)
        if dist < min_dist:
            min_dist = dist
            target_box = [int(x1), int(y1), int(x2), int(y2)]

    x1, y1, x2, y2 = target_box

    # === rembg로 전체 배경 제거 ===
    image_pil = Image.open(input_path).convert("RGBA")
    image_pil_flipped = image_pil.transpose(Image.FLIP_LEFT_RIGHT)
    image_nobg_pil = remove(image_pil_flipped)
    image_nobg_np = np.array(image_nobg_pil)

    # === YOLO 박스 영역만 crop ===
    cropped = image_nobg_np[y1:y2, x1:x2]
    if cropped.size == 0:
        print("[error: crop 영역이 비어 있습니다]")
        sys.exit(1)

    scale_factor = 2
    cropped_resized = cv2.resize(
        cropped,
        None,
        fx=scale_factor,
        fy=scale_factor,
        interpolation=cv2.INTER_CUBIC
    )

    # === 저장 ===
    Image.fromarray(cropped_resized).save(output_path)
    print("[end]")
except SystemExit:
    raise
except Exception as e:
    traceback.print_exc()
    print(f"[error: {e}]")
    sys.exit(1)
