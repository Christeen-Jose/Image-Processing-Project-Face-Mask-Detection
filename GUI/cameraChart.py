from PySide2.QtGui import *
from PySide2.QtWidgets import *
from camera import Camera

"""
    left chart 
    Camera area with current student data table
"""


class CameraChart(QWidget):
    def __init__(self, parent=None):
        super(CameraChart, self).__init__(parent)
        self.title = QLabel(self)
        self.image = QLabel(self)
        self.infoTable = QTableWidget(self)
        self.attendanceData = {}
        self.camera = None
        self.captureMaskNext = False
        self.currentId = ""
        self.currentName = ""
        # self.camera.set_method("test_and_detect")
        # self.camera.start()
        # self.camera.updateImage.connect(self.update_image)
        # self.camera.set_method("capture", {"name": "Ansary"})
        # self.camera.start()
        # self.camera.updateImage.connect(self.update_image)
        self._init_ui()
        self._init_style()

    def _init_ui(self):
        """
        Draws the GUI in the widget
        :return:
        """
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.title)
        self.layout().addWidget(self.image)
        self.layout().addWidget(self.infoTable)

    def _init_style(self):
        """
        Change the styles of the widget
        :return:
        """
        self.image.setFixedSize(640, 480)
        self.setFixedWidth(640)
        self.infoTable.setRowCount(3)
        self.infoTable.setColumnCount(1)
        self.infoTable.setVerticalHeaderLabels(["ID", "Name", "Is Masked?"])
        item = QTableWidgetItem()
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.infoTable.setItem(0, 0, item)
        item2 = QTableWidgetItem()
        item2.setFlags(item2.flags() ^ Qt.ItemIsEditable)
        self.infoTable.setItem(1, 0, item2)
        item3 = QTableWidgetItem()
        item3.setFlags(item2.flags() ^ Qt.ItemIsEditable)
        self.infoTable.setItem(2, 0, item3)
        self.infoTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.infoTable.horizontalHeader().hide()

    def update_image(self, title, image, data={}):
        self.title.setText(title)
        self.image.setPixmap(QPixmap.fromImage(image))
        if data:
            if "id" in data:
                if data["id"]:
                    self.infoTable.item(0, 0).setText(data["id"])
            else:
                self.infoTable.item(0, 0).setText("")
            if "name" in data:
                if data["name"]:
                    self.infoTable.item(1, 0).setText(data["name"])
                if "isAttendance" in data:
                    if data["isAttendance"]:
                        value = {"name": data["name"], "masked": data["masked"], "time": data["time"]}
                        self.attendanceData[data["id"]] = value
            else:
                self.infoTable.item(1, 0).setText("")
            if "masked" in data:
                if data["masked"]:
                    self.infoTable.item(2, 0).setText("Yes")
                else:
                    self.infoTable.item(2, 0).setText("No")
            else:
                self.infoTable.item(2, 0).setText("")
        else:
            self.infoTable.item(0, 0).setText("")
            self.infoTable.item(1, 0).setText("")
            self.infoTable.item(2, 0).setText("")
        if title == "" and self.captureMaskNext:
            reply = QMessageBox.information(None, "Mask is Requiried", "Please put on your mask.", QMessageBox.Ok)
            if reply == QMessageBox.Ok:
                self.camera = Camera()
                self.camera.set_method("capture_mask_training_images", {"id": self.currentId, "name": self.currentName})
                self.camera.start()
                self.camera.updateImage.connect(self.update_image)
            self.captureMaskNext = False

    def capture_images(self, id: int, name: str):
        self.camera = Camera()
        self.camera.set_method("capture_training_images", {"id": id, "name": name})
        self.camera.start()
        self.camera.updateImage.connect(self.update_image)
        self.captureMaskNext = True
        self.currentId = id
        self.currentName = name

    def take_attendance(self, students: dict):
        self.attendanceData = {}
        self.camera = Camera()
        self.camera.set_method("recognize_attendence", {"students": students})
        self.camera.start()
        self.camera.updateImage.connect(self.update_image)

    def end_attendance(self):
        self.camera.stop()
        return self.attendanceData

