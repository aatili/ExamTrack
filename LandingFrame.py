from tkinter import *
from tkinter import Canvas, Button, PhotoImage, ttk, messagebox, filedialog
from PIL import Image, ImageTk
import tkinter as tk
import pandas as pd

import FirebaseManager
import ReportFrames


class LandingFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bgimg = tk.PhotoImage(file="Resources/start_background.png")

        self.firebase_manager = FirebaseManager.firebase_manager

        self.landing_frame = tk.Frame(self, width=1200, height=600)
        self.landing_frame.place(x=0, y=0)

        self.load_report_frame = tk.Frame(self, width=1200, height=600)

        # Creating Canvas
        self.canvas = Canvas(
            self.landing_frame,
            bg="#2A2F4F",
            height=600,
            width=1200,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        self.canvas.create_image(0, 0, anchor=NW, image=self.bgimg)

        self.canvas.place(x=0, y=0)

        load_btn = Button(self.landing_frame, text='View Reports', bd='5', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                          activebackground='#917FB3', height='1', width='14',
                          command=lambda: self.show_load_reports())
        load_btn.place(x=400, y=270)

        start_btn = Button(self.landing_frame, text='Start Exam', bd='5', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                           activebackground='#917FB3', height='1', width='14',
                           command=lambda: self.controller.show_frame('StartPage'))
        start_btn.place(x=400, y=200)

    def show_load_reports(self):
        self.landing_frame.place_forget()
        self.load_report_frame.place(x=0, y=0)
        # Creating Canvas
        canvas = Canvas(
            self.load_report_frame,
            bg="#2A2F4F",
            height=600,
            width=1200,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.create_image(0, 0, anchor=NW, image=self.bgimg)

        canvas.place(x=0, y=0)

        # Function to retrieve list of folders from Firebase
        def get_folder_list():

            folder_list = []
            bucket = self.firebase_manager.get_bucket()
            folder_ref = bucket.list_blobs(prefix=f'{FirebaseManager.FIREBASE_REPORT_HISTORY_PATH}/')

            # Iterate over the items in the folder
            for f_item in folder_ref:
                # Extract the folder name from the object path
                folder_name = f_item.name.split('/')[1]  # Get the second part of the path as folder name

                # Extract exam number, term, and date from folder name
                parts = folder_name.split('_')
                exam_number = parts[1]
                term = parts[2]
                date = parts[3]

                # Reformat date from DDMMYY to DD/MM/YY
                date = f"{date[:2]}/{date[2:4]}/{date[4:]}"

                # Add folder details to the list
                folder_list.append((exam_number, term, date, folder_name))

            return folder_list

        # Create a Frame to contain the Treeview
        frame = ttk.Frame(self.load_report_frame, borderwidth=2)
        frame.place(x=400, y=170)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, background="#917FB3", fieldbackground="#917FB3", foreground="white",
                        font=("Calibri", 14 * -1))
        style.configure("Treeview.Heading", rowheight=30, background="#917FB3", fieldbackground="#917FB3",
                        foreground="white", font=("Calibri", 14 * -1))
        style.map("Treeview.Heading", background=[("active", "#917FB3"), ("!active", "#917FB3")],
                  foreground=[("active", "white"), ("!active", "white")])
        style.map("Treeview", background=[("selected", "#000080")])

        # Create a table to display the folder list
        folder_table = ttk.Treeview(master=frame, columns=('Exam Number', 'Term', 'Date', 'Folder Name'),
                                    show='headings')
        folder_table.heading('Exam Number', text='Exam Number')
        folder_table.heading('Term', text='Term')
        folder_table.heading('Date', text='Date')
        folder_table.heading('Folder Name', text='Folder Name')

        folder_table.tag_configure('oddrow', background='#917FB3')
        folder_table.tag_configure('evenrow', background='#BAA4CA')

        folder_table["height"] = 10

        # Pack the Treeview
        folder_table.pack(side="left", fill="both", expand=True)

        # Get the list of folders from Firebase
        folders = get_folder_list()

        # Clear any existing data in the table
        for row in folder_table.get_children():
            folder_table.delete(row)

        color_j = 0
        # Populate the table with folder names
        for folder in folders:
            color_tags = ('evenrow',) if color_j % 2 == 0 else ('oddrow',)
            folder_table.insert('', 'end', values=folder, tags=color_tags)
            color_j += 1
        folder_table.column('#1', width=90)
        folder_table.column('#2', width=60)
        folder_table.column('#3', width=80)
        folder_table.column('#4', width=50)

        # Convert the table data to a pandas DataFrame
        data = []
        for item in folder_table.get_children():
            data.append(folder_table.item(item)['values'])

        df_backup = pd.DataFrame(data, columns=['id', 'Term', 'Date', 'Folder Name'])

        df_backup['id'] = df_backup['id'].astype(str)

        # Searching the table

        canvas.create_text(
            795,
            200,
            anchor="nw",
            text="Search Exam Number:",
            fill="#FFFFFF",
            font=("Calibri Bold", 18 * -1)
        )

        search_entry = tk.Entry(self.load_report_frame, width=20, bg="#917FB3", font=18, borderwidth=3)
        search_entry.place(x=795, y=235)

        # Search query and filter table
        def my_search(*args):
            table_df = df_backup
            query = search_entry.get().strip()  # get entry string
            str1 = table_df.id.str.contains(query, case=False)
            df2 = table_df[str1]
            r_set = df2.to_numpy().tolist()  # Create list of list using rows
            folder_table.delete(*folder_table.get_children())
            j = 0  # similar to color j , counter for colouring purpose
            for dt in r_set:
                tags = ('evenrow',) if j % 2 == 0 else ('oddrow',)  # for colouring purpose
                v = [r for r in dt]  # creating a list from each row
                # Handling checkbox statuses
                s_id = v[0]
                folder_table.insert("", "end", iid=s_id, values=v, tags=tags)  # adding row
                j += 1  # colouring

        search_entry.bind("<KeyRelease>", my_search)

        back_btn = tk.Button(self.load_report_frame, text='Back', bd='4', fg="#FFFFFF", bg='#812e91',
                             activebackground='#917FB3',
                             font=("Calibri", 16 * -1), height='1', width='14'
                             , command=lambda: [self.landing_frame.place(x=0, y=0), self.load_report_frame.place_forget()])
        back_btn.place(x=30, y=30)
