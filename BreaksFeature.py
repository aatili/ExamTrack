from tkinter import *
from tkinter import Button, ttk, messagebox,scrolledtext
import tkinter as tk
from StudentData import *


class BreaksFeature:

    def __init__(self):
        self.flag_other_reason = None
        self.str_reason = None

    def break_window(self, parent, student_id):
        if len(student_id) == 0:
            return

        break_window = Toplevel(parent)
        break_window.geometry("300x320+350+100")
        break_window.resizable(False,False)
        break_window.title("Student Break")
        break_window.configure(bg='#917FB3')

        break_window_reason =  Label(break_window, text="Select Reason:" ,
                                          bg='#917FB3',font=("Calibri", 16 * -1))
        break_window_reason.place(x=30,y=70)


        break_window_id = Label(break_window, text="Student ID:" ,
                                          bg='#917FB3',font=("Calibri", 16 * -1))
        break_window_id.place(x=30,y=30)
        break_window_id2 = Label(break_window, text=student_id ,bg='#917FB3',font=("Calibri", 16 * -1),
                                           borderwidth=1, relief="groove")
        break_window_id2.place(x=120,y=30)

        break_window_text_area = scrolledtext.ScrolledText(break_window, wrap=tk.WORD,bd=3,background="#E5BEEC",
                                  width=25, height=3,font=("Calibri", 16*-1))

        break_window_specify = Label(break_window, text="Please specify:" ,
                                       bg='#917FB3',font=("Calibri", 16 * -1))

        self.str_reason = ""
        self.flag_other_reason = 0

        def break_submit(s_student_id):
            if self.flag_other_reason != 0:
                self.str_reason = break_window_text_area.get("1.0",END)
            if len(self.str_reason) < 3:
                messagebox.showerror("Break Error", "Invalid Reason.",parent=break_window)
            else:
                res = student_report_break(s_student_id,self.str_reason)
                if res == STUDENT_NOT_FOUND:
                    messagebox.showerror("Break Error", "Student not found.", parent=break_window)
                elif res == STUDENT_ALREADY_CONFIRMED:
                    messagebox.showerror("Break Error", "Student already on break.", parent=break_window)
                break_window.destroy()

        # Buttons
        break_confirm_btn = Button(break_window, text='Confirm', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                                  font=("Calibri", 14 * -1),activebackground='#917FB3',height='1',width='12',
                                  disabledforeground='gray',command=lambda: break_submit(student_id))
        break_confirm_btn.place(x = 30, y= 250)

        break_cancel_btn = Button(break_window, text='Cancel', bd='5',fg="#FFFFFF" ,bg='#910ac2',
                                 font=("Calibri", 14 * -1),activebackground='#917FB3',height='1',width='12',
                                 disabledforeground='gray',command=break_window.destroy)
        break_cancel_btn.place(x = 145, y= 250)

        # Combobox functionality
        def reasons_combo_changed(event):
            selected_reason = combo_reasons.get()

            if selected_reason == 'Other':
                break_window_text_area.configure(state='normal')
                break_window_specify.place(x=30,y=140)
                break_window_text_area.place(x=30,y=170)
                self.flag_other_reason = 1
            else:
                break_window_text_area.place_forget()
                break_window_specify.place_forget()
                self.flag_other_reason = 0
                self.str_reason = selected_reason

        reason_list = ['Restroom', 'Medical', 'Other']

        combo_reasons = ttk.Combobox(break_window, state="readonly" , values=reason_list,
                                   background="gray",font=("Calibri", 16 * -1))
        combo_reasons.place(x=30,y=110)

        combo_reasons.bind("<<ComboboxSelected>>", reasons_combo_changed)
