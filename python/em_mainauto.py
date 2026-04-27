import os
import sys
import time
import traceback
from PyQt5.QtWidgets import QApplication

from cobot import *

def main():
    app = QApplication(sys.argv)

    try:
        ip = '10.0.2.7'  # 로봇 IP 주소
        print(f"[INFO] Connecting to robot at {ip} ...")
        ToCB(ip)

        # 연결될 때까지 대기
        timeout = 10  # 최대 대기 시간 (초)
        start_time = time.time()
        while not (IsCommandSockConnect() and IsDataSockConnect()):
            if time.time() - start_time > timeout:
                print("[error: 로봇 연결 실패 - 타임아웃]")
                sys.stdout.flush()
                sys.exit(1)
            QApplication.processEvents()
            time.sleep(0.1)

        print("[INFO] 로봇 연결 성공!")

        # 로봇 초기화
        print("[INFO] Initializing robot...")
        CobotInit()
        time.sleep(1)

        # 프로그램 모드 설정
        print("[INFO] Setting program mode...")
        SetProgramMode(PG_MODE.REAL)
        time.sleep(1)

        # 속도 설정
        speed = 0.95
        print(f"[INFO] Setting speed: {speed}")
        SetBaseSpeed(speed)
        time.sleep(1)

        # 스크립트 파일 실행
        txt_path = "C:/drawing_data/points.txt"
        if not os.path.exists(txt_path):
            print(f"[error: 좌표 파일을 찾을 수 없습니다: {txt_path}]")
            sys.stdout.flush()
            sys.exit(1)

        with open(txt_path, "r") as file:
            print(f"[INFO] Running script file from: {txt_path}")
            for line in file:
                line_clean = line.strip()
                if not line_clean:
                    continue
                cmd = "movetcp 0.1, 0.05, " + line_clean
                print(f"[COMMAND] {cmd}")
                ManualScript(cmd)
                time.sleep(0.1)
                # 동작 완료 대기 (개별 명령당 최대 30초)
                cmd_start = time.time()
                while not IsIdle():
                    if time.time() - cmd_start > 30:
                        print("[error: 명령 실행 타임아웃 - 로봇 응답 없음]")
                        sys.stdout.flush()
                        sys.exit(1)
                    QApplication.processEvents()

        print("[end]")
        sys.stdout.flush()
    except SystemExit:
        raise
    except Exception as e:
        traceback.print_exc()
        print(f"[error: {e}]")
        sys.stdout.flush()
    finally:
        try:
            DisConnectToCB()
        except Exception:
            pass
        try:
            app.quit()
            del app
        except Exception:
            pass
    sys.exit()

if __name__ == '__main__':
    main()
