import os
import sys
import traceback

# Windows 콘솔(cp949)에서 비-ASCII 출력 시 UnicodeEncodeError가 나서
# 호출 측(JS exec)이 변환 실패로 오인하는 문제 방지.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import cv2
import numpy as np
from PIL import Image
from rembg import remove
import mediapipe as mp

# === 경로 설정 ===
image_path = r"C:/drawing_data/FaceImages/face1.png"
output_img_path = r"C:/drawing_data/FaceImages/combined_output.png"
output_txt_path = r"C:/drawing_data/points.txt"

# === 좌표 변환 범위 설정 ===
X_MIN, X_MAX = 530, 665
Y_MIN, Y_MAX = 350, 530

# === Skeletonization 함수 ===
def skeletonize(image):
    skel = np.zeros(image.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        open_img = cv2.morphologyEx(image, cv2.MORPH_OPEN, element)
        temp = cv2.subtract(image, open_img)
        eroded = cv2.erode(image, element)
        skel = cv2.bitwise_or(skel, temp)
        image[:] = eroded[:]
        if cv2.countNonZero(image) == 0:
            break
    return skel

try:
    # 이전 결과 파일을 미리 삭제해 stale 데이터 사용 방지
    if os.path.exists(output_txt_path):
        try:
            os.remove(output_txt_path)
        except OSError:
            pass

    if not os.path.exists(image_path):
        print(f"[error: 입력 이미지를 찾을 수 없습니다: {image_path}]")
        sys.exit(1)

    # === 이미지 로드 및 rembg ===
    input_image = Image.open(image_path)
    output_image = remove(input_image)
    image_np = np.array(output_image)
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR if image_np.shape[2] == 4 else cv2.COLOR_RGB2BGR)
    annotated_image = image_cv.copy()

    # === 윤곽선 검출 ===
    blurred = cv2.bilateralFilter(image_cv, 9, 3, 3)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edges_skeleton = skeletonize(edges)
    contours, _ = cv2.findContours(edges_skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 윤곽선 경계
    valid_contours = [c.reshape(-1, 2) for c in contours if len(c) > 0]
    if not valid_contours:
        print("[error: 윤곽선이 검출되지 않았습니다]")
        sys.exit(1)
    all_points = np.vstack(valid_contours)
    x_min_img, y_min_img = np.min(all_points, axis=0)
    x_max_img, y_max_img = np.max(all_points, axis=0)
    if x_max_img == x_min_img or y_max_img == y_min_img:
        print("[error: 윤곽선 경계가 0입니다]")
        sys.exit(1)

    # 스케일링 계산
    scale_x = (X_MAX - X_MIN) / (x_max_img - x_min_img)
    scale_y = (Y_MAX - Y_MIN) / (y_max_img - y_min_img)
    uniform_scale = min(scale_x, scale_y)

    def normalize_point(x, y):
        center_x = (x_min_img + x_max_img) / 2
        center_y = (y_min_img + y_max_img) / 2
        new_x = (x - center_x) * uniform_scale + (X_MIN + X_MAX) / 2
        new_y = (y - center_y) * uniform_scale + (Y_MIN + Y_MAX) / 2
        return round(new_x, 2), round(new_y, 2)

    # === MediaPipe 얼굴 landmark ===
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
    image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)
    height, width, _ = image_cv.shape

    FACE_OUTLINE = [251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378,
                    400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93,
                    234, 127, 162, 21, 54]
    LIPS_OUTLINE = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308,
                    324, 318, 402, 317, 14, 87, 178, 88, 95, 61]
    LIPS_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 78]
    LEFT_EYE = [33, 160, 158, 133, 153, 144, 145, 153, 154, 155, 133]
    RIGHT_EYE = [362, 385, 387, 263, 373, 380, 381, 382, 362]
    NOSE_CURVE = [6, 197, 195, 5, 4, 1, 2, 97, 98, 327, 326, 2, 1]

    landmark_groups = {
        "face_outline": FACE_OUTLINE,
        "left_eye": LEFT_EYE,
        "right_eye": RIGHT_EYE,
        "nose_curve": NOSE_CURVE,
        "lips_outer": LIPS_OUTLINE,
        "lips_inner": LIPS_INNER
    }

    txt_lines = []
    txt_lines.append("660, 450, 250, 90.03, 0.35, -86.91")

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for group_name, indices in landmark_groups.items():
                points = []
                for idx in indices:
                    x = int(face_landmarks.landmark[idx].x * width)
                    y = int(face_landmarks.landmark[idx].y * height)
                    nx, ny = normalize_point(x, y)
                    points.append((int(nx), int(ny)))
                    if ny < 440:
                        txt_lines.append(f"{nx}, {ny}, 156, 90.03, 0.35, -86.91")
                    else:
                        txt_lines.append(f"{nx}, {ny}, 155.5, 90.03, 0.35, -86.91")
                if group_name == "nose_curve":
                    cv2.polylines(annotated_image, [np.array(points)], isClosed=False, color=(0, 255, 0), thickness=1)
                else:
                    for i in range(len(points) - 1):
                        cv2.line(annotated_image, points[i], points[i + 1], (0, 255, 0), 1)
                if points:
                    last_x, last_y = points[-1]
                    txt_lines.append(f"{last_x}, {last_y}, 170, 90.03, 0.35, -86.91")

    # === rembg contour 그리기 (간소화 적용) ===
    for contour in contours:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cy = int(M["m01"] / M["m00"])
        else:
            cy = 0

        if cy < int(y_min_img + (y_max_img - y_min_img) * 0.6):
            # 머리쪽: arcLength 필터 약하게, 단순화 약하게
            if cv2.arcLength(contour, True) < 50:
                continue
            approx = cv2.approxPolyDP(contour, 0.005 * cv2.arcLength(contour, True), True)
        else:
            # 옷쪽: arcLength 필터 강하게, 단순화 강하게
            if cv2.arcLength(contour, True) < 200:
                continue
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)

        # 이후는 동일
        prev = None
        for pt in approx:
            x, y = pt[0]
            nx, ny = normalize_point(x, y)
            if ny < 440:
                txt_lines.append(f"{nx}, {ny}, 156, 90.03, 0.35, -86.91")
            else:
                txt_lines.append(f"{nx}, {ny}, 155.5, 90.03, 0.35, -86.91")
            if prev is not None:
                cv2.line(annotated_image, prev, (int(nx), int(ny)), (255, 0, 0), 1)
            prev = (int(nx), int(ny))
        if prev is not None:
            txt_lines.append(f"{nx}, {ny}, 170, 90.03, 0.35, -86.91")

    # === 파일 저장 ===
    with open(output_txt_path, "w") as f:
        f.write("\n".join(txt_lines))
    cv2.imwrite(output_img_path, annotated_image)

    print("[end]")
    try:
        print("패턴 간소화 + 좌표 변환 + 파일 저장 완료:", output_txt_path)
    except Exception:
        pass
except SystemExit:
    raise
except Exception as e:
    traceback.print_exc()
    print(f"[error: {e}]")
    sys.exit(1)
