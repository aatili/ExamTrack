from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox,scrolledtext
from student_data import *
import time
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
import cv2
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import date

cred = credentials.Certificate("serviceAccountKey.json")
ui_app = firebase_admin.initialize_app(cred, {
    'databaseURL': "https://examfacerecognition-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "examfacerecognition.appspot.com"} , name="UserInterfaceApp")
bucket = storage.bucket(app=ui_app)


LARGE_FONT = ("Verdana", 12)

class UserInterface(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
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


        # Creating Profile

        self.profile_gui = tk.PhotoImage(file = "Resources/profile_ui.png")
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
            text="?",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )


        student_id_label = canvas.create_text(
            115.0,
            335.0,
            anchor="nw",
            text="?",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_major_label = canvas.create_text(
            115.0,
            373.0,
            justify=CENTER,
            anchor="nw",
            text="?",
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
            #cur_values = table.item(cur_item)['values'] # this option converts ID into integer
            self.current_id = str(cur_values[0])
            canvas.itemconfig(student_id_label,text=str(self.current_id))
            canvas.itemconfig(student_name_label,text=student_get_name(self.current_id))
            temp_extra_time = 'Extra Time: ' + student_get_extra_time(self.current_id)
            canvas.itemconfig(student_extra_time_label , text=temp_extra_time)
            canvas.itemconfig(student_major_label , text=student_get_major(self.current_id))
            temp_confirmed = 'Not Confirmed'
            canvas.itemconfig(student_confirmed_label , text=temp_confirmed)

            blob = bucket.get_blob(f'Images/{self.current_id}.png')

            if blob == None: #no picture retrieved from database
                self.img_holder = tk.PhotoImage(file = "Resources/no_pic.png")
                canvas.itemconfig(profile_pic,image=self.img_holder)
            else:
                img_data = np.frombuffer(blob.download_as_string(), np.uint8)
                img_cvt = cv2.imdecode(img_data,cv2.IMREAD_COLOR)
                img_cvt = cv2.cvtColor(img_cvt, cv2.COLOR_BGR2RGB)
                self.img_holder = ImageTk.PhotoImage(image=Image.fromarray(img_cvt))
                canvas.itemconfig(profile_pic,image=self.img_holder)

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
                           activebackground='#917FB3',height='1',width='14',command= start_timers, disabledforeground='gray')
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

        def confirm_popup(id):
            if len(id)==0:
                return
            res=messagebox.askquestion('Manual Confirmation', 'Confirm Student ' + id +'?')
            if res == 'yes' :
                student_confirm_attendace(id)


        confirm_btn = Button(self, text='Manual Confirm', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                           activebackground='#917FB3',height='1',width='14',
                             command= lambda : confirm_popup(self.current_id) , disabledforeground='gray')
        confirm_btn.place(x = 650,y = 430)


        # Add Notes functionality



        def add_note_popup(noted_id):
            if len(noted_id)==0:
                return
            note_window = Toplevel(parent)
            note_window.geometry("400x500")
            note_window.title("Add Note")
            note_window.configure(bg='#917FB3')
            note_window_id_label = Label(note_window, text="Student ID:" , bg='#917FB3',font=("Calibri", 16 * -1))
            note_window_id_label.place(x=30,y=30)
            note_window_id_label2 = Label(note_window, text=noted_id , bg='#917FB3',font=("Calibri", 16 * -1))
            note_window_id_label2.place(x=120,y=30)

            note_window_reporter_label = Label(note_window, text="Reporter:" , bg='#917FB3',font=("Calibri", 16 * -1))
            note_window_reporter_label.place(x=30,y=70)
            note_window_reporter_entry = Entry(note_window, bd =3,font=("Calibri", 16 * -1))
            note_window_reporter_entry.place(x=120,y=70)

            today = date.today()
            d1 = today.strftime("%d/%m/%Y")
            note_window_date_label = Label(note_window, text=d1, bg='#917FB3',font=("Calibri", 16 * -1),
                                           borderwidth=3, relief="ridge")
            note_window_date_label.place(x=300,y=5)

            note_window_subject_label = Label(note_window, text="Subject:" , bg='#917FB3',font=("Calibri", 16 * -1))
            note_window_subject_label.place(x=30,y=110)
            note_window_subject_entry = Entry(note_window, bd =3,font=("Calibri", 16 * -1))
            note_window_subject_entry.place(x=120,y=110)

            note_window_note_label = Label(note_window, text="Note:" , bg='#917FB3',font=("Calibri", 16 * -1))
            note_window_note_label.place(x=30,y=150)
            #note_text = tk.Text(note_window, height=12, width=40,bd=3)
            #note_text.place(x=30,y=190)
            note_text_area = scrolledtext.ScrolledText(note_window, wrap=tk.WORD,bd=3,
                                      width=40, height=8,
                                      font=("Calibri", 16*-1))

            note_text_area.grid(column=0, row=2, pady=190, padx=30)

            note_confirm_btn = Button(note_window, text='Confirm', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                   activebackground='#917FB3',height='1',width='14', disabledforeground='gray')
            note_confirm_btn.place(x = 30, y= 400)

            #note cancel button
            def note_window_cancel():
                res=messagebox.askquestion('Cancel Note', 'Are you sure?',parent=note_window)
                if res == 'yes':
                    note_window.destroy()
            note_cancel_btn = Button(note_window, text='Cancel', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                   activebackground='#917FB3',height='1',width='14', disabledforeground='gray',command=note_window_cancel)
            note_cancel_btn.place(x = 180, y= 400)











        add_notes_btn = Button(self, text='Add Notes', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                   activebackground='#917FB3',height='1',width='14', disabledforeground='gray',
                               command=lambda: add_note_popup(self.current_id))
        add_notes_btn.place(x = 450,y = 430)


