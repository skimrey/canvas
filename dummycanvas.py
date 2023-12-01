import tkinter as tk
from tkinter import Canvas, Button, Frame, colorchooser, filedialog
from PIL import Image, ImageGrab
import mido
import math

class CanvasDrawingApp:
    def __init__(self, root, midi_device_name=None):
        self.root = root
        self.root.title("Canvas Drawing App")

        # Set up the canvas
        self.canvas = Canvas(root, width=800, height=600, borderwidth=1, relief="solid")
        self.canvas.pack()

        # Set up MIDI input
        self.midi_input = self.setup_midi(midi_device_name)

        # Initialize line width and color
        self.line_width = 5  # Adjust the default line width as needed
        self.color = "black"

        # Store the segments with their corresponding widths
        self.segments = []

        # Set up clear button
        clear_button = Button(root, text="Clear", command=self.clear_canvas)
        clear_button.pack()

        # Set up save button
        save_button = Button(root, text="Save", command=self.save_canvas)
        save_button.pack()

        # Set up color palette
        color_palette_frame = Frame(root)
        color_palette_frame.pack()

        colors = ["black", "red", "green", "blue", "yellow", "orange", "purple"]
        for color in colors:
            color_button = Button(color_palette_frame, bg=color, width=2, command=lambda c=color: self.set_color(c))
            color_button.pack(side="left", padx=5)

        # Initialize drawing variables
        self.drawing = False
        self.last_x = 0
        self.last_y = 0

    def setup_midi(self, midi_device_name=None):
        try:
            if midi_device_name:
                return mido.open_input(midi_device_name, callback=self.handle_midi_input)
            else:
                return mido.open_input(callback=self.handle_midi_input)
        except IOError:
            print("No MIDI input found. Line width will not be controlled by MIDI.")

    def handle_midi_input(self, message):
        if message.type == 'aftertouch' and message.channel == 4:
            # Map controller values to line width range (adjust as needed)
            self.line_width = max(1, min(30, message.value / 127 * 30))

    def clear_canvas(self):
        self.canvas.delete("all")
        self.segments = []  # Clear stored segments

    def save_canvas(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            # Capture the content of the canvas using ImageGrab
            x = self.root.winfo_rootx() + self.canvas.winfo_x()
            y = self.root.winfo_rooty() + self.canvas.winfo_y()
            x1 = x + self.canvas.winfo_width()
            y1 = y + self.canvas.winfo_height()

            # Increase the size for antialiasing
            antialias_factor = 2  # Adjust the factor as needed
            capture_width = antialias_factor * self.canvas.winfo_width()
            capture_height = antialias_factor * self.canvas.winfo_height()

            image = ImageGrab.grab(bbox=(x, y, x1, y1))
            image = image.resize((capture_width, capture_height))

            # Resize back to the original size
            image = image.resize((self.canvas.winfo_width(), self.canvas.winfo_height()))

            image.save(file_path)

    def set_color(self, color):
        self.color = color

    def start_drawing(self, event):
        self.drawing = True
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event):
        if self.drawing:
            x, y = event.x, event.y
            # Calculate control points for a Bézier curve
            cx1 = self.last_x + (x - self.last_x) / 3
            cy1 = self.last_y + (y - self.last_y) / 3
            cx2 = x - (x - self.last_x) / 3
            cy2 = y - (y - self.last_y) / 3

            # Draw the Bézier curve
            self.canvas.create_line(
                self.last_x, self.last_y, cx1, cy1, cx2, cy2, x, y,
                width=self.line_width, fill=self.color, capstyle=tk.ROUND, smooth=tk.TRUE, splinesteps=36
            )

            # Update the last coordinates
            self.last_x = x
            self.last_y = y

    def stop_drawing(self, event):
        self.drawing = False

if __name__ == "__main__":
    # Replace 'Your MIDI Device Name' with the name of your MIDI input device
    midi_device_name = 'MIDI Expression RED 3'

    root = tk.Tk()
    app = CanvasDrawingApp(root, midi_device_name)

    app.canvas.bind("<Button-1>", app.start_drawing)
    app.canvas.bind("<B1-Motion>", app.draw)
    app.canvas.bind("<ButtonRelease-1>", app.stop_drawing)

    root.mainloop()
