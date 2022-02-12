import os
import time
import cv2
import numpy as np
from PIL import Image
from threading import Thread


def get_data(path):
    """
    Get images from the given path
    :param path: path to images
    :return: Faces of images and ids of every face.
    """
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    ids = []
    for imagePath in imagePaths:
        image = Image.open(imagePath).convert('L')
        imageNo = np.array(image, 'uint8')
        id = int(float(os.path.split(imagePath)[-1].split(".")[1]))
        faces.append(imageNo)
        ids.append(id)
    return faces, ids


def train_model():
    """
    Train images to the model and saves it
    :return:
    """
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, ids = get_data("Training Images")
    Thread(target=recognizer.train(faces, np.array(ids))).start()
    recognizer.save("Training Images Labels" + os.sep + "Trainner.yml")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces, ids = get_data("Training Mask Images")
    Thread(target=recognizer.train(faces, np.array(ids))).start()
    recognizer.save("Training Images Labels" + os.sep + "Mask Trainner.yml")
