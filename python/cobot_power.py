import sys
import time
import threading
import traceback
from PyQt5.QtWidgets import QApplication
from cobot import *


def _silence_socket_shutdown_errors(args):
    if issubclass(args.exc_type, (OSError, BrokenPipeError)):
        return
    sys.__excepthook__(args.exc_type, args.exc_value, args.exc_traceback)

threading.excepthook = _silence_socket_shutdown_errors


def _wait_connect(timeout=10):
    start_time = time.time()
    while not (IsCommandSockConnect() and IsDataSockConnect()):
        if time.time() - start_time > timeout:
            return False
        QApplication.processEvents()
        time.sleep(0.1)
    return True


def _wait_idle(timeout=30):
    start_time = time.time()
    while not IsIdle():
        if time.time() - start_time > timeout:
            return False
        QApplication.processEvents()
        time.sleep(0.05)
    return True


def servo_on():
    app = QApplication(sys.argv)
    try:
        ip = '10.0.2.7'
        print(f"[INFO] Connecting to robot at {ip} ...")
        ToCB(ip)

        if not _wait_connect(10):
            print("[error: 로봇 연결 실패 - 타임아웃]")
            sys.stdout.flush()
            return

        print("[INFO] 로봇 연결 성공!")
        print("[INFO] Initializing robot...")
        CobotInit()
        time.sleep(1)

        SetProgramMode(PG_MODE.REAL)
        time.sleep(5)

        time.sleep(4)
        print("[power_on_ok]")
        sys.stdout.flush()
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


def servo_off():
    app = QApplication(sys.argv)
    try:
        ip = '10.0.2.7'
        print(f"[INFO] Connecting to robot at {ip} ...")
        ToCB(ip)

        if not _wait_connect(10):
            print("[error: 로봇 연결 실패 - 타임아웃]")
            sys.stdout.flush()
            return

        print("[INFO] 로봇 연결 성공!")
        SetProgramMode(PG_MODE.REAL)
        time.sleep(5)

        # 전원 차단 전 안전 위치로 이동 (바닥 충돌 방지)
        print("[INFO] 안전 위치로 이동 중...")
        SetBaseSpeed(0.5)
        time.sleep(0.5)
        safe_position = "660, 450, 400, 90.03, 0.35, -86.91"
        ManualScript(f"movetcp 0.5, 0.5, {safe_position}")
        time.sleep(0.1)
        if not _wait_idle(30):
            print("[WARN] 안전 위치 이동 타임아웃, 전원 차단을 그대로 진행합니다")

        print("[INFO] Servo Power OFF 시도")
        RobotPowerDown()
        time.sleep(1)

        print("[power_off_ok]")
        sys.stdout.flush()
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
     if len(sys.argv) > 1:
        if sys.argv[1] == 'on':
            servo_on()
        elif sys.argv[1] == 'off':
            servo_off()
    
