from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox,scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
import cv2
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import date,datetime

from StudentData import *

import BreaksFeature
import NotesFeature
import ManualConfirmFeature



cred = credentials.Certificate("serviceAccountKey.json")
ui_app = firebase_admin.initialize_app(cred, {
    'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "examfacerecognition.appspot.com"} , name="UserInterfaceApp")
bucket = storage.bucket(app=ui_app)


class UserInterface(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.bgimg = tk.PhotoImage(file = "Resources/new_background.png")
        self.manual_confirm = ManualConfirmFeature.ManualConfirm()
        self.notes_features = NotesFeature.NotesFeature()
        self.breaks_feature = BreaksFeature.BreaksFeature()

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

        self.profile_gui = tk.PhotoImage(file = "Resources/profile_ui2.png")
        canvas.create_image(20,20,anchor=NW,image=self.profile_gui)

        self.profile_pic_frame_tk = tk.PhotoImage(file = "Resources/pic_frame.png")
        canvas.create_image(58,58,anchor=NW,image=self.profile_pic_frame_tk)

        self.profile_pic_tk = tk.PhotoImage(file = "Resources/no_pic.png")
        profile_pic = canvas.create_image(60,60,anchor=NW,image=self.profile_pic_tk)


        #adding labels
        student_name_label = canvas.create_text(
            115.0,
            295.0,
            anchor="nw",
            text="(Name)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )


        student_id_label = canvas.create_text(
            115.0,
            335.0,
            anchor="nw",
            text="(ID)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_major_label = canvas.create_text(
            115.0,
            373.0,
            justify=CENTER,
            anchor="nw",
            text="(Major)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_extra_time_label = canvas.create_text(
            90.0,
            430.0,
            justify=CENTER,
            anchor="nw",
            text="?",
            fill="#FFFFFF",
            font=("Inter Bold", 13 * -1)
        )

        student_confirmed_label = canvas.create_text(
            244.0,
            430.0,
            justify=CENTER,
            anchor="nw",
            text="?",
            fill="#FFFFFF",
            font=("Inter Bold", 13 * -1)
        )

        # Creating Table

        table = ttk.Treeview(master=self, columns=table_columns, show="headings")

        for column in table_columns:
            table.heading(column=column, text=column)
            if column == "major":
                table.column(column=column, width=140)
            else:
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

        self.img_holder = tk.PhotoImage(file = "Resources/no_pic.png")
        self.current_id = ""

        def table_select_row(a):#view selected row items
            cur_item = table.focus()
            cur_values = table.item(cur_item,option='values') # this option keeps ID as string
            # cur_values = table.item(cur_item)['values'] # this option converts ID into integer
            self.current_id = str(cur_values[0])
            canvas.itemconfig(student_id_label,text=str(self.current_id))
            canvas.itemconfig(student_name_label,text=student_get_name(self.current_id))
            temp_extra_time = 'Extra Time: ' + student_get_extra_time(self.current_id)
            canvas.itemconfig(student_extra_time_label , text=temp_extra_time)
            canvas.itemconfig(student_major_label , text=student_get_major(self.current_id))
            temp_confirmed = 'Not Confirmed'
            canvas.itemconfig(student_confirmed_label , text=temp_confirmed)

            blob = bucket.get_blob(f'Images/{self.current_id}.png')

            if blob is None: # no picture retrieved from database
                self.img_holder = tk.PhotoImage(file = "Resources/no_pic.png")
                canvas.itemconfig(profile_pic,image=self.img_holder)
            else:
                img_data = np.frombuffer(blob.download_as_string(), np.uint8)
                img_cvt = cv2.imdecode(img_data,cv2.IMREAD_COLOR)
                img_cvt = cv2.cvtColor(img_cvt, cv2.COLOR_BGR2RGB)
                self.img_holder = ImageTk.PhotoImage(image=Image.fromarray(img_cvt))
                canvas.itemconfig(profile_pic,image=self.img_holder)

        table.bind("<<TreeviewSelect>>", table_select_row)


        # Searching the table

        canvas.create_text(
            900,
            150,
            anchor="nw",
            text="Search ID:",
            fill="#FFFFFF",
            font=("Calibri Bold", 18 * -1)
        )

        search_entry = tk.Entry(self, width=20, bg="#917FB3", font=18 , borderwidth=3)
        search_entry.place(x=900,y=185)

        def my_search(*args):
            query = search_entry.get().strip() # get entry string
            str1 = table_df.id.str.contains(query, case=False)
            df2 = table_df[str1]
            r_set = df2.to_numpy().tolist()  # Create list of list using rows
            table.delete(*table.get_children())
            for dt in r_set:
                v = [r for r in dt]  # creating a list from each row
                table.insert("", "end", iid=v[0], values=v)  # adding row

        search_entry.bind("<KeyRelease>", my_search)

        # Timers

        # time variables
        self.waiver_available = True
        self.extra_time_flag = 0
        self.waiver_total_seconds = 15
        self.total_seconds = 30

        time_secs_extra = 5

        # Creating original timer labels
        time_note_label = canvas.create_text(
            525.0,
            75.0,
            anchor="nw",
            text="Time Left",
            fill="#FFFFFF",
            font=("Inter Bold", 12 * -1)
        )
        time_label = canvas.create_text(
            525.0,
            93.0,
            anchor="nw",
            text="00:00",
            fill="#FFFFFF",
            font=("Arial", 15, "", )
        )

        bbox = canvas.bbox(time_label)
        rect_item = canvas.create_rectangle(bbox, outline="purple")
        canvas.tag_raise(time_label,rect_item)

        # Creating Waiver labels
        waiver_label = canvas.create_text(
                425.0,
                75.0,
                anchor="nw",
                text="Waiver Time",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
        )
        waiver_time_label = canvas.create_text(
                430.0,
                93.0,
                anchor="nw",
                text="00:00",
                fill="#FFFFFF",
                font=("Arial",15,"" , )
        )
        bbox2 = canvas.bbox(waiver_time_label)
        rect_item2 = canvas.create_rectangle(bbox2, outline="purple")
        canvas.tag_raise(waiver_time_label,rect_item2)

        if not self.waiver_available:
            canvas.itemconfig(waiver_label,text="")
            canvas.itemconfig(waiver_time_label,text="")
            canvas.create_text(
                370.0,
                95.0,
                anchor="nw",
                text="No Waiver Option",
                fill="#FFFFFF",
                font=("Inter Bold", 14 * -1)
            )

        def countdown():
            minutes = self.total_seconds // 60
            seconds = self.total_seconds % 60
            if self.total_seconds >= 0:
                canvas.itemconfig(time_label, text="{:02d}:{:02d}".format(minutes, seconds))
                self.after(1000, countdown)
                self.total_seconds -= 1
            else:
                if self.extra_time_flag:
                    messagebox.showinfo("Time Countdown", "Extra time is over.")
                else:
                    messagebox.showinfo("Time Countdown", "Original time is over.")
                    canvas.itemconfig(time_note_label, text="Extra Time")
                    self.extra_time_flag = 1
                    self.total_seconds = time_secs_extra
                    countdown()

        def waiver_countdown():
            waiver_minutes = self.waiver_total_seconds // 60
            waiver_seconds = self.waiver_total_seconds % 60
            if self.waiver_total_seconds >= 0:
                canvas.itemconfig(waiver_time_label, text="{:02d}:{:02d}".format(waiver_minutes, waiver_seconds))
                self.after(1000, waiver_countdown)
                self.waiver_total_seconds -= 1
            else:
                messagebox.showinfo("Time Countdown", "Waiver time is over.")

        def start_countdown():
            start_btn["state"] = "disabled"
            countdown()
            if self.waiver_available:
                waiver_countdown()


        # start exams/timers button
        start_btn = Button(self, text='Start Exam', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                           activebackground='#917FB3',height='1',width='14',command= start_countdown,
                           disabledforeground='gray')
        start_btn.place(x = 650,y = 90)


        face_recognition_btn = Button(self, text='Face Recognition', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                                      activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14'
                                      ,command=lambda: controller.show_frame("FaceRec"))

        face_recognition_btn.place(x = 950,y = 90)


        #temp button
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame("StartPage"))
        button1.pack()


        # confirm manually
        confirm_btn = Button(self, text='Manual Confirm', bd='5', fg="#FFFFFF", bg='#910ac2', font=("Calibri", 16 * -1),
                             activebackground='#917FB3', height='1', width='14',
                             command= lambda : self.manual_confirm.confirm_popup(self.parent, self.current_id), disabledforeground='gray')
        confirm_btn.place(x = 700,y = 430)



        # Interface add notes button
        add_notes_btn = Button(self, text='Add Notes', bd='5', fg="#FFFFFF", bg='#910ac2', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                               command=lambda: self.notes_features.add_note_popup(self.parent, self.current_id))
        add_notes_btn.place(x = 360,y = 430)

        # View Notes

        # Interface view notes button

        # open view notes window only if student has notes
        def popup_notes_exist(req_id):
            ref = db.reference(f'Notes/{req_id}',app=ui_app)
            if ref.get():
                self.notes_features.view_note_popup(self.parent, req_id)
            else:
                messagebox.showinfo("View Notes Message","Student has no notes.")

        # View notes button
        view_notes_btn = Button(self, text='View Notes', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                   activebackground='#917FB3',height='1',width='14', disabledforeground='gray',
                               command=lambda: popup_notes_exist(self.current_id))
        view_notes_btn.place(x = 360,y = 480)

        # Interface add notes button
        break_btn = Button(self, text='Break', bd='5', fg="#FFFFFF", bg='#910ac2', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                               command=lambda: self.breaks_feature.break_window(self.parent, self.current_id))
        break_btn.place(x = 535,y = 430)

        back_btn = Button(self, text='Back from Break', bd='5', fg="#FFFFFF", bg='#910ac2', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                               command=lambda: student_back_break(self.current_id))
        back_btn.place(x = 535,y = 480)


