import cv2
import os
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials, db, storage

# Initialize Firebase
firebase_credentials = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(firebase_credentials, {
    'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "examfacerecognition.appspot.com"
})

# Importing student images
image_folder = 'Images'
image_file_list = os.listdir(image_folder)
image_list = []
student_ids = []

for image_file in image_file_list:
    image_list.append(cv2.imread(os.path.join(image_folder, image_file)))
    student_ids.append(os.path.splitext(image_file)[0])


def find_encodings(images_list):
    encode_list = []
    for image in images_list:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encode_list.append(encode)

    return encode_list

print("Encoding images....")
encode_list = find_encodings(image_list)
encode_and_ids_list = [encode_list, student_ids]
print("Encoding done.")

encode_file = open("EncodeFile.p", 'wb')
pickle.dump(encode_and_ids_list, encode_file)
encode_file.close()
print("Encode file saved.")
