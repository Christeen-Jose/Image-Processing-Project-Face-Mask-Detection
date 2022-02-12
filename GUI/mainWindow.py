from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from GUI.cameraChart import CameraChart
from GUI.studentsWidget import StudentsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.cameraChart = CameraChart(self)
        self.studentsWidget = StudentsWidget(self)
        self._init_ui()
        self._start_communication()

    def _init_ui(self):
        """
        Draws the GUI in the widget
        :return:
        """
        widget = QWidget()
        widget.setLayout(QHBoxLayout())
        widget.layout().addWidget(self.cameraChart)
        widget.layout().addWidget(self.studentsWidget)
        self.setCentralWidget(widget)

    def _start_communication(self):
        """
        Connects signals with handlers and other components.
        :return:
        """
        self.setWindowTitle("Attendance and Face Mask Recognition System")
        self.setWindowIcon(QIcon("Data/icons/icon.png"))
        self.studentsWidget.captureImages.connect(self.capture_images)
        self.studentsWidget.takeAttendance.connect(self.take_attendance)
        self.studentsWidget.endAttendance.connect(self.end_attendance)

    def capture_images(self, id: int, name: str):
        self.cameraChart.capture_images(id, name)

    def take_attendance(self, students: dict):
        self.cameraChart.take_attendance(students)

    def end_attendance(self):
        data = self.cameraChart.end_attendance()
        self.studentsWidget.set_attendance(data)



