from tkinter import *
import tkinter as tk
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox
from PIL import Image, ImageTk
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone

import firebase_admin
from firebase_admin import credentials, db, storage

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
face_rec_app = firebase_admin.initialize_app(cred, {
    'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "examfacerecognition.appspot.com"}, name="FaceRecApp")
bucket = storage.bucket(app=face_rec_app)



LARGE_FONT = ("Verdana", 12)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.bgimg = tk.PhotoImage(file = "Resources/new_background.png")
        self.camera_waiting = tk.PhotoImage(file = "Resources/camera_waiting.png")

        # Creating Cancvas
        canvas = Canvas(
            self,
            bg = "#2A2F4F",
            height = 600,
            width = 1200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.create_image(0,0,anchor=NW,image=self.bgimg)

        canvas.place(x = 0, y = 0)


        # Load encode file
        print("Loading encode file...")
        with open('EncodeFile.p', 'rb') as encode_file:
            encode_list_with_ids = pickle.load(encode_file)
        encode_list_known, student_ids = encode_list_with_ids
        print("Encode file loaded.")

        self.imgholder = tk.PhotoImage(file = "Resources/no_pic.png")


        self.profile_pic_frame_tk = tk.PhotoImage(file = "Resources/pic_frame.png")
        canvas.create_image(58,58,anchor=NW,image=self.profile_pic_frame_tk)

        profile_pic = canvas.create_image(60,60,anchor=NW,image=self.imgholder)


        # Define a practical font for putText
        font = cv2.FONT_HERSHEY_TRIPLEX

        self.cap = None

        def start_rec():
            def scan():
                success, self.img = self.cap.read()
                if success:
                    # Resize and convert to RGB
                    self.img_arr = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
                    self.img_small = cv2.resize(self.img, (0, 0), None, 0.25, 0.25)

                    # Find and encode faces
                    face_locations = face_recognition.face_locations(self.img_small)
                    face_encodings = face_recognition.face_encodings(self.img_small, face_locations)

                    #converting to img and displaying
                    self.img = Image.fromarray(self.img_arr)
                    self.tkimg = ImageTk.PhotoImage(self.img)
                    panel.config(image=self.tkimg)
                    panel.tkimg = self.tkimg # save a reference to the image to avoid garbage collection

                    #face detected
                    if face_locations:
                        for encode_face, face_loc in zip(face_encodings, face_locations):
                            #addring red rectangle over face
                            y1, x2, y2, x1 = [coord * 4 for coord in face_loc]
                            bbox = 10 + x1, 10 + y1, x2 - x1, y2 - y1
                            self.img_arr = cvzone.cornerRect(self.img_arr, bbox, rt=0,colorC=(220, 60, 60))
                            #converting to img
                            self.img = Image.fromarray(self.img_arr)
                            self.tkimg = ImageTk.PhotoImage(self.img)
                            panel.config(image=self.tkimg)
                            panel.tkimg = self.tkimg
                            matches = face_recognition.compare_faces(encode_list_known, encode_face)
                            face_distances = face_recognition.face_distance(encode_list_known, encode_face)
                            match_index = np.argmin(face_distances)
                            if matches[match_index]: #face recognized
                                #addring green rectangle over face
                                y1, x2, y2, x1 = [coord * 4 for coord in face_loc]
                                bbox = 10 + x1, 10 + y1, x2 - x1, y2 - y1
                                student_id = student_ids[match_index]
                                #converting to img
                                self.img_arr = cvzone.cornerRect(self.img_arr, bbox, rt=0)
                                self.img = Image.fromarray(self.img_arr)
                                self.tkimg = ImageTk.PhotoImage(self.img)
                                panel.config(image=self.tkimg)
                                panel.tkimg = self.tkimg
                                #getting picture from database
                                blob = bucket.get_blob(f'Images/{student_id}.png')

                                if blob == None: #no picture found
                                    self.img_holder = tk.PhotoImage(file = "Resources/no_pic.png")
                                    canvas.itemconfig(profile_pic,image=self.img_holder)
                                else: #convert and display picture
                                    img_data = np.frombuffer(blob.download_as_string(), np.uint8)
                                    img_cvt = cv2.imdecode(img_data,cv2.IMREAD_COLOR)
                                    img_cvt = cv2.cvtColor(img_cvt, cv2.COLOR_BGR2RGB)
                                    self.img_holder = ImageTk.PhotoImage(image=Image.fromarray(img_cvt))
                                    canvas.itemconfig(profile_pic,image=self.img_holder)


                panel.after(25, scan) # change value to adjust FPS

            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                self.cap.set(3, 640)
                self.cap.set(4, 480)
                scan() # start the capture loop
            else:
                print('capture already started')

        panel = tk.Label(self)
        panel.place(x=500,y=10)
        panel.configure(image=self.camera_waiting)
        panel.tkraise()

        if self.cap:
            self.cap.release()

        def pause_rec():
            if self.cap:
                self.cap.release()
            self.cap=None
            panel.configure(image=self.camera_waiting)

        back_btn = tk.Button(self, text="Back", bd='5',fg="#FFFFFF" ,bg='#910ac2',
                            activebackground='#917FB3',font=("Calibri", 14 * -1),height='1',width='14',
                             command=lambda: [pause_rec(),controller.show_frame("PageTwo")])
        back_btn.place(x = 20,y = 10)


        magic_btn = Button(self, text='Start', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                           activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14',command=start_rec)
        magic_btn.place(x = 750,y = 520)

        #Confirm or Cancel Attendance once student recognized

        def confirm_func():
            return 0

        def cancel_func():
            return 1

        confirm_btn = Button(self, text='Confirm', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                           activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14',command=confirm_func)
        confirm_btn.place(x = 270,y = 475)

        cancel_btn = Button(self, text='Cancel', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                           activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14',command=cancel_func)
        cancel_btn.place(x = 270,y = 520)

