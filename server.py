from flask import Flask, request, jsonify,render_template
import face_recognition
import os
import csv
from datetime import datetime,date



app = Flask(__name__)
KNOWN_FACES_DIR = "known"
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.route('/upload', methods=['POST'])
def upload_file():
    image_data = request.data
    print (request.data)
    if not image_data:
        return "No data provided", 400
    
    
    now = datetime.now()

    filepath = os.path.join(UPLOAD_DIR, f"{now.strftime('%d%m%Y%H%M%S')}.jpg")
    with open(filepath, 'wb') as img_file:
        img_file.write(image_data)

    if recognize_face(filepath):
        # Save image to known faces (optional)
        #saved_path = os.path.join(KNOWN_FACES_DIR, "new_face.jpg")
        log_access("unlock",filepath)
        return "unlock" ,200
    else:
       log_access("lock",filepath)
       return "lock" ,200

@app.route('/enroll', methods=['POST'])
def enroll_face():
    print(request.headers)
    name = request.headers.get('name')
    # Here we are taking just one sample per request for simplicity, as indicated in the ESP32 code
    samples = 1 
    
    if not name:
        return "Name is required", 400

    image_data = request.data
    if not image_data:
        return "No data provided", 400

    filename = request.headers.get('filename', f"{name}.jpg")  # default to name.jpg if no filename header
    filepath = os.path.join(KNOWN_FACES_DIR, filename)
        
    with open(filepath, 'wb') as img_file:
        img_file.write(image_data)
        log_access("enrolled",filepath, name)


    return f"Enrolled sample for {name}", 200

@app.route('/access-log', methods=['GET'])
def access_log():
    entries = []
    with open('access_log.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            entries.append(row)

    return render_template('log_template.html', entries=entries)


def log_access(attempt_status, filepath, person_name=None):
    """Log access attempts to a CSV file."""
    filename = 'access_log.csv'
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Date', 'Time', 'Status', 'Name', 'ImagePath']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if os.stat(filename).st_size == 0:
            writer.writeheader()

        current_time = datetime.now()
        writer.writerow({
            'Date': current_time.strftime('%d/%m/%Y'),
            'Time': current_time.strftime('%H:%M:%S'),
            'Status': attempt_status,
            'Name': person_name if person_name else 'Unknown',
            'ImagePath': filepath
        })



def recognize_face(filepath):
    # Load the image we've received
    unknown_image = face_recognition.load_image_file(filepath)
    unknown_face_encodings = face_recognition.face_encodings(unknown_image)
    
    if len(unknown_face_encodings) == 0:
        # No faces found
        return False
    
    # For simplicity, only considering the first face found
    unknown_face = unknown_face_encodings[0]
    
    # Compare the face with all known faces
    for filename in os.listdir(KNOWN_FACES_DIR):
        known_image = face_recognition.load_image_file(os.path.join(KNOWN_FACES_DIR, filename))
        known_face_encodings = face_recognition.face_encodings(known_image)
        if len(unknown_face_encodings) == 0:
            print("No faces found in uploaded image!")
            return False

        # Check if there's a match
        results = face_recognition.compare_faces(known_face_encodings, unknown_face)
        if True in results:
            return True
    return False

if __name__ == "__main__":
    app.run(host="192.168.79.97", port=5000)
