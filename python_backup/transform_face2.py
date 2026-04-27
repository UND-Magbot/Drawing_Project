import cv2
import numpy as np
from PIL import Image
from rembg import remove
import mediapipe as mp

# === 경로 설정 ===
image_path = "C:/drawing_data/FaceImages/face.png"
output_img_path = "C:/drawing_data/FaceImages/combined_output.png"
output_txt_path = "C:/drawing_data/points.txt"

# === 좌표 변환 범위 설정 ===
X_MIN, X_MAX = 550, 670
Y_MIN, Y_MAX = 350, 550

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

# === 이미지 로드 및 좌우 반전 후 배경 제거 ===
input_image = Image.open(image_path).transpose(Image.FLIP_LEFT_RIGHT)
output_image = remove(input_image)
image_np = np.array(output_image)
image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR if image_np.shape[2] == 4 else cv2.COLOR_RGB2BGR)
annotated_image = image_cv.copy()

# === MediaPipe 얼굴 윤곽선 ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
results = face_mesh.process(image_rgb)
height, width, _ = image_cv.shape

# === 얼굴 윤곽점 정의 ===
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

txt_lines = []
txt_lines.append(f"660, 450, 250, 90.03, 0.35, -86.91")

def normalize_point(x, y):
    new_x = ((x - 0) / width) * (X_MAX - X_MIN) + X_MIN
    new_y = ((y - 0) / height) * (Y_MAX - Y_MIN) + Y_MIN
    return round(new_x, 2), round(new_y, 2)

# === 얼굴 landmark 추출 ===
if results.multi_face_landmarks:
    for face_landmarks in results.multi_face_landmarks:
        for group_name, indices in landmark_groups.items():
            points = []
            for idx in indices:
                x = int(face_landmarks.landmark[idx].x * width)
                y = int(face_landmarks.landmark[idx].y * height)
                nx, ny = normalize_point(x, y)
                points.append((x, y))
                txt_lines.append(f"{nx}, {ny}, 170, 90.03, 0.35, -86.91")
            if group_name == "nose_curve":
                cv2.polylines(annotated_image, [np.array(points)], isClosed=False, color=(0, 255, 0), thickness=1)
            else:
                for i in range(len(points) - 1):
                    cv2.line(annotated_image, points[i], points[i+1], (0, 255, 0), 1)

# === rembg 윤곽선 ===
blurred = cv2.bilateralFilter(image_cv, 9, 3, 3)
gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 50, 150)
edges_skeleton = skeletonize(edges)
contours, _ = cv2.findContours(edges_skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
simplified_contours = [cv2.approxPolyDP(c, 0.005 * cv2.arcLength(c, True), True) for c in contours if len(c) > 5]

all_points = np.vstack([cnt.reshape(-1, 2) for cnt in simplified_contours])
x_min_img, y_min_img = np.min(all_points, axis=0)
x_max_img, y_max_img = np.max(all_points, axis=0)

def normalize_rembg_point(x, y):
    new_x = ((x - x_min_img) / (x_max_img - x_min_img)) * (X_MAX - X_MIN) + X_MIN
    new_y = ((y - y_min_img) / (y_max_img - y_min_img)) * (Y_MAX - Y_MIN) + Y_MIN
    return round(new_x, 2), round(new_y, 2)

for contour in simplified_contours:
    prev = None
    for i, pt in enumerate(contour):
        x, y = pt[0]
        nx, ny = normalize_rembg_point(x, y)
        if i == 0:
            txt_lines.append(f"{nx}, {ny}, 170, 90.03, 0.35, -86.91")
        if ny < 450:
            txt_lines.append(f"{nx}, {ny}, 164.25, 90.03, 0.35, -86.91")
        else:
            txt_lines.append(f"{nx}, {ny}, 163.8, 90.03, 0.35, -86.91")
        if prev is not None:
            cv2.line(annotated_image, prev, (x, y), (255, 0, 0), 1)
        prev = (x, y)
    txt_lines.append(f"{nx}, {ny}, 180, 90.03, 0.35, -86.91")

txt_lines.append(f"{nx}, {ny}, 250, 90.03, 0.35, -86.91")


# === 저장 ===
with open(output_txt_path, "w") as f:
    f.write("\n".join(txt_lines))
cv2.imwrite(output_img_path, annotated_image)
print("✅ 결합된 윤곽선 이미지 및 텍스트 저장 완료:", output_img_path)
