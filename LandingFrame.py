from tkinter import *
from tkinter import Canvas, Button, PhotoImage, ttk, messagebox, filedialog
from PIL import Image, ImageTk
import tkinter as tk
import pandas as pd
from datetime import datetime
import re

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

        self.current_folder = -1

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

        welcome_message = """
     Welcome to ExamTrack!       
     Below are some instructions to help you get started:
            
     Starting the Exam:
     - Click on the "Start Exam" button to begin a new exam session.
     - Follow the on-screen prompts to set up exam parameters.
     - Once everything is set up, click "Continue" to initiate the
     exam process.
     - Use the face recognition feature to confirm attendance.
            
     Accessing Report History:
     - Click on the "View Reports" button to access past exam reports.
     - Browse through the list of available reports to find the one you're  
     interested in.
     - Click on a Load Report to view detailed information, including
     attendance records, break history, notes, and more.
     - Use the search and filter options to quickly find specific reports
            """
        help_msg = """
            Need Help?
            If you have any questions or encounter any issues while using 
            ExamTrack, don't hesitate to reach out to our support team for assistance.
            We're here to help make your exam management experience as smooth and 
            efficient as possible.
            """
        welcome_message_label = self.canvas.create_text(
            600.0,
            150.0,
            anchor="nw",
            text=welcome_message,
            fill="white",
            font=("Inter Bold", 18 * -1)
        )
        ReportFrames.text_add_border(self.canvas, welcome_message_label, 1, 'white')

        exit_btn = Button(self.landing_frame, text='Exit', bd='5', fg="#FFFFFF", bg='#812e91',
                          font=("Calibri", 16 * -1),
                          activebackground='#917FB3', height='1', width='14',
                          command=lambda: self.controller.on_closing())
        exit_btn.place(x=390, y=350)

        credits_btn = Button(self.landing_frame, text='Credits', bd='5', fg="#FFFFFF", bg='#812e91',
                             font=("Calibri", 16 * -1),
                             activebackground='#917FB3', height='1', width='14',
                             command=lambda: self.show_load_reports())
        credits_btn.place(x=390, y=290)

        load_btn = Button(self.landing_frame, text='View Reports', bd='5', fg="#FFFFFF", bg='#812e91',
                          font=("Calibri", 16 * -1),
                          activebackground='#917FB3', height='1', width='14',
                          command=lambda: self.show_load_reports())
        load_btn.place(x=390, y=230)

        start_btn = Button(self.landing_frame, text='Start Exam', bd='5', fg="#FFFFFF", bg='#812e91',
                           font=("Calibri", 16 * -1),
                           activebackground='#917FB3', height='1', width='14',
                           command=lambda: self.controller.show_frame('StartPage'))
        start_btn.place(x=390, y=170)

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

        canvas.create_rectangle(795, 285, 880, 370, fill='#917FB3', outline='black')

        # Function to retrieve list of folders from Firebase
        def get_folder_list():

            folder_list = []
            bucket = self.firebase_manager.get_bucket()
            folder_ref = bucket.list_blobs(prefix=f'{FirebaseManager.FIREBASE_REPORT_HISTORY_PATH}/')

            # Set to store processed folder names
            processed_folders = set()

            # Iterate over the items in the folder
            for f_item in folder_ref:
                # Extract the folder name from the object path
                folder_name = f_item.name.split('/')[1]  # Get the second part of the path as folder name

                pattern = re.compile(r'[^\w\s]+')

                # Remove non-printable characters using the pattern
                cleaned_folder_name = pattern.sub('', folder_name)

                if cleaned_folder_name in processed_folders:
                    continue

                # Define the regex pattern
                pattern = r'^Report_\d+_(MoedA|MoedB|MoedC)_(\d{2})(\d{2})(\d{2})$'
                # Check if folder name matches the pattern
                if not re.match(pattern, cleaned_folder_name):
                    # print(cleaned_folder_name)
                    continue

                # Extract exam number, term, and date from folder name
                parts = cleaned_folder_name.split('_')
                exam_number = parts[1]
                term = parts[2]
                date = parts[3]

                # Reformat date from DDMMYY to DD/MM/YY
                date = f"{date[:2]}/{date[2:4]}/{date[4:]}"

                # Add folder details to the list
                folder_list.append((exam_number, term, date, cleaned_folder_name))

                # Add the folder name to the processed folders set
                processed_folders.add(cleaned_folder_name)

            return folder_list

        # Create a Frame to contain the Treeview
        frame = ttk.Frame(self.load_report_frame, borderwidth=2)
        frame.place(x=400, y=170)

        def sort_by_date(row_data):
            # Custom comparison function for sorting by date
            return datetime.strptime(row_data[2], "%d/%m/%y")

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
        for folder in sorted(folders, key=sort_by_date, reverse=True):
            color_tags = ('evenrow',) if color_j % 2 == 0 else ('oddrow',)
            folder_table.insert('', 'end', values=folder, tags=color_tags)
            color_j += 1
        folder_table.column('#1', width=90)
        folder_table.column('#2', width=60)
        folder_table.column('#3', width=80)
        folder_table.column('#4', width=50)

        def table_select_row(a):  # view selected row items
            cur_item = folder_table.focus()
            cur_values = folder_table.item(cur_item, option='values')
            if not cur_values:
                return
            self.current_folder = str(cur_values[3])

        folder_table.bind("<<TreeviewSelect>>", table_select_row)

        # Convert the table data to a pandas DataFrame
        data = []
        for item in folder_table.get_children():
            data.append(folder_table.item(item)['values'])

        df_backup = pd.DataFrame(data, columns=['id', 'Term', 'Date', 'Folder Name'])

        # Convert 'Date' column to datetime format
        df_backup['Date'] = pd.to_datetime(df_backup['Date'], format='%d/%m/%y')

        # Sort the DataFrame by 'Date'
        df_backup.sort_values(by='Date', inplace=True, ascending=False)

        # Format 'Date' column to display only 'dd/mm/yy'
        df_backup['Date'] = df_backup['Date'].dt.strftime('%d/%m/%y')

        # Convert to str for easier handling
        df_backup['Date'] = df_backup['Date'].astype(str)
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

            # Sort the filtered results based on the original order in df_backup
            sorted_results = sorted(r_set, key=lambda x: table_df[table_df['id'] == x[0]].index[0])

            j = 0  # similar to color j , counter for colouring purpose
            for dt in sorted_results:
                tags = ('evenrow',) if j % 2 == 0 else ('oddrow',)  # for colouring purpose
                v = [r for r in dt]  # creating a list from each row
                # Handling checkbox statuses
                s_id = v[0]
                s_term = v[1]
                if moeda_checkbox_var.get() == 1:
                    if str(s_term).lower() == 'moeda':
                        folder_table.insert("", "end", iid=s_id, values=v, tags=tags)  # adding row
                        j += 1  # colouring
                if moedb_checkbox_var.get() == 1:
                    if str(s_term).lower() == 'moedb':
                        folder_table.insert("", "end", iid=s_id, values=v, tags=tags)  # adding row
                        j += 1  # colouring
                if moedc_checkbox_var.get() == 1:
                    if str(s_term).lower() == 'moedc':
                        folder_table.insert("", "end", iid=s_id, values=v, tags=tags)  # adding row
                        j += 1  # colouring
                if moedc_checkbox_var.get() == 0 and moedb_checkbox_var.get() == 0 and moeda_checkbox_var.get() == 0:
                    folder_table.insert("", "end", iid=s_id, values=v, tags=tags)  # adding row
                    # j += 1  # colouring

        search_entry.bind("<KeyRelease>", my_search)

        back_btn = tk.Button(self.load_report_frame, text='Back', bd='4', fg="#FFFFFF", bg='#812e91',
                             activebackground='#917FB3',
                             font=("Calibri", 16 * -1), height='1', width='14'
                             , command=lambda: [self.landing_frame.place(x=0, y=0),
                                                self.load_report_frame.place_forget()])
        back_btn.place(x=30, y=30)

        def load_btn_event():
            if self.current_folder == -1:
                return
            res = self.controller.frames["ReportFrames"].create_report(True, self.current_folder)
            if not res:
                messagebox.showerror("Load Report Error", "Failed to load report.")
            else:
                self.controller.show_frame("ReportFrames")

        # continue btn
        load_btn = Button(self.load_report_frame, text='Load Report', bd='5', fg="#FFFFFF", bg='#812e91',
                          font=("Calibri", 16 * -1),
                          activebackground='#917FB3', height='1', width='14',
                          command=load_btn_event)
        load_btn.place(x=795, y=410)

        # Checkboxes
        moeda_checkbox_var = IntVar()
        moeda_checkbox = Checkbutton(self.load_report_frame, variable=moeda_checkbox_var, onvalue=1, offvalue=0, height=1,
                                         font=("Inter Bold", 14 * -1), text="MoedA", bg="#917FB3",
                                         command=my_search)
        moeda_checkbox.place(x=800, y=290)

        moedb_checkbox_var = IntVar()
        moedb_checkbox = Checkbutton(self.load_report_frame, variable=moedb_checkbox_var, onvalue=1, offvalue=0, height=1,
                                     font=("Inter Bold", 14 * -1), text="MoedB", bg="#917FB3",
                                     command=my_search)
        moedb_checkbox.place(x=800, y=315)

        moedc_checkbox_var = IntVar()
        moedc_checkbox = Checkbutton(self.load_report_frame, variable=moedc_checkbox_var, onvalue=1, offvalue=0, height=1,
                                     font=("Inter Bold", 14 * -1), text="MoedC", bg="#917FB3",
                                     command=my_search)
        moedc_checkbox.place(x=800, y=340)
