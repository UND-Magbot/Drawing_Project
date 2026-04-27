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
simplified_contours = [cv2.approxPolyDP(c, 0.005 * cv2.arcLength(c, True), True) for c in contours if len(c) > 5]
all_points = np.vstack([cnt.reshape(-1, 2) for cnt in simplified_contours])
x_min_img, y_min_img = np.min(all_points, axis=0)
x_max_img, y_max_img = np.max(all_points, axis=0)

# === 스케일링 비율 계산 (비율 유지)
scale_x = (X_MAX - X_MIN) / (x_max_img - x_min_img)
scale_y = (Y_MAX - Y_MIN) / (y_max_img - y_min_img)
uniform_scale = min(scale_x, scale_y)

def normalize_point(x, y):
    center_x = (x_min_img + x_max_img) / 2
    center_y = (y_min_img + y_max_img) / 2
    new_x = (x - center_x) * uniform_scale + (X_MIN + X_MAX) / 2
    new_y = (y - center_y) * uniform_scale + (Y_MIN + Y_MAX) / 2
    return round(new_x, 2), round(new_y, 2)

# === MediaPipe 초기화 ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
results = face_mesh.process(image_rgb)
height, width, _ = image_cv.shape

# === landmark 그룹 정의 ===
FACE_OUTLINE = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378,
                400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21,
                54, 103, 67, 109, 10]
LIPS_OUTLINE = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317,
                14, 87, 178, 88, 95, 61]
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

# === txt 파일 + 시각화 ===
txt_lines = []
txt_lines.append("660, 450, 250, 90.03, 0.35, -86.91")

# rembg contour
for contour in simplified_contours:
    prev = None
    for i, pt in enumerate(contour):
        x, y = pt[0]
        nx, ny = normalize_point(x, y)
        if i == 0:
            txt_lines.append(f"{nx}, {ny}, 170, 90.03, 0.35, -86.91")
        if ny < 440:
            txt_lines.append(f"{nx}, {ny}, 159.5, 90.03, 0.35, -86.91")
        else:
            txt_lines.append(f"{nx}, {ny}, 159, 90.03, 0.35, -86.91")
        if prev is not None:
            cv2.line(annotated_image, prev, (int(nx), int(ny)), (255, 0, 0), 1)
        prev = (int(nx), int(ny))
    txt_lines.append(f"{nx}, {ny}, 170, 90.03, 0.35, -86.91")
txt_lines.append(f"{nx}, {ny}, 250, 90.03, 0.35, -86.91")

# === 파일 저장 ===
with open(output_txt_path, "w") as f:
    f.write("\n".join(txt_lines))
cv2.imwrite(output_img_path, annotated_image)

print("✅ 비율 유지 스케일링 + 좌표 파일 + 시각화 완료:", output_txt_path)
