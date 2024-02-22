import cv2
import os
import face_recognition
import pickle

import FirebaseManager


class EncodePhotos:
    def __init__(self):
        # Importing student images
        self.image_folder = FirebaseManager.CACHE_FOLDER_LOCAL
        self.image_file_list = []
        self.image_list = []
        self.student_ids = []
        self.encode_list = []

    def create_img_list(self):
        self.image_file_list = os.listdir(self.image_folder)
        for image_file in self.image_file_list:
            self.image_list.append(cv2.imread(os.path.join(self.image_folder, image_file)))
            self.student_ids.append(os.path.splitext(image_file)[0])

    def find_encodings(self):
        for image in self.image_list:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(image)[0]
            self.encode_list.append(encode)

    def encode_images(self):
        print("Encoding images....")
        self.find_encodings()
        encode_and_ids_list = [self.encode_list, self.student_ids]
        print("Encoding done.")

        encode_file = open("EncodeFile.p", 'wb')
        pickle.dump(encode_and_ids_list, encode_file)
        encode_file.close()
        print("Encode file saved.")


encode_photos = EncodePhotos()

