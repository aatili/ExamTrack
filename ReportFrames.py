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


def text_add_border(canvas, label_ref, width=2, bcolor="#d6b0e8"):
    number_bbox = canvas.bbox(label_ref)
    rect_item = canvas.create_rectangle(number_bbox, outline=bcolor, width=width)
    canvas.tag_raise(label_ref, rect_item)


class ReportFrameOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        self.controller = controller
        self.bgimg = tk.PhotoImage(file = "Resources/report_background.png")
        # Creating Canvas
        self.canvas = Canvas(
            self,
            bg = "#FF6EC7",
            height = 600,
            width = 1200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.create_image(0,0,anchor=NW,image=self.bgimg)

        self.canvas.place(x = 0, y = 0)

        #self.canvas.create_rectangle(-1, 50, 1200, 500, fill='#8b77a7')


        # temp button
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame("StartPage"))
        button1.pack()
        button2 = tk.Button(self, text="FrameTwo",
                            command=lambda: controller.show_frame("ReportFrameTwo"))
        button2.pack()

        self.display_attendance_graph()
        self.display_waiver_graph()
        self.display_exam_details()
        self.display_manual_confirm_graph()

    def display_exam_details(self):
        exam_number_label = self.canvas.create_text(
            600.0,
            70.0,
            anchor="nw",
            text=" Exam Number: " + "24133" + " ",
            fill="#d6b0e8",
            font=("Inter Bold", 20 * -1)
        )
        text_add_border(self.canvas, exam_number_label)

        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        exam_term_label = self.canvas.create_text(
            820.0,
            75.0,
            anchor="nw",
            text=" " + "MoedA" + " - " + d1 + " ",
            fill="#d6b0e8",
            font=("Inter Bold", 16 * -1)
        )
        text_add_border(self.canvas, exam_term_label)

        summary_text = "\n" + " - " + "Exams original time: " + "50" + " minutes" + " - Added time: " + "15" + " minutes.\n\n"
        summary_text += " - " + "50" + " Students enlisted for the exam, " + "35" + " of them attended the exam.\n\n"
        summary_text += " - " + "20" + " Students were confirmed using face recognition whereas\n"
        summary_text += "   " + "15" + " Were confirmed manually by the supervisors.\n\n"
        summary_text += " - " + "Most common reason for manual confirm: " + "Face not recognized" + " \n\n"
        # if waiver
        summary_text += " - " + "7" + " Students used the waiver option.\n\n"
        attendance_summary_label = self.canvas.create_text(
            600.0,
            150.0,
            anchor="nw",
            text=summary_text,
            fill="white",
            font=("Inter Bold", 18 * -1)
        )
        text_add_border(self.canvas, attendance_summary_label, 1, 'white')

    def display_attendance_graph(self):

        # Create a frame to hold the canvas
        frame = tk.Frame(self, bd=3, relief=tk.RAISED, background='#dbc5db')
        frame.place(x=50, y=70)

        # Create a Figure instance
        fig = Figure(figsize=(4.5, 2))
        fig.patch.set_alpha(0)

        # Add subplots to the figure
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        fig.subplots_adjust(wspace=0)

        # Pie chart parameters
        overall_ratios = [0.7, .3]
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
        method_ratio = [0.81, .19]
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
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas._tkcanvas.config(background='#dbc5db')
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def display_manual_confirm_graph(self):

        # Create a frame to hold the canvas
        frame = tk.Frame(self, bd=3, relief=tk.RAISED, background='#dbc5db')
        frame.place(x=50, y=325)

        # Sample data
        reason_counts = {'TIME': 10, 'NO PIC': 5, 'FACE_REC': 8, 'OTHER': 7}
        reason_labels = list(reason_counts.keys())
        reason_values = list(reason_counts.values())

        # Create a Figure instance
        fig = Figure(figsize=(3.5, 2.5))
        ax = fig.add_subplot(111)
        fig.patch.set_alpha(0)

        # Plot the donut chart
        wedges, texts, autotexts = ax.pie(reason_values, labels=reason_labels, startangle=90, wedgeprops=dict(width=0.4),
                                          autopct='%1.0f%%', textprops=dict(fontsize=8))

        # Draw a circle in the center to make it a donut chart
        centre_circle = Wedge((0, 0), 0.4, 0, 360, color='white', fill=True)
        ax.add_patch(centre_circle)

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')

        # Add title
        ax.set_title('Reasons for Manual Confirmation',fontsize='small')

        # Convert the Figure to a Tkinter canvas
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas._tkcanvas.config(background='#8b77a7')
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def display_waiver_graph(self):

        # Create a frame to hold the canvas
        frame = tk.Frame(self, bd=3, relief=tk.RIDGE, background='#dbc5db')
        frame.place(x=600, y=450)

        # Bar chart parameters
        waiver_ratio = [0.25, 0.75]
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
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas._tkcanvas.config(background='#dbc5db')
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


class ReportFrameTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.bgimg = tk.PhotoImage(file = "Resources/interface_background.png")
        # Creating Canvas
        self.canvas = Canvas(
            self,
            bg = "#FF6EC7",
            height = 600,
            width = 1200,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.create_image(0,0,anchor=NW,image=self.bgimg)

        self.canvas.place(x = 0, y = 0)

        #self.canvas.create_rectangle(-1, 50, 1200, 500, fill='#8b77a7')


        # temp button
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame("StartPage"))
        button1.pack()

        button2 = tk.Button(self, text="FrameOne",
                            command=lambda: controller.show_frame("ReportFrameOne"))
        button2.pack()

        self.display_exam_details()

    def display_exam_details(self):
        exam_number_label = self.canvas.create_text(
            70.0,
            50.0,
            anchor="nw",
            text=" Exam Number: " + "24133" + " ",
            fill="#d6b0e8",
            font=("Inter Bold", 20 * -1)
        )
        text_add_border(self.canvas, exam_number_label)

        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        exam_term_label = self.canvas.create_text(
            290.0,
            55.0,
            anchor="nw",
            text=" " + "MoedA" + " - " + d1 + " ",
            fill="#d6b0e8",
            font=("Inter Bold", 16 * -1)
        )
        text_add_border(self.canvas, exam_term_label)

        summary_text = "\n " + "15" + " Notes have been given throughout the exam. \n\n"
        # if waiver
        attendance_summary_label = self.canvas.create_text(
            70.0,
            125.0,
            anchor="nw",
            text=summary_text,
            fill="white",
            font=("Inter Bold", 18 * -1)
        )
        text_add_border(self.canvas, attendance_summary_label, 1, 'white')








