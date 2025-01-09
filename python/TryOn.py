from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import cvzone
import os
import base64

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize Video Capture
cap = cv2.VideoCapture(0)

# Haar cascade for upper body detection
upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_upperbody.xml")

# Shirt Overlay Settings
fixedRatio = 262 / 190
shirtRatioHeightWidth = 581 / 440
shirtFolderPath = os.path.abspath("Shirts")
listShirts = os.listdir(shirtFolderPath)
imageNumber = 0

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("request_frame")
def send_frame(data):
    global imageNumber
    success, img = cap.read()
    if not success:
        return

    # Detect upper body
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bodies = upper_body_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(bodies) > 0:
        x, y, w, h = bodies[0]  # Use the first detected body
        widthOfShirt = int(w * fixedRatio)

        if widthOfShirt > 0:
            shirtPath = os.path.join(shirtFolderPath, listShirts[imageNumber])
            imgShirt = cv2.imread(shirtPath, cv2.IMREAD_UNCHANGED)

            if imgShirt is not None:
                imgShirt = cv2.resize(imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth)))
                offset_x = x - int(w * 0.1)
                offset_y = y - int(h * 0.1)

                try:
                    img = cvzone.overlayPNG(img, imgShirt, (offset_x, offset_y))
                except Exception as e:
                    print(f"Error overlaying shirt: {e}")

    # Convert frame to Base64
    _, buffer = cv2.imencode(".jpg", img)
    frame_data = base64.b64encode(buffer).decode("utf-8")
    emit("frame", {"image": frame_data})

@socketio.on("change_shirt")
def change_shirt(data):
    global imageNumber
    if data["direction"] == "next" and imageNumber < len(listShirts) - 1:
        imageNumber += 1
    elif data["direction"] == "prev" and imageNumber > 0:
        imageNumber -= 1

if __name__ == "__main__":
    socketio.run(app, debug=True)
