import os

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtGui
from PySide2.QtCore import Signal
from PySide2.QtCore import Qt
import csv
from modelTraining import train_model

"""
    Right chart 
    Students table and attendace table
"""


class StudentsWidget(QWidget):
    captureImages = Signal(int, str)
    takeAttendance = Signal(dict)
    endAttendance = Signal()

    def __init__(self, parent=None):
        super(StudentsWidget, self).__init__(parent)
        self.csvFileName = "Data/students.csv"
        self.tabWidget = QTabWidget(self)
        self.studentsTable = QTableWidget(self)
        self.attendanceTable = QTableWidget(self)
        self.addBtn = QPushButton("Add")
        self.removeBtn = QPushButton("Remove")
        self.saveBtn = QPushButton("Save")
        self.trainBtn = QPushButton("Train Model")
        self.attendanceBtn = QPushButton("Take Attendance")
        self.saveAttendanceBtn = QPushButton("Save Attendance")
        self._init_ui()
        self._start_communication()
        self.load_csv()

    def _init_ui(self):
        """
        Draws the GUI in the widget
        :return:
        """
        studentsWidget = QWidget(self)
        studentsWidget.setLayout(QHBoxLayout(self))
        self.setLayout(QHBoxLayout())
        btnsLayout = QVBoxLayout(self)
        btnsLayout.addWidget(self.addBtn)
        btnsLayout.addWidget(self.removeBtn)
        btnsLayout.addWidget(self.saveBtn)
        btnsLayout.addWidget(self.trainBtn)
        btnsLayout.addStretch()
        studentsWidget.layout().addWidget(self.studentsTable)
        studentsWidget.layout().addLayout(btnsLayout)
        attendanceWidget = QWidget(self)
        attendanceWidget.setLayout(QHBoxLayout())
        attendanceWidget.layout().addWidget(self.attendanceTable)
        btnsLayout = QVBoxLayout(self)
        btnsLayout.addWidget(self.attendanceBtn)
        btnsLayout.addWidget(self.saveAttendanceBtn)
        btnsLayout.addStretch()
        attendanceWidget.layout().addLayout(btnsLayout)
        self.tabWidget.addTab(studentsWidget, "Students")
        self.tabWidget.addTab(attendanceWidget, "Attendance")
        self.layout().addWidget(self.tabWidget)

        self.studentsTable.setColumnCount(4)
        header = self.studentsTable.horizontalHeader()
        for col in range(self.studentsTable.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        self.studentsTable.setHorizontalHeaderItem(3, QTableWidgetItem("Take Images Data"))
        self.attendanceTable.setColumnCount(4)
        self.attendanceTable.setHorizontalHeaderLabels(["ID", "Name", "Is Masked?", "Time"])
        header = self.attendanceTable.horizontalHeader()
        for col in range(self.attendanceTable.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)

    def _start_communication(self):
        """
        Connects signals with handlers and other components.
        :return:
        """
        self.addBtn.clicked.connect(self._add_btn_clicked)
        self.removeBtn.clicked.connect(self._remove_btn_clicked)
        self.saveBtn.clicked.connect(self._save_btn_clicked)
        self.trainBtn.clicked.connect(self._train_btn_clicked)
        self.attendanceBtn.clicked.connect(self.take_attendance)
        self.saveAttendanceBtn.clicked.connect(self._save_attendance_btn_clicked)

    def _add_btn_clicked(self):
        """
        add new student button handler
        :return:
        """
        row = self.studentsTable.rowCount()
        self.studentsTable.insertRow(row)
        btn = QPushButton("Capture Training Images")
        btn.clicked.connect(lambda: self.capture_images(row))
        self.studentsTable.setCellWidget(row, 3, btn)

    def _remove_btn_clicked(self):
        """
        remove selected students button handler
        :return:
        """
        rowsToDelete = []
        for index in self.studentsTable.selectedIndexes():
            row = index.row()
            rowsToDelete.append(row)
        rowsToDelete.sort(reverse=True)
        for row in rowsToDelete:
            self.studentsTable.removeRow(row)

    def _train_btn_clicked(self):
        """
        Train model button handler
        :return:
        """
        self.trainBtn.setEnabled(False)
        self.trainBtn.setText("Training...")
        QApplication.processEvents()
        train_model()
        self.trainBtn.setText("Train Model")
        self.trainBtn.setEnabled(True)

    def _add_btn_at_row(self, row):
        """
        add "Capture Training Images" button in table at specific row.
        :param row: row number (0 -> row count - 1)
        :return:
        """
        btn = QPushButton("Capture Training Images")
        btn.clicked.connect(lambda: self.capture_images(row))
        self.studentsTable.setCellWidget(row, 3, btn)

    def take_attendance(self):
        """
        take / end attendance button handler
        :return:
        """
        if self.attendanceBtn.text() == "Take Attendance":
            students = self.get_students()
            self.takeAttendance.emit(students)
            self.attendanceBtn.setText("Finish")
        else:
            self.endAttendance.emit()
            self.attendanceBtn.setText("Take Attendance")

    def _save_attendance_btn_clicked(self):
        fileName = QFileDialog.getSaveFileName(None, "Save Attendance", "/", "(*.csv);;")
        fileName = fileName[0]
        with open(fileName, "w", newline='') as fileOutput:
            writer = csv.writer(fileOutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in range(self.attendanceTable.rowCount() - 1):
                if row == 0:
                    fields = []
                    for col in range(0, self.attendanceTable.columnCount()):
                        fields.append(self.attendanceTable.horizontalHeaderItem(col).text())
                    writer.writerow(fields)
                fields = []
                for col in range(self.attendanceTable.columnCount()):
                    fields.append(self.attendanceTable.item(row, col).text())
                writer.writerow(fields)
            row += 1
            fields = [self.attendanceTable.item(row, 0).text(), "", self.attendanceTable.item(row, 2).text()]
            writer.writerow(fields)


    def get_students(self):
        """
        :return: studnet in the table (id -> name)
        """
        students = {}
        for row in range(self.studentsTable.rowCount()):
            students[int(self.studentsTable.item(row, 0).text())] = self.studentsTable.item(row, 1).text()
        return students

    def set_attendance(self, data):
        """
        load studnet attendance in attendance table.
        :param data: students data
        :return:
        """
        noOfUnmasked = 0
        self.attendanceTable.setRowCount(0)
        row = 0
        for id in data:
            self.attendanceTable.insertRow(row)
            item = QTableWidgetItem(id)
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.attendanceTable.setItem(row, 0, item)
            item = QTableWidgetItem(data[id]["name"])
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.attendanceTable.setItem(row, 1, item)
            item = QTableWidgetItem()
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            if data[id]["masked"]:
                item.setText("Yes")
                item.setBackgroundColor(QColor(0, 255, 0))
            else:
                item.setText("No")
                item.setBackgroundColor(QColor(255, 0, 0))
                noOfUnmasked += 1
            self.attendanceTable.setItem(row, 2, item)
            item = QTableWidgetItem(data[id]["time"])
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            self.attendanceTable.setItem(row, 3, item)
            row += 1
        self.attendanceTable.insertRow(row)
        item = QTableWidgetItem("Total percentage of unmasked students:")
        self.attendanceTable.setSpan(row, 0, 1, 2)
        self.attendanceTable.setItem(row, 0, item)
        perc = noOfUnmasked / (self.attendanceTable.rowCount() - 1) * 100
        item = QTableWidgetItem(str(perc) + "%")
        if perc >= 50:
            item.setBackgroundColor(QColor(255, 0, 0))
        elif 30 <= perc < 50:
            item.setBackgroundColor(QColor(255, 255, 0))
        elif perc < 30:
            item.setBackgroundColor(QColor(0, 255, 0))
        self.attendanceTable.setSpan(row, 2, 1, 2)
        self.attendanceTable.setItem(row, 2, item)

    def _save_btn_clicked(self):
        self.write_csv()

    def load_csv(self):
        """
        load students data from CSV file
        :return:
        """
        with open(self.csvFileName) as fileInput:
            row = 0
            for rowData in csv.reader(fileInput, delimiter=','):
                for col in range(len(rowData)):
                    if row == 0:
                        self.studentsTable.setHorizontalHeaderItem(col, QTableWidgetItem(rowData[col]))
                    else:
                        if col == 0:
                            self.studentsTable.insertRow(row - 1)
                        item = QTableWidgetItem(rowData[col])
                        self.studentsTable.setItem(row - 1, col, item)
                if row != 0:
                    self._add_btn_at_row(row - 1)
                row += 1

    def write_csv(self):
        """
        save students data into CSV file
        :return:
        """
        with open(self.csvFileName, "w", newline='') as fileOutput:
            writer = csv.writer(fileOutput, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in range(self.studentsTable.rowCount()):
                if row == 0:
                    fields = []
                    for col in range(0, self.studentsTable.columnCount() - 1):
                        fields.append(self.studentsTable.horizontalHeaderItem(col).text())
                    writer.writerow(fields)
                fields = []
                for col in range(0, self.studentsTable.columnCount() - 1):
                    fields.append(self.studentsTable.item(row, col).text())
                writer.writerow(fields)

    def capture_images(self, row):
        """
        capture button clicked
        :param row: row number
        :return:
        """
        id = int(self.studentsTable.item(row, 0).text())
        name = self.studentsTable.item(row, 1).text()
        self.captureImages.emit(id, name)
