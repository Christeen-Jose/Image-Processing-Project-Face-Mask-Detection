from GUI.mainWindow import MainWindow
from PySide2.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.showMaximized()
    app.setStyle('Fusion')
    sys.exit(app.exec_())


# capture_training_images("Ansary")
# capture_training_images("AnsaryMask", 0, "Training Mask Images")
# train_model()
# recognize_attendence()
