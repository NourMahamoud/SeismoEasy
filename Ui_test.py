from tkinter import ANCHOR
from tkinter import filedialog
import customtkinter as ctk
import shutil
import tempfile
import numpy as np
import pandas as pd
from obspy import read
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os
from obspy.signal.trigger import classic_sta_lta, plot_trigger, trigger_onset, z_detect
from scipy.signal import medfilt
import os
from PIL import Image
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SeismoEasy")
        self.geometry("800x600")
        self.left_frame = ctk.CTkFrame(self, width=220, fg_color='#4E47C6')
        self.left_frame.pack(side="left", fill="y")
        self.right_frame = ctk.CTkFrame(self, fg_color='#07143F')
        self.right_frame.pack(side="right", expand=True, fill="both")
        self.button1 = ctk.CTkButton(self.left_frame, text="AddData", height=35, width=170, corner_radius=32,fg_color="#FAB440", command=self.show_page1)
        self.button1.pack(pady=20)
        self.button1.place(relx=0.5, rely=0.3, anchor="center")
        self.button2 = ctk.CTkButton(self.left_frame, text="ShowSeismogram", height=35, width=170, corner_radius=32,fg_color="#FAB440", command=self.show_page2)
        self.button2.pack(pady=20)
        self.button2.place(relx=0.5, rely=0.4, anchor="center")
        self.button3 = ctk.CTkButton(self.left_frame, text="ShowHistory", height=35, width=170, corner_radius=32,fg_color="#FAB440", command=self.show_page3)
        self.button3.pack(pady=20)
        self.button3.place(relx=0.5, rely=0.5, anchor="center")
        

    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def show_page1(self):

        file_path = filedialog.askopenfilename(filetypes=[("All files", "*")])
        if file_path:
            folder_path = os.path.join(os.getcwd(),"Space Invaders")  # Create a folder named 'Space Invaders' in the current directory
            normalized_path = os.path.normpath(folder_path)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # Create the folder if it doesn't exist
            file_name = os.path.basename(file_path)
            save_path = os.path.join(folder_path, file_name)
            shutil.copy(file_path, save_path)
            print(f"File saved to {save_path}")
            return save_path

            self.clear_right_frame()
            label = ctk.CTkLabel(self.right_frame, text="This is Page 1")
            label.pack(pady=20)

    def show_page2(self):
        folderpath = os.path.join(os.getcwd(), "plots")
        normalized_path1 = os.path.normpath(os.path.join(folderpath, 'plot1.png'))
        self.clear_right_frame()
        scrollable_frame = ctk.CTkScrollableFrame(self.right_frame, width=700, height=500,fg_color='#07143F')
        scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)
        label = ctk.CTkLabel(self.right_frame, text="Seismogram", height=50, width=300)
        label.pack(pady=10)
        if os.path.exists(folderpath):
         image_files = [f for f in os.listdir(folderpath) if f.endswith(".png")]

        if not image_files:
            no_image_label = ctk.CTkLabel(scrollable_frame, text="No plots found.", font=("Arial", 16))
            no_image_label.pack(pady=10)
        for image_file in image_files:
                image_path = os.path.join(folderpath, image_file)
                try:
                    img = ctk.CTkImage(light_image=Image.open(image_path), size=(600, 400))
                    image_label = ctk.CTkLabel(scrollable_frame, image=img, text="")
                    image_label.pack(pady=10)
                except : 
                  text = ctk.CTkTextbox(self.right_frame)
                  text_label = ctk.CTkLabel(self.right_frame,text='No Grave Yet')
                  text_label.pack(pady=20)
    def show_page3(self):

        folder_path = os.path.join(os.getcwd(), "Space Invaders")

        file_list = []
       

        for file_name in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, file_name)):
                # Add the file name to the list
                file_list.append(file_name)

                self.clear_right_frame()
                label = ctk.CTkLabel(self.right_frame, text="Data History")
                label.pack(pady=20)

                for i in range(len(file_list)):
                    button = ctk.CTkButton(self.right_frame,
                                           text=f"{file_list[i]}",
                                           command=lambda i= i: button_callback(file_list[i],folder_path))
                    button.pack(pady=10)

        def button_callback(filename,folderpath):
            filepath = os.path.join(folder_path, filename)
            print(filepath)
            st =read(filepath)
            tr = st[0].copy()
            br = st[0].copy()
            tr_times = tr.times()
            tr_data = tr.data
            br_times = br.times()
            br_data = br.data
            df = tr.stats.sampling_rate
            threshold = 5 * np.std(tr.data)
            spikes = np.abs(tr.data) > threshold
            tr.data[spikes] = np.interp(np.flatnonzero(spikes), np.flatnonzero(~spikes), tr.data[~spikes])
            cft = z_detect(tr_data, int(1000 * df))
            on_off = np.array(trigger_onset(cft, 4, 1.5))
            plot_trigger(br, cft, 4, 1.5, show=False)
            fig = plt.gcf()
            folderpath = os.path.join(os.getcwd(), "plots")
            if not os.path.exists(folderpath):
                os.makedirs(folderpath)
            imagename = os.path.splitext(filename)[0]
            fig.savefig(os.path.join(folderpath,f"{imagename}.png" ))
            # plt.show()
            detection_times = []
            fnames = []

            # Iterate through each trace in the stream
            for tr in st:
                fname = tr.stats.filename if 'filename' in tr.stats else 'unknown'
                starttime = tr.stats.starttime.datetime

            # Iterate through detection times and compile them
            for i in np.arange(0, len(on_off)):
                triggers = on_off[i]
                on_time = starttime + timedelta(seconds=tr_times[triggers[0]])
                on_time_str = datetime.strftime(on_time, '%Y-%m-%dT%H:%M:%S.%f')
                detection_times.append(on_time_str)
                fnames.append(fname)

            # Compile dataframe of detections
            detect_df = pd.DataFrame(data={'filename': fnames, 'time_abs(%Y-%m-%dT%H:%M:%S.%f)': detection_times,
                                           'time_rel(sec)': [tr_times[triggers[0]] for triggers in on_off]})
            print(detect_df.head())
          


if __name__ == "__main__":
    app = App()
    app.mainloop()
