import sys
import csv
import time
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QTextEdit
from PyQt5.QtGui import QColor
import numpy as np
import pyqtgraph as pg
import serial  
from QRoundProgressbar import RoundProgressbar

# 全局变量用于初始化串口，这里的参数需根据实际情况调整
ser = serial.Serial('COM4', 115200, timeout=0.1)


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class SerialReadThread(QThread):
    update_data = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.mode = [0xFE, 0x00, 0x78, 0x41, 0x00, 0x00, 0x00, 0x00, 0xb9]
        self.read_adc = [0xFE, 0x00, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x86]

    def run(self):
        self.is_running = True
        
        while self.is_running:
            try:
                ser.write(bytearray(self.read_adc))
                time.sleep(0.1)
                if ser.in_waiting:
                    received_data = ser.read(ser.in_waiting)
                    hex_str_data2 = hex((received_data[7] << 8) | received_data[8])[2:].zfill(4)
                    data2 = int(hex_str_data2, 16)
                    self.update_data.emit(data2)
                    print( data2)
                time.sleep(0.1)
            except Exception as e:
                print("串口读取线程错误:", e)
                break

    def stop(self):
        self.is_running = False


class Stats(QMainWindow):
    old_image = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        # Load UI
        self.ui = uic.loadUi("ScanGUI.ui", self)
        self.setWindowTitle("Gas System")
        self.csv_file = "Data/data_" +str(time.time()) +".csv"
        self.init_csv()
        # Output Display
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.outputTextEdit = self.ui.findChild(QTextEdit, "Console")

        # 创建串口读取线程实例
        self.serial_read_thread = SerialReadThread()
        self.serial_read_thread.update_data.connect(self.Handle_Update_Image)

        # Events
        self.ui.scan.clicked.connect(self.Scan)
        self.ui.stop.clicked.connect(self.Stop)

        # Figures Initialization
        self.plot = self.ui.IMG1
        self.show()
        self.normal_threshold = 30
        self.bad_threshold = 70

        self.concentrations = np.zeros(1000)
        self.x = np.arange(1000)
        self.plot_conc = self.ui.Records
        self.plot_conc.setBackground('w')
        pg.setConfigOption('background', 'w')  # 设置背景为白色
        pg.setConfigOption('foreground', 'k')

        plot_instance1 = self.plot_conc.addPlot()
        plot_instance1.showGrid(x=True, y=True)
        plot_instance1.enableAutoRange()

        pen = pg.mkPen(color=pg.intColor(0, 9), width=2)  # 不同颜色
        self.line_conc = plot_instance1.plot(self.x, self.concentrations, pen=pen, name=f"conc")

    @pyqtSlot(str)
    def normalOutputWritten(self, text):
        cursor = self.outputTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.outputTextEdit.setTextCursor(cursor)
        self.outputTextEdit.ensureCursorVisible()

    def on_connection_success(self):
        print("Successfully connected to the server!")

    def on_connection_failed(self, error_message):
        print(error_message)

    @pyqtSlot(int)
    def Handle_Update_Image(self, new_data):
        conc = max((1500 - new_data)/15, 0)
        self.plot.set_value(conc)
        if (conc < self.normal_threshold):
            self.plot.set_color(QColor(100, 255, 100))
        elif (conc < self.bad_threshold):
            self.plot.set_color(QColor(250, 150, 100))
        else:
            self.plot.set_color(QColor(255, 100, 100))
        self.concentrations = np.roll(self.concentrations, -1)
        self.concentrations[-1] = conc
        self.line_conc.setData(self.x, self.concentrations)
        self.append_to_csv(np.append(new_data,self.concentrations[-1]))
        self.show()

    def Scan(self):
        try:
            # 这里不再创建ScanThread，而是直接操作serial_read_thread
            if not self.serial_read_thread.isRunning():
                print("Start Serial Reading...")
                self.serial_read_thread.start()
        except:
            print("线程相关错误.")

    def Stop(self):
        self.serial_read_thread.stop()
        print("串口读取停止.")

    def init_csv(self):
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            header = ["raw","conc"]
            writer.writerow(header)

    def append_to_csv(self, new_data):
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_data)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    stats = Stats()
    stats.show()
    sys.exit(app.exec_())

