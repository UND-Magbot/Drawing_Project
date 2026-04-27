import cv2
import numpy as np
from PIL import Image
from rembg import remove

# === 경로 설정 ===
image_path = r"C:/drawing_data/FaceImages/face.png"
output_txt_path = r"C:/drawing_data/points.txt"

# === 좌표 변환 범위 설정 (로봇 작업 영역 mm 기준) ===
X_MIN, X_MAX = 550, 650
Y_MIN, Y_MAX = 350, 530

# === Skeletonize 함수 ===
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

# === 정규화 함수 (픽셀 좌표 → 로봇 좌표) ===
def normalize_point(x, y, x_min_img, x_max_img, y_min_img, y_max_img):
    new_x = ((x - x_min_img) / (x_max_img - x_min_img)) * (X_MAX - X_MIN) + X_MIN
    new_y = ((y - y_min_img) / (y_max_img - y_min_img)) * (Y_MAX - Y_MIN) + Y_MIN
    return round(new_x, 2), round(new_y, 2)

# === 이미지 처리 시작 ===
input_image = Image.open(image_path)
input_image = input_image.transpose(Image.FLIP_LEFT_RIGHT)
output_image = remove(input_image)
image_np = np.array(output_image)
image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

# === 윤곽선 추출 ===
blurred = cv2.medianBlur(gray, 7)
edges = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 4)
edges_skeleton = skeletonize(edges)

# === 윤곽선 단순화 및 추출 ===
contours, _ = cv2.findContours(edges_skeleton, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
simplified_contours = [cv2.approxPolyDP(c, 0.005 * cv2.arcLength(c, True), True) for c in contours if len(c) > 5]

# === 정규화 범위 계산 ===
all_points = np.vstack([cnt.reshape(-1, 2) for cnt in simplified_contours])
x_min_img, y_min_img = np.min(all_points, axis=0)
x_max_img, y_max_img = np.max(all_points, axis=0)

# === points.txt 저장 ===
txt_lines = []
txt_lines.append("660, 450, 250, 90.03, 0.35, -86.91")  # 시작점(펜업)

for contour in simplified_contours:
    prev = None
    for i, pt in enumerate(contour):
        x, y = pt[0]
        nx, ny = normalize_point(x, y, x_min_img, x_max_img, y_min_img, y_max_img)
        if i == 0:
            txt_lines.append(f"{nx}, {ny}, 170, 90.03, 0.35, -86.91")  # 펜다운 직전
        if ny < 430:
            txt_lines.append(f"{nx}, {ny}, 164.25, 90.03, 0.35, -86.91")  # 그리는 높이
        else:
            txt_lines.append(f"{nx}, {ny}, 163.5, 90.03, 0.35, -86.91")
        prev = (nx, ny)
    txt_lines.append(f"{nx}, {ny}, 180, 90.03, 0.35, -86.91")  # 펜업

txt_lines.append(f"{nx}, {ny}, 250, 90.03, 0.35, -86.91")  # 끝점(펜업)

# === 저장 ===
with open(output_txt_path, "w") as f:
    f.write("\n".join(txt_lines))

print("✅ points.txt 저장 완료:", output_txt_path)
