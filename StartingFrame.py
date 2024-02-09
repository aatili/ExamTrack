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



exam_number = "1"
room_number = "102"



#Class used to transition between Classes (tkinter pages)
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
        self.bgimg = tk.PhotoImage(file = "Resources/new_background.png")

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


        button = tk.Button(self, text="Face Recognition",
                            command=lambda: controller.show_frame("FaceRec"))
        button.pack()

        button2 = tk.Button(self, text="User Interface",
                            command=lambda: controller.show_frame("UserInterface"))
        button2.pack()



app = ExamApp()
app.mainloop()
