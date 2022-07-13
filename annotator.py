from tkinter import *
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
                                  tickinterval=600, command=self.get_slider_values)
        self.frame_slider.grid(row=0, column=0)


        # Define start frame at 0
        self.current_frame = 0
        self.slider_pos = 0

        # Select Button
        self.btn_select=Button(bottom_frame, text="Select video file", width=15, command=self.open_file)
        self.btn_select.grid(row=1, column=0)

        # Play Button
        self.btn_play=Button(bottom_frame, text="Start", width=15, command=self.play_video)
        self.btn_play.grid(row=1, column=1)

        # Pause Button
        self.btn_pause=Button(bottom_frame, text="Play/Pause", width=15, command=self.play_pause_video)
        self.btn_pause.grid(row=1, column=2)

        self.btn_save=Button(bottom_frame, text="Save", width=15, command=self.save_data)
        self.btn_save.grid(row=1, column=3)

        # Create Var for annotation

        self.var=StringVar()
        self.var.set('not-specific')

        # Region radiobuttons

        self.b_dict = {'not-specific': 0, 'movement': 0, 'social': 0, 'non-social': 0, 'grooming': 0, 'rearing': 0}

        for key in self.b_dict:
            self.b_dict[key] = Radiobutton(annotation_frame, text=key, bd=4, width=12, command=self.print_var)
            self.b_dict[key].config(indicatoron=0, variable=self.var, value=key)
            self.b_dict[key].pack(side='left')

        # endregion

        # TOP WINDOW

        # Button that lets the user take annotate
        self.btn_annotate = Button(self.top, text="Annotate", width=50, command=self.annotate)
        self.btn_annotate.pack(anchor=CENTER, expand=True)

        self.btn_stop_annotate = Button(self.top, text="Stop Annotate", width=50, command=self.stop_annotate)
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




        self.delay = 15   # ms

        self.window.mainloop()

    def open_file(self):

        self.pause = False
        home = os.path.expanduser('~')
        self.filename = filedialog.askopenfilename(initialdir = home, title="Select file")
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

        # Set values on data
        self.data.ix[int(self.current_frame), 'behavior'] = self.current_behavior

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

            # stop
            if self.current_frame > self.total_frames:
                self.pause = True
                messagebox.showerror(title='End of video', message='End of video!')

            # update the slider
            self.frame_slider.set(self.current_frame)
            self.window.after(self.delay, self.play_video)


    # This function serves as a toggle for play/pause
    def play_pause_video(self):
        if self.pause == False:
            self.pause = True
            self.play_video()
        else:
            self.pause = False
            self.play_video()

    # We need to disable start so there are not a lot of instances
    def disable_start_button(self):
        self.btn_play.configure(state=DISABLED)

    # Release the video source when the object is destroyed
    def __del__(self):

        self.top.quit()

        if self.cap.isOpened():
            self.cap.release()

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
        self.ax = self.top_canvas.figure.axes[0]
        self.ax.set_xlim(x_min, x_max)
        # ax.set_ylim(y.min(), y.max())
        self.top_canvas.draw()

    def save_data(self):

        filename = filedialog.asksaveasfilename(title="Type filename to save",
                                                filetypes = (("csv files","*.csv"),("all files","*.*")))
        self.data.to_csv(filename, index=False)



##### End Class #####


print("Starting app...")

time.sleep(1)


# Create a window and pass it to videoGUI Class
videoGUI(Tk(), "Video player")