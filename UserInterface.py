from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox,scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
import cv2
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import date,datetime

from student_data import *
from OfflineFeatures import *


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
        self.offline = OfflineFeatures()
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
        time_secs = 30
        time_secs_extra = 5
        time_secs_waiver = 15

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

        def countdown(total_seconds):
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            if total_seconds >= 0:
                canvas.itemconfig(time_label, text="{:02d}:{:02d}".format(minutes, seconds))
                self.after(1000, countdown,total_seconds-1)
            else:
                if self.extra_time_flag:
                    messagebox.showinfo("Time Countdown", "Extra Time is Up ")
                else:
                    messagebox.showinfo("Time Countdown", "Original Time is Up ")
                    canvas.itemconfig(time_note_label, text="Extra Time")
                    self.extra_time_flag = 1
                    countdown(time_secs_extra)

        def waiver_countdown(waiver_total_seconds):
            waiver_minutes = waiver_total_seconds // 60
            waiver_seconds = waiver_total_seconds % 60
            if waiver_total_seconds >= 0:
                canvas.itemconfig(waiver_time_label, text="{:02d}:{:02d}".format(waiver_minutes, waiver_seconds))
                self.after(1000, waiver_countdown, waiver_total_seconds-1)
            else:
                messagebox.showinfo("Time Countdown", "Waiver Time is Up ")



        def start_countdown():
            start_btn["state"] = "disabled"
            countdown(time_secs)
            if self.waiver_available:
                waiver_countdown(time_secs_waiver)


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
        confirm_btn = Button(self, text='Manual Confirm', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                           activebackground='#917FB3',height='1',width='14',
                             command= lambda : self.offline.confirm_popup2(self.parent,self.current_id) , disabledforeground='gray')
        confirm_btn.place(x = 650,y = 430)


        # Add Notes
        #Add Notes Window
        def add_note_popup(noted_id):
            if len(noted_id)==0:
                return
            note_window = Toplevel(parent)
            note_window.geometry("400x500+350+100")
            note_window.resizable(False,False)
            note_window.title("Add Note")
            note_window.configure(bg='#917FB3')
            note_window_id_label = Label(note_window, text="Student ID:" , bg='#917FB3',font=("Calibri", 16 * -1))
            note_window_id_label.place(x=30,y=30)
            note_window_id_label2 = Label(note_window, text=noted_id , bg='#917FB3',font=("Calibri", 16 * -1),
                                          borderwidth=3, relief="ridge")
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
                                      width=40, height=8,font=("Calibri", 16*-1))

            note_text_area.grid(column=0, row=2, pady=190, padx=30)

            #note confirm button
            def note_window_confirm():
                ref = db.reference('Notes',app=ui_app)
                now = datetime.now()
                dt_string = now.strftime("%d-%m-%Y %H:%M")
                temp_data = {noted_id:{
                    dt_string:{
                        'subject':note_window_subject_entry.get(),
                        'reporter':note_window_reporter_entry.get(),
                        'note': note_text_area.get("1.0",END)
                    }
                }}

                try:
                    for key, value in temp_data.items():
                        ref.child(key).update(value)
                except ValueError:
                        messagebox.showerror("Add Note Error","Failed to Submit.",parent=note_window)
                messagebox.showinfo("Add Note Message","Submitted Succesfully.",parent=note_window)
                note_window.destroy()



            note_confirm_btn = Button(note_window, text='Confirm', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                                      font=("Calibri", 16 * -1),activebackground='#917FB3',height='1',width='14',
                                      disabledforeground='gray',command=note_window_confirm)
            note_confirm_btn.place(x = 30, y= 400)

            #note cancel button
            def note_window_cancel():
                res=messagebox.askquestion('Cancel Note', 'Are you sure?',parent=note_window)
                if res == 'yes':
                    note_window.destroy()

            note_cancel_btn = Button(note_window, text='Cancel', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                                     font=("Calibri", 16 * -1),activebackground='#917FB3',height='1',width='14',
                                     disabledforeground='gray',command=note_window_cancel)
            note_cancel_btn.place(x = 180, y= 400)


        # Interface add notes button
        add_notes_btn = Button(self, text='Add Notes', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                   activebackground='#917FB3',height='1',width='14', disabledforeground='gray',
                               command=lambda: add_note_popup(self.current_id))
        add_notes_btn.place(x = 360,y = 430)



        #View Notes

        #View Notes Window
        def view_note_popup(noted_id):
            if len(noted_id)==0:
                return
            view_note_window = Toplevel(parent)
            view_note_window.geometry("500x500+350+100")
            view_note_window.resizable(False,False)
            view_note_window.title("View Notes")
            view_note_window.configure(bg='#917FB3')

            view_note_window_label =  Label(view_note_window, text="Select Date:" ,
                                              bg='#917FB3',font=("Calibri", 16 * -1))
            view_note_window_label.place(x=30,y=30)


            view_note_window_id = Label(view_note_window, text="Student ID:" ,
                                              bg='#917FB3',font=("Calibri", 16 * -1))
            view_note_window_id.place(x=30,y=70)
            view_note_window_id2 = Label(view_note_window, text=noted_id ,bg='#917FB3',font=("Calibri", 16 * -1),
                                               borderwidth=1, relief="groove")
            view_note_window_id2.place(x=120,y=70)

            view_note_window_reporter = Label(view_note_window, text="Reporter:" ,
                                                    bg='#917FB3',font=("Calibri", 16 * -1))
            view_note_window_reporter.place(x=30,y=110)
            view_note_window_reporter2 = Label(view_note_window, text="Anonymos" ,
                                                     bg='#917FB3',font=("Calibri", 16 * -1))
            view_note_window_reporter2.place(x=120,y=110)

            today = date.today()
            d1 = today.strftime("%d/%m/%Y")
            view_note_window_date_label = Label(view_note_window, text=d1, bg='#917FB3',font=("Calibri", 16 * -1),
                                           borderwidth=3, relief="ridge")
            view_note_window_date_label.place(x=400,y=5)


            view_note_window_subject = Label(view_note_window, text="Subject:" ,
                                                   bg='#917FB3',font=("Calibri", 16 * -1))
            view_note_window_subject.place(x=30,y=150)
            view_note_window_subject2 = Label(view_note_window, text="Note Subject" ,
                                                    bg='#917FB3',font=("Calibri", 16 * -1))
            view_note_window_subject2.place(x=120,y=150)

            view_note_text_area = scrolledtext.ScrolledText(view_note_window, wrap=tk.WORD,bd=3,background="gray",
                                      width=50, height=8,font=("Calibri", 16*-1))

            view_note_text_area.grid(column=0, row=2, pady=190, padx=30)
            view_note_text_area.insert(INSERT,"Nothing to view")
            view_note_text_area["state"] ="disabled"
            view_note_window.update()


            view_note_done_btn = Button(view_note_window, text='Done', bd='5',fg="#FFFFFF" ,bg='#910ac2'
                                        ,font=("Calibri", 16 * -1),activebackground='#917FB3',height='1',
                                        width='14', disabledforeground='gray',command = view_note_window.destroy)
            view_note_done_btn.place(x = 350, y= 400)

            ref = db.reference(f'Notes/{noted_id}',app=ui_app)
            res_dict = ref.order_by_key().get()
            res_keys = list(res_dict.keys())

            #Combobox functionality

            def combo_changed(event):
                selected_date = combo_dates.get()
                view_note_window_reporter2.configure(text = res_dict[selected_date]['reporter'])
                view_note_window_subject2.configure(text = res_dict[selected_date]['subject'])
                view_note_text_area.configure(state='normal')
                view_note_text_area.delete("1.0","end")
                view_note_text_area.insert(INSERT,res_dict[selected_date]['note'])
                view_note_text_area.configure(state='disabled')


            combo_dates = ttk.Combobox(view_note_window, state="readonly" , values=res_keys,
                                       background="gray",font=("Calibri", 16 * -1))
            combo_dates.place(x=120,y=35)

            combo_dates.bind("<<ComboboxSelected>>", combo_changed)




        # Interface view notes button

        #open view notes window only if student has notes
        def popup_notes_exist(req_id):
            ref = db.reference(f'Notes/{req_id}',app=ui_app)
            if ref.get():
                view_note_popup(req_id)
            else:
                messagebox.showinfo("View Notes Message","Student has no notes!")



        view_notes_btn = Button(self, text='View Notes', bd='5',fg="#FFFFFF" ,bg='#910ac2',font=("Calibri", 16 * -1),
                   activebackground='#917FB3',height='1',width='14', disabledforeground='gray',
                               command=lambda: popup_notes_exist(self.current_id))
        view_notes_btn.place(x = 360,y = 480)


