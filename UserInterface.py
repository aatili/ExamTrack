from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox,scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
import cv2
from datetime import date,datetime
import threading

from StudentData import *

import ExamConfig
import FirebaseManager

import BreaksFeature
import NotesFeature
import ManualConfirmFeature


# Loading label, changes according to the state of the app - enables face recognition button when done
class LoadingLabel:
    def __init__(self, frame, canvas, label_ref, text):
        self.frame = frame
        self.label_ref = label_ref
        self.canvas = canvas
        self.text = text
        self.rotation_chars = ["|", "/", "-", "\\"]
        self.rotation_index = 0
        self.update_text()

    def update_text(self):
        temp_state = FirebaseManager.firebase_manager.get_state()
        rot = self.rotation_chars[self.rotation_index]
        loading_text = self.text + " " + rot + " " + rot + " " + rot

        if temp_state == FirebaseManager.AppState.ENCODING or temp_state == FirebaseManager.AppState.DOWNLOADING :
            self.text = str(self.frame.firebase_manager.get_state().value)
            self.rotation_index = (self.rotation_index + 1) % len(self.rotation_chars)
            self.canvas.itemconfig(self.label_ref, text=loading_text)
        elif temp_state == FirebaseManager.AppState.FAILED:
            self.canvas.itemconfig(self.label_ref, text="Failed")
            self.frame.show_retry_btn()
        elif temp_state == FirebaseManager.AppState.DONE:
            self.canvas.itemconfig(self.label_ref, text="")
            self.frame.enable_face_recognition()
            return

        self.canvas.after(350, self.update_text)  # Update every given milliseconds


