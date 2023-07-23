#!/usr/bin/env python3
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from generateScript import GenerateScript
from uploadDialog import Ui_uploadProgressDialog
from powerDownDialog import Ui_power_dialogBox
from deleteDialog import Ui_Dialog
from playSelectDialog import Ui_playSelectDialogBox
from mainui_update import Ui_MainWindow
import sys
import qdarkstyle

# TODO: 
# Make feature to rotate display
# Implement power off
# Implement dialog windows for errors and confirmations
# Open dialog 
#   * when deleting files for confirmation (delete before clicking "Save")
#   * when uploading a file
#   * confirmation of shutdown
#   * for errors

class MainUI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.gs = GenerateScript()
        self.connect()
        self.time_modifier = False
        
    def openUploadDialog(self, showError=None):
        self.window = QtWidgets.QDialog()
        ui = Ui_uploadProgressDialog(showError)
        ui.setupUi(self.window)
        self.window.exec_()

    def openPlaySelectDialog(self):
        self.dialog = QtWidgets.QDialog()
        ui = Ui_playSelectDialogBox(self.gs, self.dialog)
        self.dialog.exec_()

    def openShutdownDialog(self):
        self.window = QtWidgets.QMainWindow()
        ui = Ui_power_dialogBox(self.gs)
        ui.setupUi(self.window)
        self.window.show()

    def openDeleteDialog(self):
        self.dialog = QtWidgets.QDialog()
        ui = Ui_Dialog(self.gs, self.dialog)
        self.dialog.exec_()

    def uploadFile(self):
        fileName, _= QFileDialog.getOpenFileName(self, "Select video file", "",
                                "Video Files (*.avi *.mp4 *.m4v *.mkv *.mov *.MOV)")
        if fileName:
            exit_status = self.gs.uploadFile(fileName)
            if exit_status:
                self.openUploadDialog()

            else:
                self.openUploadDialog(showError=True)
    
    def saveChanges(self):
        self.gs.execFile()
        MainWindow.close()

    def cancelChanges(self):
        self.gs.cancel()
        MainWindow.close()

    def playSelected(self):
        self.openPlaySelectDialog()

    def selectInterval(self):
        interval = self.interval_spinBox.value()
       
        if self.time_modifier == False:
            self.interval_spinBox.setMaximum(60)
            self.interval = interval * 60

        elif self.time_modifier == True:
            self.interval = interval * 3600
            self.interval_spinBox.setMaximum(24)

        self.gs.setInterval(str(self.interval))

    def timeModifier(self):
        if self.time_comboBox.currentIndex() == 1:
            self.time_modifier = True
        
        else:
            self.time_modifier = False

    def selectFramesPerInterval(self):
        frames = self.frames_spinBox.value()
        self.gs.setFramesPerInterval(str(frames))

    def connect(self):
        try:
            self.interval_spinBox.setValue(self.gs.current_interval)
            self.frames_spinBox.setValue(self.gs.current_frames)

        except Exception:
            pass

        self.time_comboBox.setCurrentIndex(0)
        self.upload_button.clicked.connect(self.uploadFile)
        self.save_button.clicked.connect(self.saveChanges)
        self.cancel_button.clicked.connect(self.cancelChanges)
        self.remove_button.clicked.connect(self.openDeleteDialog)
        self.interval_spinBox.valueChanged.connect(self.selectInterval)
        self.time_comboBox.currentIndexChanged.connect(self.timeModifier)
        self.power_button.clicked.connect(self.openShutdownDialog)
        self.play_button.clicked.connect(self.playSelected)
        self.rotate_button.clicked.connect(self.gs.rotateImage)
        self.frames_spinBox.valueChanged.connect(self.selectFramesPerInterval)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    MainWindow = QtWidgets.QMainWindow()
    ui = MainUI()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())   
