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


def _move_to(target_coords):
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
        time.sleep(1)

        speed = 0.85
        print(f"[INFO] Setting speed: {speed}")
        SetBaseSpeed(speed)
        time.sleep(1)

        cmd_penchange = "movetcp 0.8, 0.8, " + target_coords
        print(f"=========== move: {cmd_penchange}")
        ManualScript(cmd_penchange)
        time.sleep(0.1)
        if not _wait_idle(30):
            print("[error: 이동 타임아웃]")
            sys.stdout.flush()
            return

        print("[pen_ok]")
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


def change():
    _move_to("516.8,-59,672.12,-33.14,89.36,-4.45")


def home():
    _move_to("660, 450, 250, 90.03, 0.35, -86.91")



if __name__ == '__main__':
     if len(sys.argv) > 1:
        if sys.argv[1] == 'change':
            change()
        elif sys.argv[1] == 'home':
            home()