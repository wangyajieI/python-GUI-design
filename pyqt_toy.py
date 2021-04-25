#!/usr/local/anaconda3/bin/python3

from ui_ssh_toy import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication
from PyQt5.Qt import QThread, pyqtSignal
import subprocess
import os
import signal
import sys


class EmittingStream(QThread):
    writeSig = pyqtSignal(str)

    def __init__(self, command=None):
        super(EmittingStream, self).__init__()
        self.command = command

    def write(self, text):
        self.writeSig.emit(str(text))

    def run(self):
        if self.command:
            self.subprss = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            shell=True)
            while True:
                output = self.subprss.stdout.readline()
                if output == '' and self.subprss.poll() is not None:
                    break
                if output:
                    print(str(output, encoding='utf-8').strip())

    def pkill(self):
        try:
            os.killpg(self.subprss.pid, signal.SIGKILL)
        except Exception as e:
            print(e)


class logicPartClass(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(logicPartClass, self).__init__()
        self.setupUi(self)

        self.toolButton.clicked.connect(self.setShellPath)
        self.pushButton.clicked.connect(self.run_clicked)

        self.backFunc = EmittingStream()
        self.backFunc.writeSig.connect(self.outputWritten)
        sys.stdout = self.backFunc

    def setShellPath(self):
        shell_file = QFileDialog.getOpenFileName(self, "选择文件", "", "Shell Files (*.sh)")
        self.lineEdit.setText(shell_file[0])

    def _shell_path(self):
        return self.lineEdit.text()

    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()
        self.textBrowser.setReadOnly(True)

    def run_clicked(self):
        shell_path = self._shell_path()
        command = '/bin/bash ' + shell_path
        try:
            self.process = EmittingStream(command=command)
            self.process.start()
        except Exception as e:
            raise(e)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, '警告', '你确认要退出吗？',
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            sys.stdout = sys.__stdout__
            self.process.pkill()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = logicPartClass()
    window.show()
    sys.exit(app.exec_())
