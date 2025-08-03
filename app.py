from flask import Flask, render_template, Response, request, redirect, url_for
from camera import Camera
import os
import datetime
import platform
import RPI.GPIO as GPIO

app = Flask(__name__)
camera = Camera()
latest_filename = None
RELAY_PIN = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)

@app.route('/')
def welcome():
    # camera.release()
    return render_template('index.html')

@app.route('/booth')
def booth():
    return render_template('booth.html')

@app.route('/result')
def result():
    global latest_filename
    if latest_filename:
        return render_template('result.html', filename=latest_filename)
    return redirect(url_for('booth'))

@app.route('/stream')
def stream():
    def generate():
        while True:
            frame = camera.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/photo', methods=['POST'])
def photo():
    global latest_filename
    frame = camera.get_frame()
    if frame:
        filename = datetime.datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
        path = f"static/photos/{filename}"
        os.makedirs("static/photos", exist_ok=True)
        with open(path, "wb") as f:
            f.write(frame)
        latest_filename = filename
        return {'status': 'ok', 'filename': filename}
    return {'status': 'error'}

@app.route('/print', methods=['POST'])
def print_photo():
    filename = request.form.get('filename')
    if filename:
        full_path = f"static/photos/{filename}"
        if platform.system() == 'Windows':
            full_path = os.path.abspath(f"static/photos/{filename}")
            os.startfile(full_path)
        else:
            os.system(f"lp -o media=Custom.100x150mm {full_path}")
        return render_template('print.html')
    return render_template('index.html')

@app.route('/relay/on', methods=['POST'])
def relay_on():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    return {'status': 'on'}

@app.route('/relay/off', methods=['POST'])
def relay_off():
    GPIO.output(RELAY_PIN, GPIO.LOW)
    return {'status': 'off'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
