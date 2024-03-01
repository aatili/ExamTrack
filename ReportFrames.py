from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox,scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
from datetime import date,datetime

import pandas as pd

from matplotlib.figure import Figure
from matplotlib.patches import Wedge
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator


import ExamConfig
import StudentData

import ReportData


def text_add_border(canvas, label_ref, width=2, bcolor="#d6b0e8"):
    number_bbox = canvas.bbox(label_ref)
    rect_item = canvas.create_rectangle(number_bbox, outline=bcolor, width=width)
    canvas.tag_raise(label_ref, rect_item)


class ReportFrames(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        self.exam = ExamConfig.cur_exam
        self.students = StudentData.students

        self.report_data = ReportData.cur_report

        self.report_frame_one = tk.Frame(self, width=1200, height=600)
        self.report_frame_one.place(x=0, y=0)

        self.report_frame_two = tk.Frame(self, width=1200, height=600)
        #self.report_frame_two.place(x=0, y=0)

        self.frame_one_bg = tk.PhotoImage(file = "Resources/report_background.png")

        self.frame_two_bg = tk.PhotoImage(file = "Resources/interface_background.png")

        self.img_avg_break = tk.PhotoImage(file = "Resources/avg_break.png")

        # temp button
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: self.controller.show_frame("StartPage"))
        button1.pack()
        button2 = tk.Button(self, text="FrameTwo",
                            command=lambda: [self.report_frame_one.place_forget(),
                                             self.report_frame_two.place(x=0, y=0)])
        button2.pack()

        button3 = tk.Button(self, text="FrameOne",
                            command=lambda: [self.report_frame_one.place(x=0, y=0), self.report_frame_two.place_forget()])
        button3.pack()

    def create_report(self):
        if not self.exam.is_loaded_exam():
            self.report_data.create_new_report()
        self.initiate_report_one()
        self.initiate_report_two()

    def initiate_report_one(self):  # Creates first part of the report

        # Creating Canvas
        canvas = Canvas(
            self.report_frame_one,
            bg = "#FF6EC7",
            height = 600,
            width = 1200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.create_image(0,0,anchor=NW,image=self.frame_one_bg)

        canvas.place(x = 0, y = 0)

        # self.canvas.create_rectangle(-1, 50, 1200, 500, fill='#8b77a7')

        # Display exam details and summary

        exam_number_label = canvas.create_text(
            600.0,
            70.0,
            anchor="nw",
            text=" Exam Number: " + str(self.report_data.get_exam_number()) + " ",
            fill="#d6b0e8",
            font=("Inter Bold", 20 * -1)
        )
        text_add_border(canvas, exam_number_label)

        exam_term_label = canvas.create_text(
            825.0,
            75.0,
            anchor="nw",
            text=" " + self.report_data.get_term() + " - " + self.report_data.get_date() + " ",
            fill="#d6b0e8",
            font=("Inter Bold", 16 * -1)
        )
        text_add_border(canvas, exam_term_label)

        summary_text = "\n" + " - " + "Exams original time: " + str(self.report_data.get_duration()) + " minutes" +\
                       " - Added time: " + str(self.report_data.get_added_time()) + " minutes.\n\n"
        summary_text += " - " + str(self.report_data.get_enlisted_count()) + " Students enlisted for the exam, " +\
                        str(self.report_data.get_attendance_count()) + " of them attended the exam.\n\n"
        summary_text += " - " + str(self.report_data.get_auto_confirm_count()) + " Students were confirmed using face " \
                                                                         "recognition whereas\n"
        summary_text += "   " + str(self.report_data.get_manual_confirm_count()) + " Were confirmed manually by the " \
                                                                                   "supervisors.\n\n"

        # Creating Attendance Graph

        # Create a frame to hold the canvas
        attendance_frame = tk.Frame(self.report_frame_one, bd=3, relief=tk.RAISED, background='#dbc5db')
        attendance_frame.place(x=50, y=70)

        # Create a Figure instance
        fig = Figure(figsize=(4.5, 2))
        fig.patch.set_alpha(0)

        # Add subplots to the figure
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        fig.subplots_adjust(wspace=0)

        attended_perc = 0
        if self.report_data.get_enlisted_count() != 0:  # Avoiding Divide by 0
            attended_perc = round(self.report_data.get_attendance_count() / self.report_data.get_enlisted_count(), 2)
        absent_perc = 1-attended_perc
        # Pie chart parameters
        overall_ratios = [attended_perc, absent_perc]
        labels = ['Attended', 'Absent']
        explode = [0.1, 0]
        angle = -180 * overall_ratios[0]
        wedges, *_, texts = ax1.pie(overall_ratios, autopct='%1.1f%%', startangle=angle, labels=labels, explode=explode,
                                    colors=['#1f77b4', 'red', '#2ca02c'])
        ax1.set_title('Overall Attendance',fontsize='medium')

        # Set label size
        for text in texts:
            text.set_fontsize(12)

        # Bar chart parameters
        manual_confirm_perc = 0
        if self.report_data.get_attendance_count() != 0:  # Avoiding Divide by 0
            manual_confirm_perc = round(self.report_data.manual_confirm_count / self.report_data.get_attendance_count(), 2)
        method_ratio = [1-manual_confirm_perc, manual_confirm_perc]
        method_labels = ['Auto', 'Manual']
        bottom = 1
        width = .2

        # Adding from the top matches the legend.
        for j, (height, label) in enumerate(reversed([*zip(method_ratio, method_labels)])):
            bottom -= height
            bc = ax2.bar(0, height, width, bottom=bottom, color='#1f77b4', label=label,
                         alpha=0.3 + 0.5 * j)
            ax2.bar_label(bc, labels=[f"{height:.0%}"], label_type='center')

        ax2.set_title('Confirm method', fontsize='small')
        ax2.legend(bbox_to_anchor=(0.75, 0.5), fontsize='small')
        ax2.axis('off')
        ax2.set_xlim(- 2.5 * width, 2.5 * width)

        # Convert the Figure to a Tkinter canvas
        attendance_canvas = FigureCanvasTkAgg(fig, master=attendance_frame)
        attendance_canvas._tkcanvas.config(background='#dbc5db')
        attendance_canvas.draw()
        attendance_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Manual Confirm Reasons Graph

        # Create a frame to hold the canvas
        manual_confirm_frame = tk.Frame(self.report_frame_one, bd=3, relief=tk.RAISED, background='#dbc5db')
        manual_confirm_frame.place(x=50, y=325)

        # Manual confirm reasons data
        reason_counts = self.report_data.get_manual_confirm_hist()
        reason_values = list(reason_counts.values())

        # Remove labels with 0% value
        reason_labels_filtered = [label for label, value in reason_counts.items() if value != 0]
        reason_values_filtered = [value for value in reason_values if value != 0]

        # Create a Figure instance
        fig = Figure(figsize=(4.5, 2.5))
        ax = fig.add_subplot(111)
        fig.patch.set_alpha(0)

        # Plot the donut chart
        wedges, texts, autotexts = ax.pie(reason_values_filtered, labels=reason_labels_filtered, startangle=90, wedgeprops=dict(width=0.4),
                                          autopct='%1.0f%%', textprops=dict(fontsize=8))

        # Draw a circle in the center to make it a donut chart
        centre_circle = Wedge((0, 0), 0.4, 0, 360, color='#dbc5db', fill=True)
        ax.add_patch(centre_circle)

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')

        # Add title
        ax.set_title('Reasons for Manual Confirmation',fontsize='small')

        # Convert the Figure to a Tkinter canvas
        manual_confirm_canvas = FigureCanvasTkAgg(fig, master=manual_confirm_frame)
        manual_confirm_canvas._tkcanvas.config(background='#8b77a7')
        manual_confirm_canvas.draw()
        manual_confirm_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Display Waiver graph if exam had waiver option
        if self.report_data.is_waiver_available():

            # if waiver
            summary_text += " - " + str(self.report_data.get_waiver_count()) + " Students used the waiver option.\n\n"
            # Create a frame to hold the canvas
            waiver_frame = tk.Frame(self.report_frame_one, bd=3, relief=tk.RIDGE, background='#dbc5db')
            waiver_frame.place(x=600, y=450)

            # Bar chart parameters
            waiver_perc = 0
            if self.report_data.get_attendance_count() != 0:  # Avoiding Divide by 0
                waiver_perc = round(self.report_data.get_waiver_count() / self.report_data.get_attendance_count(), 2)
            waiver_ratio = [waiver_perc, 1-waiver_perc]
            waiver_labels = ['Waiver', 'Continued']
            bottom = 1
            width = .2

            # Create a Figure
            fig = Figure(figsize=(3, 1.1))
            fig.patch.set_alpha(0)

            # Create an Axes within the Figure
            ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

            # Adding from the top matches the legend.
            for j, (height, label) in enumerate(reversed([*zip(waiver_ratio, waiver_labels)])):
                bottom -= height
                bc = ax.barh(0, height, width, left=bottom, color='#ff7f0e', label=label,
                             alpha=0.3 + 0.5 * j, edgecolor='black')
                ax.bar_label(bc, labels=[f"{height:.0%}"], label_type='center')

            ax.set_title('Waiver %', fontsize='small', loc='center', pad=-0, y = 0.85)
            ax.legend( loc='center', bbox_to_anchor=(0.5, 0.1), fontsize='small', ncol=2)
            ax.axis('off')
            ax.set_ylim(- 2.5 * width, 2.5 * width)

            # Convert the Figure to a Tkinter canvas
            waiver_canvas = FigureCanvasTkAgg(fig, master=waiver_frame)
            waiver_canvas._tkcanvas.config(background='#dbc5db')
            waiver_canvas.draw()
            waiver_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Displaying summary at the end (in case we need to add waiver info)
        max_reason = max(self.report_data.get_manual_confirm_hist(), key=self.report_data.manual_confirm_hist.get)
        summary_text += " - " + "Most common reason for manual confirm: " + max_reason + " \n\n"

        attendance_summary_label = canvas.create_text(
            600.0,
            150.0,
            anchor="nw",
            text=summary_text,
            fill="white",
            font=("Inter Bold", 18 * -1)
        )
        text_add_border(canvas, attendance_summary_label, 1, 'white')

    def initiate_report_two(self):

        # Creating Canvas
        canvas = Canvas(
            self.report_frame_two,
            bg = "#FF6EC7",
            height = 600,
            width = 1200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        canvas.create_image(0,0,anchor=NW,image=self.frame_two_bg)

        canvas.place(x = 0, y = 0)

        exam_number_label = canvas.create_text(
            70.0,
            20.0,
            anchor="nw",
            text=" Exam Number: " + str(self.report_data.get_exam_number()) + " ",
            fill="#d6b0e8",
            font=("Inter Bold", 20 * -1)
        )
        text_add_border(canvas, exam_number_label)

        exam_term_label = canvas.create_text(
            295.0,
            25.0,
            anchor="nw",
            text=" " + self.report_data.get_term() + " - " + self.report_data.get_date() + " ",
            fill="#d6b0e8",
            font=("Inter Bold", 16 * -1)
        )
        text_add_border(canvas, exam_term_label)

        summary_text = "\n - " + str(self.report_data.get_notes_count()) + " Notes have been given throughout the exam. \n\n"
        summary_text += " - " + str(self.report_data.get_breaks_count()) + " Students took a break\n\n"

        break_avg_seconds = self.report_data.get_avg_break_time()
        break_avg_time = divmod(break_avg_seconds, 60)

        summary_text += " - " + "Break length on average: " + str(break_avg_time[0]) + " minutes " \
                        + str(break_avg_time[1]) + " seconds \n\n"

        attendance_summary_label = canvas.create_text(
            70.0,
            70.0,
            anchor="nw",
            text=summary_text,
            fill="white",
            font=("Inter Bold", 18 * -1)
        )
        text_add_border(canvas, attendance_summary_label, 1, 'white')

        # Display Notes graph (hist)

        # Create a frame to hold the canvas
        notes_frame = tk.Frame(self.report_frame_two, bd=3, relief=tk.RAISED, background='#dbc5db')
        notes_frame.place(x=550, y=20)

        '''notes_dict = {'311244057' : 3 , '206902111' : 2 , '311255932' : 1 , '909090122' : 1,
                      '311244157' : 3 , '216902111' : 2 , '312255932' : 1 , '929090122' : 1,
                      '311244151' : 3 , '216902112' : 2 , '312255933' : 1 , '929090124' : 1}'''

        notes_dict = self.report_data.get_notes_hist()
        # Convert dictionary keys and values to lists
        student_ids = list(notes_dict.keys())
        notes_given = list(notes_dict.values())

        # Create a new figure
        fig = Figure(figsize=(6, 3))
        fig.patch.set_alpha(0)

        # Add subplot
        ax = fig.add_subplot(111)

        # Create histogram
        ax.bar(student_ids, notes_given, width=0.3, color='#d2700a')

        ax.set_facecolor('#dbc5db')

        # Rotate the ID labels vertically
        ax.set_xticklabels(student_ids, rotation=315)

        # Set the size of the x-axis label ticks
        ax.tick_params(axis='x', which='major', labelsize=8)  # Adjust the label size as needed (here, 10 points)


        # Set y-axis ticks to integers only
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Adjust padding to make the plot take less space
        fig.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.25)

        # Add labels and title
        # ax.set_xlabel('Student ID')
        ax.set_ylabel('Number of Notes')
        ax.set_title('Number of Notes Given by Student', fontsize='medium')

        # Convert the Figure to a Tkinter canvas
        notes_canvas = FigureCanvasTkAgg(fig, master=notes_frame)
        notes_canvas._tkcanvas.config(background='#8b77a7')
        notes_canvas.draw()
        notes_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Breaks Reasons Graph

        # Create a frame to hold the canvas
        breaks_reasons_frame = tk.Frame(self.report_frame_two, bd=3, relief=tk.SUNKEN, background='#dbc5db')
        breaks_reasons_frame.place(x=835, y=360)

        # Create a Figure instance
        fig = Figure(figsize=(3, 2))
        fig.patch.set_alpha(0)

        # Add subplot
        ax = fig.add_subplot(111)

        # breaks reasons data
        breaks_reasons_counts = self.report_data.get_breaks_reasons_hist()

        total_count = sum(breaks_reasons_counts.values())

        # overall_ratios = [0 for count in breaks_reasons_counts.values()]
        if total_count != 0:
            # Calculate ratios for each reason
            overall_ratios = [count / total_count for count in breaks_reasons_counts.values()]
            # Round the ratios to two decimal places
            overall_ratios = [round(ratio, 2) for ratio in overall_ratios]

            reasons_labels_filtered = [label for label, value in breaks_reasons_counts.items() if value != 0]
            ratios_filtered = [value for value in overall_ratios if value != 0]

            # Pie chart parameters

            angle = -180 * overall_ratios[0]
            wedges, *_, texts = ax.pie(ratios_filtered, autopct='%1.1f%%', startangle=angle, labels=reasons_labels_filtered,
                                       colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
            ax.set_title('Breaks Reasons',fontsize='medium')

            # Set label size
            for text in texts:
                text.set_fontsize(8)

            # Convert the Figure to a Tkinter canvas
            breaks_reasons_canvas = FigureCanvasTkAgg(fig, master=breaks_reasons_frame)
            breaks_reasons_canvas._tkcanvas.config(background='#dbc5db')
            breaks_reasons_canvas.draw()
            breaks_reasons_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Display Breaks Time Distribution

        # Create a frame to hold the canvas
        breaks_time_frame = tk.Frame(self.report_frame_two, bd=3, relief=tk.RAISED, background='#dbc5db')
        breaks_time_frame.place(x=350, y=360)

        '''breaks_dict = {'311244057' : 150 , '206902111' : 200 , '311255932' : 500 , '909090122' : 1200,
                      '311244157' : 800 , '216902111' : 600 , '312255932' : 750 , '929090122' : 900,
                      '311244151' : 1100 , '216902112' : 620 , '312255933' : 720 , '929090124' : 270}'''

        breaks_dict = self.report_data.get_breaks_time_hist()

        # Convert dictionary keys and values to lists
        student_ids_b = list(breaks_dict.keys())
        student_breaks_time = list(breaks_dict.values())

        break_times_minutes = [time / 60 for time in student_breaks_time]

        # Create a new figure
        fig = Figure(figsize=(4, 2))
        fig.patch.set_alpha(0)

        # Add subplot
        ax = fig.add_subplot(111)

        # Create histogram
        #ax.bar(student_ids_b, break_times_minutes, width=0.3,color='#ad0309')

        # Create scatter plot
        ax.scatter(student_ids_b, break_times_minutes, color='#4e075c', marker='+')

        # Calculate the average break time
        average_break_time = np.mean(break_times_minutes)

        # Display the average break time as a horizontal line
        ax.axhline(y=average_break_time, color='red', linestyle='--', label='Average Break Time')

        ax.set_facecolor('#8b77a7')

        # Hide the labels on the x-axis
        ax.set_xticklabels([])

        # Set y-axis ticks to integers only
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Add a legend
        #ax.legend()
        canvas.create_image(350, 320, anchor=NW, image=self.img_avg_break)

        # Adjust padding to make the plot take less space
        fig.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.1)

        # Add labels and title
        ax.set_ylabel('Break Time (minutes)')
        ax.set_title('Break Time Distribution', fontsize='medium')

        # Convert the Figure to a Tkinter canvas
        breaks_time_canvas = FigureCanvasTkAgg(fig, master=breaks_time_frame)
        breaks_time_canvas._tkcanvas.config(background='#dbc5db')
        breaks_time_canvas.draw()
        breaks_time_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Break features buttons
        view_table_btn = Button(self.report_frame_two, text='View Table', bd='4', fg="#FFFFFF", bg='#812e91', font=("Calibri", 16 * -1),
                               activebackground='#917FB3', height='1', width='14', disabledforeground='gray')
        view_table_btn.place(x = 70,y = 290)


    # self.table = None
    # self.display_table()
    # Display Table
    def display_table(self):
        # Create a Frame to contain the Treeview
        frame = ttk.Frame(self, borderwidth=2)
        frame.place(x=650, y=50)

        # Creating Table
        self.table = ttk.Treeview(master=frame)

        self.table.tag_configure('oddrow', background='#917FB3')
        self.table.tag_configure('evenrow', background='#BAA4CA')

        table_columns = self.students.student_table_columns()
        self.table.configure(columns=table_columns, show="headings")
        for column in table_columns:
            self.table.heading(column=column, text=column)
            self.table.column(column=column, width=70)

        color_j = 0
        table_data = self.students.student_table_values()
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

        # Set the height of the Treeview
        self.table["height"] = 6

        # Create a vertical scrollbar
        y_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)

        # Configure the Treeview to use the scrollbar
        self.table.configure(yscrollcommand=y_scrollbar.set)

        # Pack the Treeview and scrollbar
        self.table.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")

        #self.table.pack(fill="both", expand=True)
        #self.table.place(x=650, y=50, height=200)







