import sys
import time
import traceback
from PyQt5.QtWidgets import QApplication
from cobot import *


def _wait_connect(timeout=10):
    start_time = time.time()
    while not (IsCommandSockConnect() and IsDataSockConnect()):
        if time.time() - start_time > timeout:
            return False
        QApplication.processEvents()
        time.sleep(0.1)
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
    
