from PIL import Image
import numpy as np
import cv2
from rembg import remove

# === 경로 ===
input_path = 'C:/drawing_data/FaceImages/face1.png'
output_path = 'C:/drawing_data/FaceImages/face_smooth_cloth.png'

# === rembg ===
input_image = Image.open(input_path).convert("RGBA")
output_image = remove(input_image)
image_np = np.array(output_image)

# === 색공간 변환 ===
image_bgr = cv2.cvtColor(image_np[:, :, :3], cv2.COLOR_RGBA2BGR)
hls = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HLS)

# === 목 아래 마스크 ===
alpha = image_np[:, :, 3]
h, w = alpha.shape
neck_y = int(h * 0.4)  # 필요시 조정
cloth_mask = (alpha > 0) & (np.arange(h)[:, None] >= neck_y)

# === 색조, 채도 제거 ===
hls[..., 0][cloth_mask] = 0       # 색조 고정
hls[..., 2][cloth_mask] = 0       # 채도 제거 (무채색화)

# === 다시 BGR + RGBA ===
result_bgr = cv2.cvtColor(hls, cv2.COLOR_HLS2BGR)
result_rgba = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGBA)
result_rgba[:, :, 3] = alpha

# === 저장 ===
Image.fromarray(result_rgba).save(output_path)
print(f"✅ 색 제거 + 주름 유지 완료: {output_path}")
