import cv2
import cvzone
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk


class SnapFilterApp:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.setup_cascade()
        self.load_filters()
        self.setup_gui()
        self.current_filter = None

    def setup_cascade(self):
        cascade_path = os.path.join(os.path.dirname(__file__), "haarcascade_frontalface_default.xml")
        if not os.path.exists(cascade_path):
            raise FileNotFoundError(f"Cascade file not found: {cascade_path}")
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def load_filters(self):
        self.filters = {}
        current_dir = os.path.dirname(os.path.abspath(__file__))
        filter_dir = os.path.join(current_dir, "filters")

        if not os.path.exists(filter_dir):
            os.makedirs(filter_dir)
            print(f"Created filters directory at: {filter_dir}")
            print("Please add PNG filter files to this directory")
            return

        filter_files = [f for f in os.listdir(filter_dir) if f.endswith('.png')]
        if not filter_files:
            print("No PNG files found in filters directory")
            return

        for file in filter_files:
            try:
                path = os.path.join(filter_dir, file)
                filter_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if filter_img is not None:
                    filter_name = os.path.splitext(file)[0]
                    self.filters[filter_name] = filter_img
                    print(f"Loaded filter: {filter_name}")
                else:
                    print(f"Failed to load filter: {file}")
            except Exception as e:
                print(f"Error loading {file}: {str(e)}")

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Snap Filter App")

        # Video frame
        self.video_frame = ttk.Label(self.root)
        self.video_frame.pack(padx=10, pady=10)

        # Filter selection
        filter_frame = ttk.LabelFrame(self.root, text="Select Filter")
        filter_frame.pack(fill="x", padx=10, pady=5)

        self.filter_var = tk.StringVar()
        filter_names = list(self.filters.keys())
        if filter_names:
            self.filter_var.set(filter_names[0])
            self.current_filter = self.filters[filter_names[0]]

        filter_dropdown = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=filter_names,
            state="readonly"
        )
        filter_dropdown.pack(padx=5, pady=5, fill="x")
        filter_dropdown.bind('<<ComboboxSelected>>', self.on_filter_change)

        # Buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="Take Photo", command=self.take_photo).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exit", command=self.cleanup).pack(side=tk.LEFT, padx=5)

    def on_filter_change(self, event=None):
        selected = self.filter_var.get()
        self.current_filter = self.filters.get(selected)

    def apply_filter(self, frame, face):
        if self.current_filter is None:
            return frame

        x, y, w, h = face
        try:
            filter_img = cv2.resize(self.current_filter, (w, h))
            frame = cvzone.overlayPNG(frame, filter_img, [x, y])
        except Exception as e:
            print(f"Error applying filter: {str(e)}")
        return frame

    def take_photo(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.dirname(__file__), "snapshots")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        filename = os.path.join(output_dir, f"snapshot_{timestamp}.jpg")

        if hasattr(self, 'current_frame'):
            cv2.imwrite(filename, self.current_frame)
            print(f"Saved photo as: {filename}")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            for face in faces:
                frame = self.apply_filter(frame, face)

            # Convert frame for tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)

            self.video_frame.configure(image=img_tk)
            self.video_frame.image = img_tk

        self.root.after(10, self.update_frame)

    def cleanup(self):
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

    def run(self):
        self.update_frame()
        self.root.mainloop()


if __name__ == "__main__":
    app = SnapFilterApp()
    app.run()
