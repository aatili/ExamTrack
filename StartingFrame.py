from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox
import time
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
import cv2
import firebase_admin
from firebase_admin import credentials, db, storage

import UserInterface
import FaceRecFrame


# Class used to transition between tkinter pages
class ExamApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.resizable(False, False)
        self.title("Exam App")
        self.geometry("1200x600+20+20")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, FaceRecFrame.FaceRec, UserInterface.UserInterface):

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
        self.bgimg = tk.PhotoImage(file = "Resources/start_background.png")

        # Creating Canvas
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

        # Trying something
        self.cap = None
        self.selected_device = 0
        self.capture_running = False
        self.camera_waiting_small = tk.PhotoImage(file = "Resources/camera_waiting_small.png")

        # Function to start capture loop
        def start_rec():
            def scan():
                success, self.img = self.cap.read()
                if success:
                    # convert to RGB
                    self.img_arr = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
                    # converting to img
                    self.img = Image.fromarray(self.img_arr)
                    self.tkimg = ImageTk.PhotoImage(self.img)
                    panel.config(image=self.tkimg)
                    panel.tkimg = self.tkimg
                if self.capture_running:
                    panel.after(25, scan)  # change value to adjust FPS

            if not self.capture_running:
                self.cap = cv2.VideoCapture(0)
                self.cap.set(3, 240*0.75)
                self.cap.set(4, 180*0.75)
                self.capture_running = True
                scan()  # start the capture loop
            else:
                print('capture already started')

        # Create the label with the image
        panel = tk.Label(self)
        panel.place(x=900, y=200)
        panel.configure(image=self.camera_waiting_small)
        panel.tkraise()

        if self.cap:
            self.cap.release()

        def pause_rec():
            self.capture_running = False
            if self.cap is not None:
                self.cap.release()
            panel.configure(image=self.camera_waiting_small)

        # Get available camera devices
        available_devices = []
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_devices.append('Camera ' + str(i))
            cap.release()

        def combo_cameras_changed(a):
            pause_rec()
            self.selected_device = combo_cameras.get()

        canvas.create_text(
            795.0,
            165.0,
            anchor="nw",
            text="Select Camera:",
            fill="white",
            font=("Inter Bold", 15 * -1)
        )

        # Create ComboBox to select camera device
        combo_cameras = ttk.Combobox(self, values=available_devices)
        combo_cameras.place(x=900,y=165)
        self.selected_device = combo_cameras.get()

        combo_cameras.bind("<<ComboboxSelected>>", combo_cameras_changed)

        # continue btn
        test_btn = Button(self, text='Test', bd='5',fg="#FFFFFF" ,bg='#812e91',font=("Calibri", 12 * -1),
                              activebackground='#917FB3',height='1',width='10', command=start_rec)
        test_btn.place(x=950, y=360)

        # End

        button = tk.Button(self, text="Face Recognition",
                            command=lambda: controller.show_frame("FaceRec"))
        button.pack(side='bottom')

        button2 = tk.Button(self, text="User Interface",
                            command=lambda: controller.show_frame("UserInterface"))
        button2.pack(side='bottom')

        # Adding labels and entries

        canvas.create_text(
            400.0,
            150.0,
            anchor="nw",
            text="Exam Number:",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        exam_entry = tk.Entry(self, width=13, bg="#917FB3", font=18, borderwidth=3)
        exam_entry.place(x=525, y=145)

        canvas.create_text(
            400.0,
            200.0,
            anchor="nw",
            text="Term:",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        # creating combo box
        combo_terms = ttk.Combobox(self, state="readonly", values=['MoedA', 'MoedB', 'Special'],
                                   foreground="#917FB3", font=("Calibri", 18 * -1), width=10)
        combo_terms.place(x=525, y=198)

        canvas.create_text(
            400.0,
            250.0,
            anchor="nw",
            text="Duration:",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        duration_entry = tk.Entry(self, width=4, bg="#917FB3", font=18, borderwidth=3)
        duration_entry.place(x=525, y=245)

        canvas.create_text(
            585.0,
            250.0,
            anchor="nw",
            text="Minutes",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        canvas.create_text(
            400.0,
            300.0,
            anchor="nw",
            text="Supervisors:",
            fill="white",
            font=("Inter Bold", 18 * -1)
        )

        self.supervisor_num = 2

        def exam_add_supervisor():
            self.supervisor_num += 1
            if self.supervisor_num % 4 == 1:
                supervisor_entry2.place_forget()
                supervisor_entry3.place_forget()
                supervisor_entry4.place_forget()
            elif self.supervisor_num % 4 == 2:
                supervisor_entry2.place(x=525, y=345)
                supervisor_entry3.place_forget()
                supervisor_entry4.place_forget()
            elif self.supervisor_num % 4 == 3:
                supervisor_entry2.place(x=525, y=345)
                supervisor_entry3.place(x=525, y=395)
                supervisor_entry4.place_forget()
            elif self.supervisor_num % 4 == 0:
                supervisor_entry2.place(x=525, y=345)
                supervisor_entry3.place(x=525, y=395)
                supervisor_entry4.place(x=525, y=445)

        supervisor_entry = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        supervisor_entry.place(x=525, y=295)

        supervisor_entry2 = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        supervisor_entry2.place(x=525, y=345)

        supervisor_entry3 = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        # supervisor_entry3.place(x=525,y=445)

        supervisor_entry4 = tk.Entry(self, width=20, bg="#917FB3", font=18, borderwidth=3)
        # supervisor_entry.place(x=525,y=495)

        add_sup_btn = Button(self, text='+', bd='3', fg="#FFFFFF", bg='#812e91', font=("Arial", 16 * -1),
                             activebackground='#917FB3', height='1', width='2', command=exam_add_supervisor)
        add_sup_btn.place(x=770, y=295)

        '''remove_sup_btn = Button(self, text='-', bd='3',fg="#FFFFFF" ,bg='#812e91',font=("Arial", 16 * -1),
                                activebackground='#917FB3',height='1',width='2')
        remove_sup_btn.place(x=770,y=395)'''

        # continue btn
        continue_btn = Button(self, text='Continue', bd='5',fg="#FFFFFF" ,bg='#812e91',font=("Calibri", 16 * -1),
                              activebackground='#917FB3',height='1',width='14')
        continue_btn.place(x=800, y=480)


app = ExamApp()
app.mainloop()
