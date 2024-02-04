from tkinter import *
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
import tkinter as tk
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


LARGE_FONT = ("Verdana", 12)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame("StartPage"))
        button1.pack()

        button2 = tk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame("PageTwo"))
        button2.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bgimg = tk.PhotoImage(file = "../Resources/new_background.png")

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


        # Creating Profile

        self.profile_gui = tk.PhotoImage(file = "../Resources/profile_ui.png")
        canvas.create_image(20,20,anchor=NW,image=self.profile_gui)

        self.profile_pic_frame_tk = tk.PhotoImage(file = "../Resources/pic_frame.png")
        canvas.create_image(58,58,anchor=NW,image=self.profile_pic_frame_tk)

        self.profile_pic_tk = tk.PhotoImage(file = "../Resources/no_pic.png")
        profile_pic = canvas.create_image(60,60,anchor=NW,image=self.profile_pic_tk)



        student_name_label = canvas.create_text(
            115.0,
            295.0,
            anchor="nw",
            text="No Name",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )


        student_id_label = canvas.create_text(
            115.0,
            335.0,
            anchor="nw",
            text="999999",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_major_label = canvas.create_text(
            115.0,
            373.0,
            justify=CENTER,
            anchor="nw",
            text="No Major",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_extra_time_label = canvas.create_text(
            90.0,
            430.0,
            justify=CENTER,
            anchor="nw",
            text="No Extra Time",
            fill="#FFFFFF",
            font=("Inter Bold", 13 * -1)
        )

        student_confirmed_label = canvas.create_text(
            244.0,
            430.0,
            justify=CENTER,
            anchor="nw",
            text="Not checked",
            fill="#FFFFFF",
            font=("Inter Bold", 13 * -1)
        )

        # Creating Table

        table = ttk.Treeview(master=self, columns=table_columns, show="headings")

        for column in table_columns:
            table.heading(column=column, text=column)
            table.column(column=column, width=70)

        for row_data in table_data:
            table.insert(parent="", index="end", values=row_data)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#917FB3", fieldbackground="#917FB3", foreground="white")
        style.configure("Treeview.Heading", background="#917FB3", fieldbackground="#917FB3", foreground="white")
        style.map("Treeview", background=[("selected", "#E5BEEC")])

        table.place(x=360, y=150, height=260)


        #Selecting row in table

        table_current_row = 0
        def table_select_row(a): #0:ID , 1:First Name , 2:Last Name , 3:Extra Time , 4:Tuition , 5:Confirmed
            cur_item = table.focus()
            cur_values = table.item(cur_item)['values']
            canvas.itemconfig(student_id_label,text=cur_values[0])
            canvas.itemconfig(student_name_label,text=cur_values[1]+' '+cur_values[2])
            temp_extra_time = 'No Extra Time'
            if cur_values[3] == 'Yes':
                temp_extra_time = 'Extra Time'
            canvas.itemconfig(student_extra_time_label , text=temp_extra_time)
            temp_confirmed = 'Not Confirmed'
            if cur_values[5] == 'Yes':
                temp_confirmed = 'Confirmed'
            canvas.itemconfig(student_confirmed_label , text=temp_confirmed)
            global img_holder

            blob = bucket.get_blob(f'Images/{cur_values[0]}.png')

            if blob == None:
                img_holder = tk.PhotoImage(file = "../Resources/no_pic.png")
                canvas.itemconfig(profile_pic,image=img_holder)
            else:
                img_data = np.frombuffer(blob.download_as_string(), np.uint8)
                img_cvt = cv2.imdecode(img_data,cv2.IMREAD_COLOR)
                img_cvt = cv2.cvtColor(img_cvt, cv2.COLOR_BGR2RGB)
                img_holder = ImageTk.PhotoImage(image=Image.fromarray(img_cvt))
                canvas.itemconfig(profile_pic,image=img_holder)
            #canvas.itemconfig(l3,text=img_data)



        table.bind("<<TreeviewSelect>>", table_select_row)



        #Timers

        #time variables
        time_mins = 2
        time_mins_extra = 1
        time_mins_waiver = 1
        waiver_available = False

        minute=StringVar()
        second=StringVar()
        minute_waiver=StringVar()
        second_waiver=StringVar()

        # setting the default value as 0
        minute.set("00")
        second.set("00")
        minute_waiver.set("00")
        second_waiver.set("00")



        # Creating original timer labels
        time_left_label = canvas.create_text(
            515.0,
            75.0,
            anchor="nw",
            text="Time Left",
            fill="#FFFFFF",
            font=("Inter Bold", 11 * -1)
        )
        minute_label= Label(self, width=3, font=("Arial",14,"" , ), fg="#FFFFFF",
                           textvariable=minute, background="#917FB3")
        minute_label.place(x=500,y=90)

        seperate_time= Label(self, width=1, font=("Arial",14,"" , ), fg="#FFFFFF",
                           text=':',background="#917FB3")
        seperate_time.place(x=530,y=90)

        second_label= Label(self, width=2, font=("Arial",14,""), fg="#FFFFFF",
                           textvariable=second,background="#917FB3")
        second_label.place(x=545,y=90)

        if waiver_available:
            #Creating Waiver labels
            canvas.create_text(
                410.0,
                75.0,
                anchor="nw",
                text="Waiver Time",
                fill="#FFFFFF",
                font=("Inter Bold", 11 * -1)
            )
            minute_label_waiver= Label(self, width=3, font=("Arial",14,"" , ), fg="#FFFFFF",
                               textvariable=minute_waiver, background="#917FB3")
            minute_label_waiver.place(x=400,y=90)

            seperate_time_waiver= Label(self, width=1, font=("Arial",14,"" , ), fg="#FFFFFF",
                               text=':',background="#917FB3")
            seperate_time_waiver.place(x=430,y=90)

            second_label_waiver= Label(self, width=2, font=("Arial",14,""), fg="#FFFFFF",
                               textvariable=second_waiver,background="#917FB3")
            second_label_waiver.place(x=445,y=90)
        else:
            canvas.create_text(
                370.0,
                95.0,
                anchor="nw",
                text="No Waiver Option",
                fill="#FFFFFF",
                font=("Inter Bold", 14 * -1)
            )


        def exam_timer(time_mins,minute,second,extra,waiver_flag):
                temp = time_mins * 60
                temp_waiver = time_mins_waiver * 60
                while temp >-1:
                    #divmod(firstvalue = temp//60, secondvalue = temp%60)
                    mins,secs = divmod(temp,60)

                    if waiver_flag == 0:
                        mins_waiver,secs_waiver =  divmod(temp_waiver,60)

                    # using format () method to store the value up to
                    # two decimal places
                    minute.set("{:02d}".format(mins))
                    second.set("{:02d}".format(secs))

                    if(waiver_flag == 0):
                        minute_waiver.set("{:02d}".format(mins_waiver))
                        second_waiver.set("{:02d}".format(secs_waiver))


                    # updating the GUI window after decrementing the
                    # temp value every time

                    self.update()
                    time.sleep(1)

                    # when temp value = 0; then a messagebox pop's up
                    # with a message:"Time's up"
                    if (temp_waiver==0):
                        if not extra and waiver_available and waiver_flag == 0:
                            messagebox.showinfo("Time Countdown", "Waiver Time is up ")
                            waiver_flag = 1

                    if (temp == 0):
                        if extra:
                            messagebox.showinfo("Time Countdown", "Extra Time is up ")
                        else:
                            messagebox.showinfo("Time Countdown", "Original Time is up ")

                    # after every one sec the value of temp will be decremented
                    # by one
                    temp -= 1
                    if waiver_flag == 0:
                        temp_waiver -= 1

        def start_timers():
            start_btn["state"] = "disabled"
            waiver_flag = 1  #no waiver available
            if waiver_available:
                waiver_flag = 0
            exam_timer(time_mins , minute , second, 0 , waiver_flag) #original timer
            canvas.itemconfig(time_left_label, text = 'Extra Time')
            exam_timer(time_mins_extra , minute , second , 1, 1) #extra time timer

        # start exams/timers button
        start_btn = Button(self, text='Start Exam', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                           activebackground='#917FB3',height='1',width='14',command= start_timers)
        start_btn.place(x = 650,y = 90)



        face_recognition_btn = Button(self, text='Face Recognition', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                                      activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14')

        face_recognition_btn.place(x = 950,y = 90)


        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame("StartPage"))
        button1.pack()

        button2 = tk.Button(self, text="Page One",
                            command=lambda: controller.show_frame("PageOne"))
        button2.pack()

