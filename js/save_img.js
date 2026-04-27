function SaveImage() {
  // Electron 환경에서 로컬 파일을 표시하려면 file:// 경로 사용
  const imgPath = 'C:/drawing_data/FaceImages/face1.png';
  const img = document.getElementById('capturedImage');

  if (img) {
    img.src = `file:///${imgPath.replace(/\\/g, '/')}`;  // 윈도우 경로를 웹 형식으로 변환
  } else {
    alert("이미지 태그를 찾을 수 없습니다.");
  }

}


// 버튼 기능
function retry() {
  window.location.href = 'camera_shot.html';
}


function complete() {

  window.location.href = 'image_transform.html';


}


window.addEventListener('load', SaveImage);