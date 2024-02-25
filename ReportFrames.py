from tkinter import *
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk, messagebox,scrolledtext
from PIL import Image, ImageTk
import tkinter as tk
import numpy as np
from datetime import date,datetime

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import ConnectionPatch
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import FigureCanvasTk



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

        self.canvas.create_rectangle(-1, 50, 1200, 500, fill='#8b77a7', outline='white')


        # temp button
        button1 = tk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame("StartPage"))
        button1.pack()

        self.display_attendance_graph()

    def display_attendance_graph(self):
           # Create a Figure instance
        fig = Figure(figsize=(4.5, 2.5))
        fig.patch.set_alpha(0)

        # Add subplots to the figure
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        fig.subplots_adjust(wspace=0)

        # Pie chart parameters
        overall_ratios = [.27, .56, .17]
        labels = ['Approve', 'Disapprove', 'Undecided']
        explode = [0.1, 0, 0]
        angle = -180 * overall_ratios[0]
        wedges, *_ = ax1.pie(overall_ratios, autopct='%1.1f%%', startangle=angle,
                             labels=labels, explode=explode, colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
        ax1.set_title('Overall Approval')

        # Bar chart parameters
        age_ratios = [.33, .54, .07, .06]
        age_labels = ['Under 35', '35-49', '50-65', 'Over 65']
        bottom = 1
        width = .2

        # Adding from the top matches the legend.
        for j, (height, label) in enumerate(reversed([*zip(age_ratios, age_labels)])):
            bottom -= height
            bc = ax2.bar(0, height, width, bottom=bottom, color='#1f77b4', label=label,
                         alpha=0.1 + 0.25 * j)
            ax2.bar_label(bc, labels=[f"{height:.0%}"], label_type='center')

        ax2.set_title('Age of Approvers')
        ax2.legend()
        ax2.axis('off')
        ax2.set_xlim(- 2.5 * width, 2.5 * width)

        # Use ConnectionPatch to draw lines between the two plots
        theta1, theta2 = wedges[0].theta1, wedges[0].theta2
        center, r = wedges[0].center, wedges[0].r
        bar_height = sum(age_ratios)

        # Draw top connecting line
        x = r * np.cos(np.pi / 180 * theta2) + center[0]
        y = r * np.sin(np.pi / 180 * theta2) + center[1]
        con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                              xyB=(x, y), coordsB=ax1.transData, color='#555555', linewidth=2, linestyle='--')
        ax2.add_artist(con)

        # Draw bottom connecting line
        x = r * np.cos(np.pi / 180 * theta1) + center[0]
        y = r * np.sin(np.pi / 180 * theta1) + center[1]
        con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
                              xyB=(x, y), coordsB=ax1.transData, color='#555555', linewidth=2, linestyle='--')
        ax2.add_artist(con)

        # Convert the Figure to a Tkinter canvas
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas._tkcanvas.config(background='#dbc5db')
        canvas.draw()
        canvas.get_tk_widget().place(x=50, y=100)





