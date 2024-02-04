from tkinter import *
import tkinter as tk
# Explicit imports to satisfy Flake8
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from data import *
import time
import numpy as np
import cv2
from PIL import Image, ImageTk
import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
from PyQt5.QtWidgets import *
import os

import firebase_admin
from firebase_admin import credentials, db, storage

import UserInterface



# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
        'storageBucket': "examfacerecognition.appspot.com"
    })
    bucket = storage.bucket()


LARGE_FONT = ("Verdana", 12)

exam_number = "1"
room_number = "102"



#Class used to transition between Classes (tkinter pages)
class ExamApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1200x600")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, UserInterface.PageOne, UserInterface.PageTwo):

            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

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
                            y1, x2, y2, x1 = [coord * 4 for coord in face_loc]
                            bbox = 10 + x1, 10 + y1, x2 - x1, y2 - y1
                            self.img_arr = cvzone.cornerRect(self.img_arr, bbox, rt=0,colorC=(220, 60, 60))
                            self.img = Image.fromarray(self.img_arr)
                            self.tkimg = ImageTk.PhotoImage(self.img)
                            panel.config(image=self.tkimg)
                            panel.tkimg = self.tkimg
                            matches = face_recognition.compare_faces(encode_list_known, encode_face)
                            face_distances = face_recognition.face_distance(encode_list_known, encode_face)
                            match_index = np.argmin(face_distances)
                            if matches[match_index]: #face recognized
                                y1, x2, y2, x1 = [coord * 4 for coord in face_loc]
                                bbox = 10 + x1, 10 + y1, x2 - x1, y2 - y1
                                student_id = student_ids[match_index]
                                self.img_arr = cvzone.cornerRect(self.img_arr, bbox, rt=0)
                                self.img = Image.fromarray(self.img_arr)
                                self.tkimg = ImageTk.PhotoImage(self.img)
                                panel.config(image=self.tkimg)
                                panel.tkimg = self.tkimg
                                #print(student_id)

                                blob = bucket.get_blob(f'Images/{student_id}.png')

                                if blob == None:
                                    self.img_holder = tk.PhotoImage(file = "Resources/no_pic.png")
                                    canvas.itemconfig(profile_pic,image=self.img_holder)
                                else:
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


        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = tk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame("PageOne"))
        button.pack()

        button2 = tk.Button(self, text="Visit Page 2",
                            command=lambda: controller.show_frame("PageTwo"))
        button2.pack()


        magic_btn = Button(self, text='Start', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                           activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14',command=start_rec)
        magic_btn.place(x = 750,y = 520)
        magic_btn.tkraise()


app = ExamApp()
app.mainloop()
