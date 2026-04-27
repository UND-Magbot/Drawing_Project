import time

import sys
import time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QToolTip, QGridLayout, QLabel, QLineEdit, QSlider,
                             QVBoxLayout, QHBoxLayout)

from cobot import *

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)
        global spd, setspd_sld
        global ip_get, ip

        #####
        global btn
        btn = QPushButton('Connect', self)
        ip = QLineEdit('10.0.2.7')
        init_btn = QPushButton('Initialized')
        ip_hgrid = QHBoxLayout()
        ip_hgrid.addWidget(ip)
        ip_hgrid.addWidget(init_btn)
        grid.addLayout(ip_hgrid, 0, 1)
        grid.addWidget(btn, 0, 0)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.setStyleSheet("background-color: red")
        btn.clicked.connect(lambda: ToCB(ip.text()))
        init_btn.clicked.connect(CobotInit)

        #####
        timer = QTimer(self)
        timer.setInterval(10)
        timer.timeout.connect(self.datareset)
        timer.start()

        #####
        status_hgrid = QHBoxLayout()
        mode_btn = QPushButton('Mode')
        global mode_lb, robot_lb
        mode_lb = QLabel('Mode : ')
        robot_lb = QLabel('Robot : ')
        grid.addWidget(mode_btn, 1, 0)
        status_hgrid.addWidget(mode_lb)
        status_hgrid.addWidget(robot_lb)
        grid.addLayout(status_hgrid, 1, 1)
        global mode
        mode = PG_MODE.SIMULATION
        mode_btn.clicked.connect(lambda: SetProgramMode(mode))

        #####
        setspd_hgrid = QHBoxLayout()
        setspd_btn = QPushButton('Speed Bar')
        setspd_sld = QSlider(Qt.Horizontal)
        setspd_sld.setTickPosition(1)
        setspd_sld.setMaximum(100)
        setspd_sld.setMinimum(0)
        spd = float(setspd_sld.value()) * 0.01
        global spd_lb
        spd_lb = QLabel(str(float(setspd_sld.value()) * 0.01))
        setspd_hgrid.addWidget(spd_lb)
        setspd_hgrid.addWidget(setspd_sld)
        grid.addLayout(setspd_hgrid, 2, 1)
        grid.addWidget(setspd_btn, 2, 0)
        setspd_btn.clicked.connect(lambda: SetBaseSpeed(float(setspd_sld.value()) * 0.01))

        #### Manual Script from File
        mscript_btn = QPushButton('Run Script File')
        grid.addWidget(mscript_btn, 5, 0)
        mscript_btn.clicked.connect(self.run_script_file)

        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This is a <b>QWidget</b> widget')
        self.setWindowTitle('Rainbow Robotics')
        self.setWindowIcon(QIcon('robotics-ci-1.png'))
        self.setGeometry(300, 300, 300, 300)
        self.show()

    def datareset(self):
        global mode, mode_lb, robot_lb
        global spd_lb
        global btn

        setspd_f2 = round(float(setspd_sld.value()) * 0.01, 2)
        spd_lb.setText(str(setspd_f2))

        if IsRobotReal():
            mode_lb.setText('Mode : REAL')
            mode = PG_MODE.SIMULATION
        else:
            mode_lb.setText('Mode : SIMULATION')
            mode = PG_MODE.REAL

        if IsIdle():
            robot_lb.setText('ROBOT : IDLE')
        else:
            robot_lb.setText('ROBOT : RUN')

        if IsCommandSockConnect() and IsDataSockConnect():
            btn.setStyleSheet("background-color: green")
            btn.setText('Connect')
        else:
            btn.setStyleSheet("background-color: red")
            btn.setText('Disconnect')

    def run_script_file(self):
        # txt_path = "C:\drawing_data\points.txt"
        txt_path = "C:\drawing_data\sqaure_test.txt"
        with open(txt_path, "r") as file:
            for line in file:
                cmd = "movetcp 0.1, 0.05, " + line.strip()
                if cmd:
                    # IsIdle == True -> IDLE인 상태 
                    # IsIdle == False -> RUN인 상태
                    print(f"=========== 명령 실행: {cmd}\n")
                    ManualScript(cmd)
                    time.sleep(0.1)
                    switch = 0
                    while not IsIdle():
                        pass 
                        # QApplication.processEvents()
                        # time.sleep(0.1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
