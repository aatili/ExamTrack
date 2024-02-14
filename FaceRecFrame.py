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

from StudentData import *

cred = credentials.Certificate("serviceAccountKey.json")
try:
    # Initialize Firebase
    face_rec_app = firebase_admin.initialize_app(cred, {
        'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
        'storageBucket': "examfacerecognition.appspot.com"}, name="FaceRecApp")
except firebase_admin.exceptions.FirebaseError as e:
    # Handle Firebase initialization error
    print("Firebase initialization error:", e)

bucket = storage.bucket(app=face_rec_app)



LARGE_FONT = ("Verdana", 12)

class FaceRec(tk.Frame):

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

        # Creating Profile

        self.profile_gui = tk.PhotoImage(file = "Resources/profile_ui2.png")
        canvas.create_image(120,20,anchor=NW,image=self.profile_gui)

        #adding profile pic
        self.imgholder = tk.PhotoImage(file = "Resources/not_rec.png")

        self.profile_pic_frame_tk = tk.PhotoImage(file = "Resources/pic_frame.png")
        canvas.create_image(158,58,anchor=NW,image=self.profile_pic_frame_tk)

        profile_pic = canvas.create_image(160,60,anchor=NW,image=self.imgholder)

        #adding labels
        student_name_label = canvas.create_text(
            215.0,
            295.0,
            anchor="nw",
            text="(Name)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )


        student_id_label = canvas.create_text(
            215.0,
            335.0,
            anchor="nw",
            text="(ID)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_major_label = canvas.create_text(
            215.0,
            373.0,
            justify=CENTER,
            anchor="nw",
            text="(Major)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_extra_time_label = canvas.create_text(
            190.0,
            430.0,
            justify=CENTER,
            anchor="nw",
            text="?",
            fill="#FFFFFF",
            font=("Inter Bold", 13 * -1)
        )

        student_confirmed_label = canvas.create_text(
            350.0,
            430.0,
            justify=CENTER,
            anchor="nw",
            text="?",
            fill="#FFFFFF",
            font=("Inter Bold", 13 * -1)
        )


        # Define a practical font for putText
        font = cv2.FONT_HERSHEY_TRIPLEX

        self.cap = None
        self.loaded_flag = 0
        self.current_id = "-1"

        #Function to start capture loop
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
                            #adding red rectangle over face
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
                            if matches[match_index] : #face recognized
                                #adding green rectangle over face
                                y1, x2, y2, x1 = [coord * 4 for coord in face_loc]
                                bbox = 10 + x1, 10 + y1, x2 - x1, y2 - y1
                                self.current_id = student_ids[match_index]
                                #converting to img
                                self.img_arr = cvzone.cornerRect(self.img_arr, bbox, rt=0)
                                self.img = Image.fromarray(self.img_arr)
                                self.tkimg = ImageTk.PhotoImage(self.img)
                                panel.config(image=self.tkimg)
                                panel.tkimg = self.tkimg

                                if self.loaded_flag==0:
                                    self.loaded_flag = 1
                                    # displaying student info
                                    canvas.itemconfig(student_id_label,text=self.current_id)
                                    canvas.itemconfig(student_name_label,
                                                      text=student_get_name(self.current_id))
                                    canvas.itemconfig(student_major_label,
                                                      text=student_get_major(self.current_id))

                                    canvas.itemconfig(student_extra_time_label,
                                                      text=' Extra Time: '+student_get_extra_time(self.current_id))
                                    '''canvas.itemconfig(student_tuition_label,
                                                      text='Paid Tuition: '+data.student_get_tuition(self.current_id))
                                    '''
                                    #getting picture from database
                                    blob = bucket.get_blob(f'Images/{self.current_id}.png')

                                    if blob == None: #no picture found
                                        self.img_holder = tk.PhotoImage(file = "Resources/no_pic.png")
                                        canvas.itemconfig(profile_pic,image=self.img_holder)
                                    else: #convert and display picture
                                        img_data = np.frombuffer(blob.download_as_string(), np.uint8)
                                        img_cvt = cv2.imdecode(img_data,cv2.IMREAD_COLOR)
                                        img_cvt = cv2.cvtColor(img_cvt, cv2.COLOR_BGR2RGB)
                                        self.img_holder = ImageTk.PhotoImage(image=Image.fromarray(img_cvt))
                                        canvas.itemconfig(profile_pic,image=self.img_holder)


                                    # enabling confirm/cancel buttons
                                    confirm_btn["state"] = "normal"
                                    cancel_btn["state"] = "normal"


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

        back_btn = tk.Button(self, text="Back", bd='5',fg="#FFFFFF" ,bg='#812e91',
                            activebackground='#917FB3',font=("Calibri", 14 * -1),height='1',width='14',
                             command=lambda: [pause_rec(),controller.show_frame("UserInterface")])
        back_btn.place(x = 20,y = 10)


        magic_btn = Button(self, text='Start', bd='5',fg="#FFFFFF" ,bg='#812e91',
                           activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14',command=start_rec)
        magic_btn.place(x = 750,y = 520)

        # Confirm or Cancel Attendance once student recognized

        def rec_confirm_func(student_id): # mode: confirm 1, cancel 0
            self.imgholder = tk.PhotoImage(file = "Resources/not_rec.png")
            canvas.itemconfig(profile_pic,image=self.imgholder)
            self.loaded_flag = 0
            confirm_btn["state"] = "disabled"
            cancel_btn["state"] = "disabled"
            if student_check_attendance(student_id):
                messagebox.showinfo("Confirm Message", "Student has been confirmed already.", parent=self)
            else:
                student_auto_confirm_attendance(student_id)
            print(student_check_attendance(student_id))
            self.current_id = -1
            reset_profile_labels()

        def rec_dismiss_function():
            self.imgholder = tk.PhotoImage(file = "Resources/not_rec.png")
            canvas.itemconfig(profile_pic,image=self.imgholder)
            self.loaded_flag = 0
            self.current_id = -1
            reset_profile_labels()

        def reset_profile_labels():
            canvas.itemconfig(student_id_label,text="(ID)")
            canvas.itemconfig(student_name_label,text="(Name)")
            canvas.itemconfig(student_major_label,text="(Major)")
            canvas.itemconfig(student_extra_time_label,text="?")
            #canvas.itemconfig(student_tuition_label,text="?")


        confirm_btn = Button(self, text='Confirm', bd='5',fg="#FFFFFF" ,bg='#812e91',state="disabled",
                           activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14'
                             ,command=lambda: rec_confirm_func(self.current_id))
        confirm_btn.place(x = 270,y = 475)

        cancel_btn = Button(self, text='Dismiss', bd='5',fg="#FFFFFF" ,bg='#812e91',state="disabled",
                           activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14'
                            ,command=rec_dismiss_function)
        cancel_btn.place(x = 270,y = 520)