class UserInterface(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.bgimg = tk.PhotoImage(file = "Resources/interface_background.png")
        self.manual_confirm = ManualConfirmFeature.ManualConfirm()
        self.notes_features = NotesFeature.NotesFeature()
        self.breaks_feature = BreaksFeature.BreaksFeature()

        self.firebase_manager = FirebaseManager.firebase_manager
        self.exam = ExamConfig.cur_exam

        # Creating Cancvas
        self.canvas = Canvas(self, bg="#2A2F4F", height=600, width=1200, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.create_image(0, 0, anchor=NW, image=self.bgimg)

        self.canvas.place(x = 0, y = 0)

        self.canvas.create_rectangle(895, 225, 1000, 350, fill='#917FB3', outline='black')

        # Loading Label

        self.loading_label = self.canvas.create_text(
            960.0,
            40.0,
            anchor="nw",
            text="00:00",
            fill="#FFFFFF",
            font=("Inter Bold", 16 * -1)
        )

        LoadingLabel(self, self.canvas, self.loading_label, 'Downloading')


        # Creating Profile

        self.profile_gui = tk.PhotoImage(file = "Resources/profile_ui2.png")
        self.canvas.create_image(20, 20, anchor=NW, image=self.profile_gui)

        self.profile_pic_frame_tk = tk.PhotoImage(file = "Resources/pic_frame.png")
        self.canvas.create_image(58, 58, anchor=NW, image=self.profile_pic_frame_tk)

        self.profile_pic_tk = tk.PhotoImage(file = "Resources/no_pic.png")
        profile_pic = self.canvas.create_image(60, 60, anchor=NW, image=self.profile_pic_tk)

        self.confirmed_img = tk.PhotoImage(file = "Resources/confirmed.png")
        confirmed_img_panel = Label(self, image=self.confirmed_img,borderwidth=0)
        # confirmed_img_panel.place(x=250,y=422)

        self.not_confirmed_img = tk.PhotoImage(file = "Resources/not_confirmed.png")
        not_confirmed_img_panel = Label(self, image=self.not_confirmed_img,borderwidth=0)
        # not_confirmed_img_panel.place(x=250,y=422)

        extra_img_panel = Label(self, image=self.confirmed_img,borderwidth=0)
        # extra_img_panel.place(x=90,y=422)
        no_extra_img_panel = Label(self, image=self.not_confirmed_img,borderwidth=0)

        # Date label

        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        date_label = self.canvas.create_text(
            10.0,
            10.0,
            anchor="nw",
            text=d1,
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        date_bbox = self.canvas.bbox(date_label)
        date_rect = self.canvas.create_rectangle(date_bbox, outline="#d6b0e8")
        self.canvas.tag_raise(date_label, date_rect)

        # adding labels
        student_name_label = self.canvas.create_text(
            115.0,
            295.0,
            anchor="nw",
            text="(Name)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_id_label = self.canvas.create_text(
            115.0,
            335.0,
            anchor="nw",
            text="(ID)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_major_label = self.canvas.create_text(
            115.0,
            373.0,
            justify=CENTER,
            anchor="nw",
            text="(Major)",
            fill="#d6b0e8",
            font=("Inter Bold", 18 * -1)
        )

        student_confirmed_label = self.canvas.create_text(
            253.0,
            427.0,
            justify=CENTER,
            anchor="nw",
            text="",
            fill="#FFFFFF",
            font=("Calibri Bold", 20 * -1)
        )

        self.canvas.create_text(
            42.0,
            458.0,
            justify=CENTER,
            anchor="nw",
            text="Extra Time",
            fill="#FFFFFF",
            font=("Calibri", 12 * -1)
        )

        self.canvas.create_text(
            197.0,
            458.0,
            justify=CENTER,
            anchor="nw",
            text="Attendance",
            fill="#FFFFFF",
            font=("Calibri", 12 * -1)
        )

        # Creating Table
        # table_columns = student_table_columns()
        self.table = ttk.Treeview(master=self)
        # table.place(x=360, y=150, height=260)

        self.table.tag_configure('oddrow', background='#917FB3')
        self.table.tag_configure('evenrow', background='#BAA4CA')


        '''# Create a vertical scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=table.yview)
        scrollbar.place(x=850, y=140, height=250)

        # Configure the table to use the scrollbar
        table.configure(yscrollcommand=scrollbar.set)'''

        # Selecting row in table

        self.img_holder = tk.PhotoImage(file = "Resources/no_pic.png")
        self.current_id = ""

        # enabled/disabled relevant button depending on the students attendance
        def set_button_state(str_state):
            if str_state == "waiver":
                confirm_btn["state"] = "disabled"
                break_btn["state"] = "disabled"
                view_breaks_btn["state"] = "disabled"

                self.undo_waiver_btn.place(x=700, y=480)
                self.waiver_btn.place_forget()
                self.waiver_btn["state"] = "normal"

            elif str_state == "confirmed":
                confirm_btn["state"] = "disabled"
                break_btn["state"] = "normal"
                view_breaks_btn["state"] = "normal"

                self.undo_waiver_btn.place_forget()
                self.waiver_btn.place(x=700, y=480)
                self.waiver_btn["state"] = "normal"

            elif str_state == "not_confirmed":
                confirm_btn["state"] = "normal"
                break_btn["state"] = "disabled"
                view_breaks_btn["state"] = "disabled"

                self.undo_waiver_btn.place_forget()
                self.waiver_btn.place(x=700, y=480)
                self.waiver_btn["state"] = "disabled"

        def table_select_row(a):  # view selected row items
            cur_item = self.table.focus()
            cur_values = self.table.item(cur_item,option='values') # this option keeps ID as string
            if not cur_values:
                return
            # cur_values = table.item(cur_item)['values'] # this option converts ID into integer
            self.current_id = str(cur_values[0])
            self.canvas.itemconfig(student_id_label, text=str(self.current_id))
            self.canvas.itemconfig(student_name_label, text=students.student_get_name(self.current_id))

            temp_extra_time = students.student_get_extra_time(self.current_id)
            if temp_extra_time.lower() == "no":
                no_extra_img_panel.place(x=90,y=422)
                extra_img_panel.place_forget()
            else:
                no_extra_img_panel.place_forget()
                extra_img_panel.place(x=90,y=422)

            self.canvas.itemconfig(student_major_label, text=students.student_get_major(self.current_id))

            if students.student_check_waiver(self.current_id):
                set_button_state("waiver")
                self.canvas.itemconfig(student_confirmed_label, text="Waiver", fill='#b83e4f')
                confirmed_img_panel.place_forget()
                not_confirmed_img_panel.place_forget()
            elif students.student_check_attendance(self.current_id):
                set_button_state("confirmed")
                self.canvas.itemconfig(student_confirmed_label, text="")
                confirmed_img_panel.place(x=250,y=422)
                not_confirmed_img_panel.place_forget()
            else:
                set_button_state("not_confirmed")
                self.canvas.itemconfig(student_confirmed_label, text="")
                confirmed_img_panel.place_forget()
                not_confirmed_img_panel.place(x=250,y=422)

            if students.student_in_break(self.current_id):
                break_btn.place_forget()
                back_from_break_btn.place(x = 535,y = 430)
            else:
                back_from_break_btn.place_forget()
                break_btn.place(x = 535,y = 430)

            self.img_holder = tk.PhotoImage(file=FirebaseManager.get_image_path(self.current_id))
            self.canvas.itemconfig(profile_pic, image=self.img_holder)
            # Fetch blob using threading
            '''fetch_thread = threading.Thread(target=fetch_blob)
            fetch_thread.start()'''

        self.table.bind("<<TreeviewSelect>>", table_select_row)

        # Searching the table

        self.canvas.create_text(
            895,
            150,
            anchor="nw",
            text="Search ID:",
            fill="#FFFFFF",
            font=("Calibri Bold", 18 * -1)
        )

        search_entry = tk.Entry(self, width=20, bg="#917FB3", font=18 , borderwidth=3)
        search_entry.place(x=895,y=185)

        # Search query and filter table
        def my_search(*args):
            table_df = students.get_student_df_ref()
            query = search_entry.get().strip() # get entry string
            str1 = table_df.id.str.contains(query, case=False)
            df2 = table_df[str1]
            r_set = df2.to_numpy().tolist()  # Create list of list using rows
            self.table.delete(*self.table.get_children())
            j = 0  # similar to color j , counter for colouring purpose
            for dt in r_set:
                tags = ('evenrow',) if j % 2 == 0 else ('oddrow',)  # for colouring purpose
                v = [r for r in dt]  # creating a list from each row
                # Handling checkbox statuses
                s_id = v[0]
                if confirmed_checkbox_var.get() == 1 and extra_checkbox_var.get() == 0:
                    if students.student_check_attendance(s_id):
                        self.table.insert("", "end", iid=s_id, values=v, tags=tags)  # adding row
                        j += 1  # colouring
                elif confirmed_checkbox_var.get() == 1 and extra_checkbox_var.get() == 1:
                    if students.student_check_attendance(s_id) and students.student_get_extra_time(s_id).lower() == 'yes':
                        self.table.insert("", "end", iid=s_id, values=v, tags=tags)
                        j += 1  # colouring
                elif confirmed_checkbox_var.get() == 0 and extra_checkbox_var.get() == 1:
                    if students.student_get_extra_time(s_id).lower() == 'yes':
                        self.table.insert("", "end", iid=s_id, values=v, tags=tags)
                        j += 1  # colouring
                else:
                    self.table.insert("", "end", iid=s_id, values=v, tags=tags)
                    j += 1  # colouring

        search_entry.bind("<KeyRelease>", my_search)

        # Checkboxes
        confirmed_checkbox_var = IntVar()
        confirmed_checkbox = Checkbutton(self,variable = confirmed_checkbox_var,onvalue = 1,offvalue = 0,height = 1,
                                     font=("Inter Bold", 14 * -1),text="Attending",bg = "#917FB3",
                                         command=my_search)
        confirmed_checkbox.place(x=900,y=230)

        extra_checkbox_var = IntVar()
        extra_checkbox = Checkbutton(self,variable = extra_checkbox_var,onvalue = 1,offvalue = 0,height = 1,
                                     font=("Inter Bold", 14 * -1),text="Extra time",bg = "#917FB3",
                                         command=my_search)
        extra_checkbox.place(x=900,y=260)

        # Break Checkbox filter
        def filter_on_break():
            table_df = students.get_student_df_ref()
            if break_checkbox_var.get() == 1:
                confirmed_checkbox_var.set(0)
                extra_checkbox_var.set(0)
                waiver_checkbox_var.set(0)
                confirmed_checkbox.configure(state="disabled")
                extra_checkbox.configure(state="disabled")
                waiver_checkbox.configure(state="disabled")
            else:
                confirmed_checkbox.configure(state="normal")
                extra_checkbox.configure(state="normal")
                waiver_checkbox.configure(state="normal")
            query = search_entry.get().strip() # get entry string
            str1 = table_df.id.str.contains(query, case=False)
            df2 = table_df[str1]
            r_set = df2.to_numpy().tolist()  # Create list of list using rows
            self.table.delete(*self.table.get_children())
            color_i = 0
            for dt in r_set:
                v = [r for r in dt]  # creating a list from each row
                j_tags = ('evenrow',) if color_i % 2 == 0 else ('oddrow',)
                if break_checkbox_var.get() == 1:
                    if students.student_in_break(v[0]):
                        self.table.insert("", "end", iid=v[0], values=v, tags=j_tags)
                        color_i += 1
                else:
                    self.table.insert("", "end", iid=v[0], values=v, tags=j_tags)
                    color_i += 1

        break_checkbox_var = IntVar()
        break_checkbox = Checkbutton(self,variable = break_checkbox_var,onvalue = 1,offvalue = 0,height = 1,
                                     font=("Inter Bold", 14 * -1),text="On Break",bg = "#917FB3",command=filter_on_break)
        break_checkbox.place(x=900,y=290)

        # Waiver Checkbox filter
        def filter_on_waiver():
            table_df = students.get_student_df_ref()
            if waiver_checkbox_var.get() == 1:
                confirmed_checkbox_var.set(0)
                extra_checkbox_var.set(0)
                break_checkbox_var.set(0)
                confirmed_checkbox.configure(state="disabled")
                extra_checkbox.configure(state="disabled")
                break_checkbox.configure(state="disabled")
            else:
                confirmed_checkbox.configure(state="normal")
                extra_checkbox.configure(state="normal")
                break_checkbox.configure(state="normal")
            query = search_entry.get().strip() # get entry string
            str1 = table_df.id.str.contains(query, case=False)
            df2 = table_df[str1]
            r_set = df2.to_numpy().tolist()  # Create list of list using rows
            self.table.delete(*self.table.get_children())
            color_i = 0
            for dt in r_set:
                v = [r for r in dt]  # creating a list from each row
                j_tags = ('evenrow',) if color_i % 2 == 0 else ('oddrow',)
                if waiver_checkbox_var.get() == 1:
                    if students.student_check_waiver(v[0]):
                        self.table.insert("", "end", iid=v[0], values=v, tags=j_tags)
                        color_i += 1
                else:
                    self.table.insert("", "end", iid=v[0], values=v, tags=j_tags)
                    color_i += 1

        waiver_checkbox_var = IntVar()
        waiver_checkbox = Checkbutton(self,variable = waiver_checkbox_var,onvalue = 1,offvalue = 0,height = 1,
                                      font=("Inter Bold", 14 * -1),text="Waiver",bg = "#917FB3",command=filter_on_waiver)
        waiver_checkbox.place(x=900, y=320)

        # Timers

        # time variables
        self.waiver_available = True
        self.extra_time_flag = 0
        self.waiver_total_seconds = 15
        self.total_seconds = 30

        self.time_secs_extra = 5

        # Creating original timer labels
        time_note_label = self.canvas.create_text(
            525.0,
            75.0,
            anchor="nw",
            text="Time Left",
            fill="#FFFFFF",
            font=("Inter Bold", 12 * -1)
        )
        time_label = self.canvas.create_text(
            525.0,
            93.0,
            anchor="nw",
            text="00:00",
            fill="#FFFFFF",
            font=("Arial", 15, "", )
        )

        '''bbox = self.canvas.bbox(time_label)
        rect_item = self.canvas.create_rectangle(bbox, outline="purple")
        self.canvas.tag_raise(time_label, rect_item)'''

        # Creating Waiver labels
        self.waiver_label = self.canvas.create_text(
                425.0,
                75.0,
                anchor="nw",
                text="Waiver Time",
                fill="#FFFFFF",
                font=("Inter Bold", 12 * -1)
        )
        self.waiver_time_label = self.canvas.create_text(
                430.0,
                93.0,
                anchor="nw",
                text="00:00",
                fill="#FFFFFF",
                font=("Arial",15,"" , )
        )
        bbox2 = self.canvas.bbox(self.waiver_time_label)
        self.rect_item2 = self.canvas.create_rectangle(bbox2, outline="purple")
        self.canvas.tag_raise(self.waiver_time_label, self.rect_item2)

        def countdown():
            minutes = self.total_seconds // 60
            seconds = self.total_seconds % 60
            if self.total_seconds >= 0:
                self.canvas.itemconfig(time_label, text="{:02d}:{:02d}".format(minutes, seconds))
                self.after(1000, countdown)
                self.total_seconds -= 1
            else:
                if self.extra_time_flag:
                    messagebox.showinfo("Time Countdown", "Extra time is over.")
                    add_time_btn.place_forget()
                else:
                    messagebox.showinfo("Time Countdown", "Original time is over.")
                    self.canvas.itemconfig(time_note_label, text="Extra Time")
                    self.extra_time_flag = 1
                    self.total_seconds = self.time_secs_extra
                    countdown()

        def waiver_countdown():
            waiver_minutes = self.waiver_total_seconds // 60
            waiver_seconds = self.waiver_total_seconds % 60
            if self.waiver_total_seconds >= 0:
                self.canvas.itemconfig(self.waiver_time_label, text="{:02d}:{:02d}".format(waiver_minutes, waiver_seconds))
                self.after(1000, waiver_countdown)
                self.waiver_total_seconds -= 1
            else:
                messagebox.showinfo("Time Countdown", "Waiver time is over.")

        def start_countdown():
            start_btn["state"] = "disabled"
            add_time_btn.place(x = 595,y = 87)
            countdown()
            if self.waiver_available:
                waiver_countdown()

        # start exams/timers button
        start_btn = Button(self, text='Start Exam', bd='4',fg="#FFFFFF" ,bg='#812e91',font=("Calibri", 16 * -1),
                           activebackground='#917FB3',height='1',width='14',command= start_countdown,
                           disabledforeground='gray')
        start_btn.place(x = 700,y = 80)

        # Add Time for exam

        def add_time():
            add_time_window = Toplevel(self)
            add_time_window.geometry("300x270+350+200")
            add_time_window.resizable(False,False)
            add_time_window.title("Add Time")
            add_time_window.configure(bg='#917FB3')
            add_time_window_reason =  Label(add_time_window, text="Specify Reason:" ,
                                          bg='#917FB3',font=("Calibri", 16 * -1))
            add_time_window_reason.place(x=20,y=70)

            add_time_label =  Label(add_time_window, text="Add minutes:" ,
                                          bg='#917FB3',font=("Calibri", 16 * -1))
            add_time_label.place(x=20,y=30)

            add_time_box = Spinbox(add_time_window, from_= 0, to = 100,increment=5,font=("Calibri", 16 * -1),width=3)
            add_time_box.place(x=120,y=30)

            add_reason_entry = scrolledtext.ScrolledText(add_time_window, wrap=tk.WORD,bd=3,bg='#E5BEEC',width=30,
                                                   height=3,font=("Calibri", 16*-1))
            add_reason_entry.place(x=20,y=95)

            # add minute to time variable
            def add_total_seconds():
                temp_added = int(add_time_box.get())
                self.total_seconds += temp_added * 60
                ExamConfig.cur_exam.add_time(temp_added)
                add_time_window.destroy()

            # Buttons
            add_time_confirm_btn = Button(add_time_window, text='Confirm', bd='4',fg="#FFFFFF" ,bg='#812e91',
                                      font=("Calibri", 14 * -1),activebackground='#917FB3',height='1',width='12',
                                      disabledforeground='gray',command=add_total_seconds)
            add_time_confirm_btn.place(x=30, y=200)

            add_time_cancel_btn = Button(add_time_window, text='Cancel', bd='4',fg="#FFFFFF" ,bg='#812e91',
                                     font=("Calibri", 14 * -1),activebackground='#917FB3',height='1',width='12',
                                     disabledforeground='gray',command= add_time_window.destroy)
            add_time_cancel_btn.place(x=145, y=200)

        # add time button
        add_time_btn = Button(self, text='+', bd='3',fg="#FFFFFF" ,bg='#812e91',font=("Arial", 13 * -1),
                           activebackground='#917FB3',height='1',width='2',command = add_time)
        #add_time_btn.place(x = 590,y = 80)

        # retry button - only shows in case the encoding fails
        def retry_download_encode():
            # Thread to allow the app to run while downloading images
            self.firebase_manager.set_downloading()
            self.retry_btn.place_forget()  # hide button when clicked
            fetch_thread = threading.Thread(target=lambda: controller.frames["StartPage"].download_and_encode())
            fetch_thread.start()

        self.retry_btn = Button(self, text='Retry', bd='4',fg="#FFFFFF" ,bg='#812e91',
                                      activebackground='#917FB3',font=("Calibri", 12 * -1),height='1',width='10'
                                      ,command=retry_download_encode)
        # self.retry_btn.place(x = 1100,y = 40)

        # open face recognition frame
        self.face_recognition_btn = Button(self, text='Face Recognition', bd='4',fg="#FFFFFF" ,bg='#812e91',
                                      activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14'
                                      ,command=lambda: [controller.show_frame("FaceRec")],state="disabled")

        self.face_recognition_btn.place(x = 950,y = 80)

        # temp button
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame("StartPage"))
        button1.pack()

        button2 = tk.Button(self, text="TEST",
                            command=lambda: [students.create_result_table() , print(students.result_table_df)])
        button2.pack()

        # confirm manually
        def manual_confirm_check(student_id):  # check before calling manual confirm
            if students.student_check_attendance(student_id):
                messagebox.showwarning("Manual Confirm Message", "Student attendance already confirmed.")
                return
            self.manual_confirm.confirm_popup(self.parent, self.current_id)

        confirm_btn = Button(self, text='Manual Confirm', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                             activebackground='#917FB3', height='1', width='14' , disabledforeground='gray',
                             command= lambda :manual_confirm_check(self.current_id))
        confirm_btn.place(x = 700,y = 430)

        # Interface add notes button
        add_notes_btn = Button(self, text='Add Notes', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                               command=lambda: self.notes_features.add_note_popup(self.parent, self.current_id))
        add_notes_btn.place(x = 360,y = 430)

        # View Notes

        # Interface view notes button

        # open view notes window only if student has notes
        def popup_notes_exist(req_id):
            ref = self.firebase_manager.get_student_notes(req_id)
            if ref.get():
                self.notes_features.view_note_popup(self.parent, req_id)
            else:
                messagebox.showinfo("View Notes Message", "Student has no notes.")

        # View notes button
        view_notes_btn = Button(self, text='View Notes', bd='4',fg="#FFFFFF" ,bg='#812e91',font=("Calibri", 16 * -1),
                   activebackground='#917FB3',height='1',width='14', disabledforeground='gray',
                               command=lambda: popup_notes_exist(self.current_id))
        view_notes_btn.place(x=360, y=480)

        self.last_hover_time = datetime.now()

        # refresh to display updated info on ui
        def table_selection_refresh(a):
            current_time = datetime.now()
            if (current_time - self.last_hover_time).total_seconds() >= 5:
                selected_item = self.table.selection()  # Get the currently selected item
                self.table.selection_set(selected_item) # Reselect the same item
                self.last_hover_time = current_time

        self.bind("<Enter>", table_selection_refresh)

        # Break Function
        def student_take_break(student_id):
            if not students.student_check_attendance(student_id):
                messagebox.showerror("Break Error", "Student not in attendance.")
                return
            if students.student_in_break(student_id):
                messagebox.showerror("Break Error", "Student already in break.")
                return
            self.breaks_feature.break_window(self.parent, self.current_id)

        # Break features buttons
        break_btn = Button(self, text='Break', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                               command=lambda: student_take_break(self.current_id))
        break_btn.place(x = 535,y = 430)

        # Back from break check function
        def student_back_from_break(student_id):
            if not students.student_check_attendance(student_id):
                messagebox.showerror("Break Error", "Student attendance was not confirmed.")
                return
            if not students.student_in_break(student_id):
                messagebox.showinfo("Break Info", "Student not in break.")
                return
            res = students.student_back_break(self.current_id)
            if res != STUDENT_NOT_FOUND:
                messagebox.showinfo("Break Info", res)
                if break_checkbox_var.get() == 1:
                    filter_on_break()
                else:
                    my_search()

        # back from break button
        back_from_break_btn = Button(self, text='Back from Break', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                               command=lambda: student_back_from_break(self.current_id))
        #back_btn.place(x = 535,y = 480)

        # view breaks btn

        view_breaks_btn = Button(self, text='View Breaks', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                               command=lambda: self.breaks_feature.view_break_window(self.parent, self.current_id))
        view_breaks_btn.place(x = 535,y = 480)

        # waiver
        def student_waiver_popup(student_id):
            if students.student_report_waiver(student_id) != FUNC_SUCCESS:
                messagebox.showerror("Waiver Error", "Student not found.")
                return
            self.waiver_btn.place_forget()
            self.undo_waiver_btn.place(x=700, y=480)
            messagebox.showinfo("Waiver Message", "Student waiver successful.")

        def student_undo_waiver(student_id):
            res = students.student_undo_waiver(student_id)
            if res == STUDENT_NOT_FOUND:
                messagebox.showerror("Undo Waiver Error", "Student not found.")
                return
            if res == STUDENT_ALREADY_CONFIRMED:
                messagebox.showerror("Undo Waiver Error", "Student is already attending.")
                return
            messagebox.showinfo("Waiver Message", "Undo waiver successful.")
            filter_on_waiver()
            self.waiver_btn.place(x=700, y=480)
            self.undo_waiver_btn.place_forget()

        # waiver button
        self.waiver_btn = Button(self, text='Waiver', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                                 activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                 command=lambda: student_waiver_popup(self.current_id))
        self.waiver_btn.place(x=700, y=480)

        # undo waiver button
        self.undo_waiver_btn = Button(self, text='Undo Waiver', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                                      activebackground='#917FB3', height='1', width='14', disabledforeground='gray',
                                      command=lambda: student_undo_waiver(self.current_id))
        #self.undo_waiver_btn.place(x=700, y=480)


        # View Report
        self.view_report_btn = Button(self, text='View Report', bd='4',fg="#FFFFFF" ,bg='#812e91',
                                      activebackground='#917FB3',font=("Calibri", 16 * -1),height='1',width='14'
                                      ,command=lambda: [controller.frames["ReportFrames"].create_report(),
                                                        controller.show_frame("ReportFrames")])

        self.view_report_btn.place(x = 950,y = 500)

    def initiate_time(self):
        self.waiver_available = self.exam.is_waiver_available()
        self.extra_time_flag = 0
        self.waiver_total_seconds = ExamConfig.WAIVER_TIME * 60
        self.total_seconds = self.exam.get_exam_duration() * 60
        self.time_secs_extra = int(ExamConfig.EXTRA_TIME_PERCENTAGE * self.total_seconds)

        if not self.waiver_available:  # do not show waiver button if not available
            self.canvas.itemconfig(self.waiver_label, text="")
            self.canvas.itemconfig(self.waiver_time_label, text="")
            self.canvas.create_text(
                370.0,
                95.0,
                anchor="nw",
                text="No Waiver Option",
                fill="#FFFFFF",
                font=("Inter Bold", 14 * -1)
            )
            self.waiver_btn.place_forget()
            self.canvas.itemconfig(self.rect_item2, state="hidden")

    def initiate_table(self):
        students.students_initiate_attendance()
        table_columns = students.student_table_columns()
        self.table.configure(columns=table_columns, show="headings")
        for column in table_columns:
            self.table.heading(column=column, text=column)
            if column == "major":
                self.table.column(column=column, width=140)
            else:
                self.table.column(column=column, width=70)

        color_j = 0
        table_data = students.student_table_values()
        for row_data in table_data:
            color_tags = ('evenrow',) if color_j % 2 == 0 else ('oddrow',)
            self.table.insert(parent="", index="end", values=row_data, tags=color_tags)
            color_j += 1

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, background="#917FB3", fieldbackground="#917FB3", foreground="white",
                        font=("Calibri", 14 * -1))
        style.configure("Treeview.Heading", rowheight=30, background="#917FB3", fieldbackground="#917FB3",
                        foreground="white", font=("Calibri", 14 * -1))
        style.map("Treeview.Heading", background=[("active", "#917FB3"), ("!active", "#917FB3")],
           foreground=[("active", "white"), ("!active", "white")])
        style.map("Treeview", background=[("selected", "#000080")])
        self.table.place(x=360, y=150, height=260)

    def enable_face_recognition(self):
        self.face_recognition_btn["state"] = 'normal'

    def show_retry_btn(self):
        self.retry_btn.place(x = 1100,y = 40)





