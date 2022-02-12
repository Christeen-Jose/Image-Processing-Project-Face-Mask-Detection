import csv
import cv2
import os
import time
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from datetime import datetime

threshold = 67  # percentage

"""
    Responsible for interfacing with web cam and the logic envolving the camera
    The class is a QThead that runs in the background and emits the image to be shown in the GUI
"""


class Camera(QThread):
    updateImage = Signal(str, QImage, dict)  # Title, image

    def set_method(self, name, params={}):
        """
        :param name:  Method (function_ required to run the background
        :param params: the parameters of that method
        :return: None
        """
        self.name = name
        self.params = params

    def run(self):
        """
        Thread main function that calls the method set using set_method function
        :return: None
        """
        self.isActive = True
        if self.name == "test_and_detect":
            self.test_and_detect()
        elif self.name == "capture_training_images":
            self.capture_training_images(self.params["name"], self.params["id"])
        elif self.name == "capture_mask_training_images":
            self.capture_training_images(self.params["name"], self.params["id"], "Training Mask Images")
        elif self.name == "recognize_attendence":
            self.recognize_attendence(self.params["students"])

    def test_and_detect(self):
        """
        tests the camera and detect the faces and add square around them
        :return: None
        """
        # Load the cascade
        cascadeFace = cv2.CascadeClassifier('haarcascade_default.xml')

        # Capture the video from webcam
        cam = cv2.VideoCapture(0)

        while self.isActive:
            _, image = cam.read()

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            faces = cascadeFace.detectMultiScale(gray, 1.3, 5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

            for (p1, p2, p3, p4) in faces:
                cv2.rectangle(image, (p1, p2), (p1 + p3, p2 + p4), (0, 0, 255), 2)  # BGR

            self.emit_image('Test Camera', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.emit_image('', None)
        cam.release()
        cv2.destroyAllWindows()

    def capture_training_images(self, name: str, id: int, path="Training Images"):
        """
        capture the training images (basic or masked) for a particular student.
        :param name: Student name
        :param id: Student ID (the handling of unique is from other class)
        :param path: path to save pictures at
        :return:
        """
        if name.replace(" ", "").isalpha():
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            detector = cv2.CascadeClassifier("haarcascade_default.xml")
            imageNo = 0

            while self.isActive:
                _, image = cam.read()
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

                for (x, y, w, h) in faces:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # BGR
                    imageNo += 1
                    cv2.imwrite(path + os.sep + name + "." + str(id) + '.' +
                                str(imageNo) + ".jpg", gray[y: y + h, x: x + w])

                self.emit_image("Capturing " + path, image, {"id": str(id), "name": name})

                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                if imageNo > 100:
                    break

            cam.release()
            cv2.destroyAllWindows()
            self.emit_image('', None)

            row = [id, name]

            return row

    def recognize_attendence(self, students: dict):
        """
        recognize the attendance
        :param students: Students id -> name
        :return:
        """
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("Training Images Labels" + os.sep + "Trainner.yml")
        recognizerMask = cv2.face.LBPHFaceRecognizer_create()
        recognizerMask.read("Training Images Labels" + os.sep + "Mask Trainner.yml")
        harcascadePath = "haarcascade_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cam.set(3, 640)
        cam.set(4, 480)
        minWidth = 0.1 * cam.get(3)
        minHight = 0.1 * cam.get(4)

        while self.isActive:
            data = {"isAttendance": True}
            ret, image = cam.read()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5,
                                                 minSize=(int(minWidth), int(minHight)), flags=cv2.CASCADE_SCALE_IMAGE)
            masked = False
            for (p1, p2, p3, p4) in faces:
                cv2.rectangle(image, (p1, p2), (p1 + p3, p2 + p4), (0, 0, 255), 2)  # BGR
                id, conf = recognizerMask.predict(gray[p2: p2 + p4, p1: p1 + p3])
                if 100 - conf <= 65:
                    id, conf = recognizer.predict(gray[p2: p2 + p4, p1: p1 + p3])
                else:
                    masked = True
                imageText = ""
                if 100 - conf > 0:
                    name = students[id]
                    confstr = "  {0}%".format(round(100 - conf))
                    imageText = str(id)
                    data["id"] = str(id)
                    data["name"] = name
                    now = datetime.now()
                    data["time"] = now.strftime("%H:%M:%S")
                    if masked:
                        imageText += " [Masked]"
                        data["masked"] = True
                    else:
                        imageText += " [Not Masked]"
                        data["masked"] = False
                else:
                    imageText = "\tUnknown\t"
                    confstr = "  {0}%".format(round(100 - conf))

                if 100 - conf > threshold:
                    ts = time.time()

                cv2.putText(image, str(imageText), (p1 + 5, p2 - 5), font, 1, (255, 255, 255), 2)

                if (100 - conf) > threshold:
                    cv2.putText(image, str(confstr), (p1 + 5, p2 + p4 - 5), font, 1, (0, 255, 0), 1)
                elif (100 - conf) > 50:
                    cv2.putText(image, str(confstr), (p1 + 5, p2 + p4 - 5), font, 1, (0, 255, 255), 1)
                else:
                    cv2.putText(image, str(confstr), (p1 + 5, p2 + p4 - 5), font, 1, (0, 0, 255), 1)

            self.emit_image("Taking Attendance", image, data)
            if cv2.waitKey(1) == ord('q'):
                break

        cam.release()
        cv2.destroyAllWindows()
        self.emit_image('', None)

    def emit_image(self, title, image, data={}):
        """
        emits the image to be shown in the GUI
        :param title: Image title
        :param image: Image to show
        :param data: Extra data (name, id, is masked, etc)
        :return:
        """
        if image is not None:
            height, width, bytesPerComponent = image.shape
            bytesPerLine = bytesPerComponent * width
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            imageConversion = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
            # qtImage = imageConversion.scaled(640, 480, Qt.KeepAspectRatio)
            self.updateImage.emit(title, imageConversion, data)
        else:
            self.updateImage.emit('', QImage(), data)

    def stop(self):
        """
        stops the thread from running.
        :return:
        """
        self.emit_image('', None)
        self.isActive = False
        self.quit()

