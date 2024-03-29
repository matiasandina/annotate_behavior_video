from tkinter import *
from tkinter.font import Font
from tkinter import messagebox
from tkinter import filedialog
import PIL.Image, PIL.ImageTk
import cv2
import pandas as pd
import time

# For plots we need
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import yaml
import os

# TODO: add colors/style to matplotlib
# TODO: Allow for user to populate behavior categories at will
# TODO: Add function on_key_press
# TODO: Add ask before quit


# def on_key_press(event):
#    print("you pressed {}".format(event.key))
#    key_press_handler(event, canvas, toolbar)

class videoGUI:

    def __init__(self, window, window_title):

        # region window creation
        self.window = window
        self.window.title(window_title)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.home = os.path.expanduser('~')

        top_frame = Frame(self.window)
        top_frame.pack(side=TOP, pady=5)

        middle_frame = Frame(self.window)
        middle_frame.pack(side=TOP, pady=5)

        bottom_frame = Frame(self.window)
        bottom_frame.pack(side=BOTTOM, pady=5)

        annotation_frame = Frame(self.window)
        annotation_frame.pack(side=BOTTOM, pady=5)

        # Create pop-up for controls
        self.top = Toplevel()
        self.top.protocol("WM_DELETE_WINDOW", self.disable_event)

        # endregion

        # Region init variables

        self.pause = False   # Parameter that controls pause button

        self.canvas = Canvas(top_frame)
        self.canvas.pack()

        self.data = pd.DataFrame({'frameID':[], 'behavior':[]})

        self.annotate_flag = "off"

        # endregion


        # MAIN WINDOW
        # frame slider
        self.frame_slider = Scale(middle_frame, from_=0, to=500,
                                          orient=HORIZONTAL,
                                          sliderlength=15, length=800,
                                  # roughly 30 fps * 60 sec * 30 min
                                  tickinterval=30*60*30, 
                                  command=self.get_slider_values)
        self.frame_slider.grid(row=0, column=0)

        self.back_button = Button(middle_frame, text = "Back 300 frames", width=14, command=self.back_frames)
        self.back_button.grid(row=1, column =0)


        # Define start frame at 0
        self.current_frame = 0
        self.slider_pos = 0

        # Select Button
        self.btn_select=Button(bottom_frame, text="Select video file", width=15, command=self.open_file)
        self.btn_select.grid(row=1, column=0)

        self.btn_prev=Button(bottom_frame, text="Load Previous Data", width=15, command=self.load_csv)
        self.btn_prev.grid(row=1, column=1)

        # Play Button
        self.btn_play=Button(bottom_frame, text="Start", width=15, command=self.play_video)
        self.btn_play.grid(row=1, column=2)

        # Pause Button
        self.btn_pause=Button(bottom_frame, text="Play/Pause", width=15, command=self.play_pause_video)
        self.btn_pause.grid(row=1, column=3)

        self.btn_save=Button(bottom_frame, text="Save", width=15, command=self.save_data)
        self.btn_save.grid(row=1, column=4)

        # Create Var for annotation

        self.var=StringVar()
        self.var.set('not-specific')

        # Region radiobuttons

        with open("config.yaml", "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        self.b_dict = {}
        for key in self.config["behaviors"]:
            self.b_dict[key] = Radiobutton(annotation_frame, text=key, bd=4, width=12, command=self.print_var)
            self.b_dict[key].config(indicatoron=0, variable=self.var, value=key)
            self.b_dict[key].pack(side='left')

        # endregion

        # TOP WINDOW

        # Button that lets the user take annotate
        # we are going to disable it when it's being "active", it works more like a toggle
        # so instead of activeforeground and activebackground we use disabledforeground
        self.btn_annotate = Button(self.top, text="Annotate", width=50, command=self.annotate, 
            disabledforeground='#428249', activebackground = "#93B365",
            font = Font(size = 12))
        self.btn_annotate.pack(anchor=CENTER, expand=True)

        self.btn_stop_annotate = Button(self.top, text="Stop Annotate", width=50, command=self.stop_annotate,
            font = Font(size = 12))
        self.btn_stop_annotate.pack(anchor=CENTER, expand=True)

        self.fig = Figure(figsize=(5, 4), dpi=100)


        #self.t = np.array(self.data)
        self.ax = self.fig.add_subplot(111)
        # Mind the comma! it's to get only one output
        self.ethogram, = self.ax.plot(self.data["frameID"], self.data["behavior"], '|', markersize=20)


        self.top_canvas = FigureCanvasTkAgg(self.fig, master=self.top)  # A tk.DrawingArea.
        self.top_canvas.draw()
        self.top_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.top_canvas, self.top)
        self.toolbar.update()
        self.top_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)


        # HotKey Bindings
        self.window.bind("<space>", self.play_pause_video)
        self.key_options = ["a","s", "d", "f", "g", "h", "j", "k", "l"]
        if len(self.config["behaviors"]) > len(self.key_options):
            print(f"More behaviors {len(self.config['behaviors'])} than key_options")
        self.key_options = self.key_options[:len(self.config["behaviors"])]
        for i, hotkey in enumerate(self.key_options):
            behavior_i = self.config["behaviors"][i]
            self.window.bind(hotkey, self.switch_radiobutton)


        self.delay = 15   # ms

        self.window.mainloop()

    def switch_radiobutton(self, event):
        for i, hotkey in enumerate(self.key_options):
            if event.char == hotkey:
                behavior_i = self.config["behaviors"][i]
                self.var.set(behavior_i)
                break

    def open_file(self):

        self.pause = False
        self.filename = filedialog.askopenfilename(initialdir = self.home, title="Select file")
        print("Trying to read...")
        print(self.filename)

        # Open the video file
        self.cap = cv2.VideoCapture(self.filename)

        # Get the properties of the video
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

        # Configure slider
        self.frame_slider.configure(to=self.total_frames)

        # Create space in the data
        self.data["frameID"] = range(0, int(self.total_frames))
        self.data["behavior"] = "NA"


        self.canvas.config(width = self.width, height = self.height)

    def get_slider_values(self, event):
        self.slider_pos = self.frame_slider.get()

    def annotate(self):

        if str(self.btn_annotate["state"]) == "active":
            # First disable button
            self.btn_annotate.configure(state=DISABLED)

        # Set a flag to mark you are annotating
        self.annotate_flag = "on"
        print(int(self.current_frame))
        # Set values on data
        self.data.at[int(self.current_frame),"behavior"] = self.current_behavior

        # print(self.data.iloc[self.current_frame-1:self.current_frame+2])
        print("Annotating..." + self.current_behavior)

    def stop_annotate(self):
        # Enable annotate button back
        self.btn_annotate.configure(state=NORMAL)
        self.annotate_flag = "off"


    def print_var(self, *args):
        print("Changing to " + self.var.get())

    def get_frame(self):   # get only one frame
        try:
            if self.cap.isOpened():
                ret, frame = self.cap.read(self.current_frame)
                #self.current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        except:
            messagebox.showerror(title='Video file not found', message='Please select a video file.')

    # This is the main function that we use to 'loop/update'
    def play_video(self):

        # First disable play button to prevent multiple instances of play
        self.disable_start_button()

        # Check if the slider has been moved
        if abs(self.slider_pos - self.current_frame) > 1:
            # Update the current frame
            self.current_frame = self.slider_pos
            # set the camera for that frame >>> THIS IS THE IMPORTANT TELL THE CAMERA WHAT"S THE NEXT FRAME!
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame - 1)

        # stop if needed
        if self.current_frame > self.total_frames:
            self.pause = True
            messagebox.showerror(title='End of video', message='End of video!')

        # Get a frame from the video source, and go to the next frame automatically
        ret, frame = self.get_frame()

        # Show frame
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = NW)


        # Get the behavior
        self.current_behavior = self.var.get()
        # Call the annotate function
        if self.annotate_flag == "on":
            self.annotate()

        # update plot every 10 frames
        # We do this for speed purposes (we don't really need to refresh that fast)
        if self.current_frame % 10 == 0:
            self.refreshFigure()

        # If not pause, call this function again (aka, keep playing)
        if not self.pause:
            # increase the frame number
            self.current_frame = self.current_frame + 1

            # update the slider
            self.frame_slider.set(self.current_frame)
            self.window.after(self.delay, self.play_video)


    # This function serves as a toggle for play/pause
    def play_pause_video(self, event=None):
        if self.pause == False:
            self.pause = True
            self.play_video()
        else:
            self.pause = False
            self.play_video()

    def back_frames(self):
        self.play_pause_video()
        self.frame_slider.set(self.current_frame - 300)

    # We need to disable start so there are not a lot of instances
    def disable_start_button(self):
        self.btn_play.configure(state=DISABLED)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?\nALL UNSAVED DATA WILL BE LOST"):
            self.__del__()

    # Release the video source when the object is destroyed
    def __del__(self):
        self.top.quit()


    # This will prevent the user from closing the top window (which stalls the program)
    def disable_event(self):
        pass

    def refreshFigure(self):

        # Clear the axis
        self.ax.clear()

        # new range
        x_min = max(0, self.current_frame - 500)
        x_max = min(self.current_frame + 500, self.total_frames)

        # We want them for indexing so change them to integers
        x_min = int(x_min)
        x_max = int(x_max)

        # Subset the portions we care about
        x = self.data["frameID"][x_min:x_max]
        y = self.data["behavior"][x_min:x_max]


        # make the new plot
        self.ax.plot(x, y, '|', markersize=20)
        self.ax.plot(self.current_frame, y[self.current_frame], '|', markersize=20, color='red')
        self.ax = self.top_canvas.figure.axes[0]
        self.ax.set_xlim(x_min, x_max)
        # ax.set_ylim(y.min(), y.max())
        self.top_canvas.draw()

    def save_data(self):
        filename = filedialog.asksaveasfilename(title="Type filename to save",
                                                filetypes = (("csv files","*.csv"),("all files","*.*")))
        self.data.to_csv(filename, index=False)

    def load_csv(self):
        filename = filedialog.askopenfilename(initialdir=self.home, 
            title="Select Previous Annotated Data", 
            filetypes=(("csv files", "*.csv"),("all files","*.*")))
        #  keep_default_na=False helps to read NA as string
        self.data = pd.read_csv(filename,  keep_default_na=False)


##### End Class #####


print("Starting app...")

time.sleep(1)


# Create a window and pass it to videoGUI Class
videoGUI(Tk(), "Video player")