import cv2
import numpy as np
from rembg import remove
import os

# === 설정 ===
image_path = "C:/drawing_data/FaceImages/face.png"
output_txt_path = "C:/drawing_data/points.txt"

min_x, max_x = 550, 670
min_y, max_y = 350, 550

# === 좌표 변환 범위 설정 ===
X_MIN, X_MAX = 550, 670
Y_MIN, Y_MAX = 350, 550

# === 이미지 로드 및 배경 제거 ===
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")

# rembg는 RGB 입력이므로 변환 필요
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image_no_bg = remove(image_rgb)  # 배경 제거
image_no_bg = cv2.cvtColor(np.array(image_no_bg), cv2.COLOR_RGBA2BGRA)  # BGRA로 변환

# === 좌우 반전 ===
flipped = cv2.flip(image_no_bg, 1)

# === 그레이 변환 및 Canny 엣지 추출 (알파채널 고려) ===
bgr = flipped[:, :, :3]
alpha = flipped[:, :, 3]
mask = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)[1]
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
gray = cv2.bitwise_and(gray, gray, mask=mask)
canny_edges = cv2.Canny(gray, 100, 200)

# === 윤곽선 찾기 및 필터링 ===
contours, _ = cv2.findContours(canny_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
filtered_contours = [cnt for cnt in contours if len(cnt) > 30]

# === 스케일 및 중심 정렬 ===
img_h, img_w = gray.shape[:2]
target_w = max_x - min_x
target_h = max_y - min_y
scale_x = target_w / img_w
scale_y = target_h / img_h
scale = min(scale_x, scale_y)
offset_x = min_x + (target_w - img_w * scale) / 2
offset_y = min_y + (target_h - img_h * scale) / 2

# === 좌표 저장 ===
with open(output_txt_path, "w") as f:
    for contour in filtered_contours:
        for point in contour:
            x, y = point[0]
            scaled_x = int(x * scale + offset_x)
            scaled_y = int(y * scale + offset_y)
            f.write(f"{scaled_x}, {scaled_y}, 170, 90.03, 0.35, -86.91\n")

print(f"✅ 저장 완료 → {output_txt_path}")

# === 시각화 ===
preview_w = max_x + 50
preview_h = max_y + 50
preview = np.ones((preview_h, preview_w, 3), dtype=np.uint8) * 255

for contour in filtered_contours:
    scaled_points = [(int(p[0][0] * scale + offset_x), int(p[0][1] * scale + offset_y)) for p in contour]
    for i in range(len(scaled_points) - 1):
        cv2.line(preview, scaled_points[i], scaled_points[i + 1], (0, 0, 0), 1)

cv2.imshow("Final Drawing Preview", preview)
cv2.waitKey(0)
cv2.destroyAllWindows()
