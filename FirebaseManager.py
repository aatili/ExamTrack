import firebase_admin
from firebase_admin import credentials, db, storage

import os
import shutil

from StudentData import *

# Constants
CACHE_FOLDER_DOWNLOAD = '\\cachedPictures'
IMG_NOT_FOUND = "Resources/no_pic.png"
CACHE_FOLDER_LOCAL = 'cachedPictures/'

FIREBASE_IMAGES_PATH = 'Images'
FIREBASE_EXAMS_PATH = 'Exams'
FIREBASE_NOTES_PATH = 'Exams/Notes'


class FirebaseManager:

    def __init__(self):
        self.cred = credentials.Certificate("serviceAccountKey.json")
        try:
            self.exam_app = firebase_admin.initialize_app(self.cred, {
                'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
                'storageBucket': "examfacerecognition.appspot.com"} , name="ExamApp")
        except firebase_admin.exceptions.FirebaseError as e:
            # Handle Firebase initialization error
            print("Firebase initialization error:", e)

        self.bucket = storage.bucket(app=self.exam_app)
        self.images_list = self.get_image_list()

    # cache images
    def cache_files_from_firebase(self, c_dir):
        current_directory = os.getcwd()
        cache_dir = current_directory + c_dir

        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        students_id_list = students.student_table_ids()
        for s_id in students_id_list:
            blob = self.bucket.get_blob(f'{FIREBASE_IMAGES_PATH}/{s_id}.png')
            if blob is None:  # no picture retrieved from database
                continue
            # Construct local file path
            local_file_path = os.path.join(cache_dir, f'{s_id}.png')
            print(local_file_path)
            # Download file from Firebase Storage to local cache
            blob.download_to_filename(local_file_path)

    def get_csv_file(self, exam_no, exam_term):
        blob = self.bucket.get_blob(f'{FIREBASE_EXAMS_PATH}/{exam_no}_{exam_term}.csv')
        if blob is None:
            return "Exam Error", "Exam was not found in database make sure input is correct or upload a file."
        csv_data = blob.download_as_string()
        if not students.read_students_blob(csv_data):
            return "Exam Error", "Failed to read file."
        if not students.check_csv_struct():
            return "Exam Error", "File structure does not match."
        return True

    # Get student image path
    def get_image_path(self, student_id):
        current_directory = os.getcwd()
        cache_dir = current_directory + CACHE_FOLDER_DOWNLOAD
        file_path = os.path.join(cache_dir, f'{student_id}.png')
        if os.path.exists(file_path):
            return file_path
        return IMG_NOT_FOUND

    def get_image_list(self):
        b_list = self.bucket.list_blobs(prefix=FIREBASE_IMAGES_PATH)
        img_list = []
        for blob in b_list:
            img_list.append(os.path.basename(blob.name))
        return img_list

    def update_images_list(self):
        students_id_list = students.student_table_ids()
        temp_list = self.images_list.copy()
        for img in temp_list:
            temp_id = img.split(".")[0]
            if temp_id not in students_id_list:
                self.images_list.remove(temp_id + '.png')


    # GETS PICTURE FROM FIREBASE
    '''def get_student_image(self, student_id):
        blob = self.bucket.get_blob(f'Images/{student_id}.png')
        if blob is None:  # no picture found
            return blob
        else:  # convert and display picture
            img_data = np.frombuffer(blob.download_as_string(), np.uint8)
            img_cvt = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
            img_cvt = cv2.cvtColor(img_cvt, cv2.COLOR_BGR2RGB)
            return Image.fromarray(img_cvt)
    '''

firebase_manager = FirebaseManager()

print(firebase_manager.images_list)
