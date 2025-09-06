from flask import Flask, request, render_template
import os
import torch
import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1
from datetime import datetime
import csv

# Initialize Flask app
app = Flask(__name__, static_url_path='/uploads', static_folder=os.path.join(os.getcwd(), 'uploads'))

# Directories for known faces and uploads
KNOWN_FACES_DIR = "known"
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Set device to CPU
device = torch.device("cpu")
mtcnn = MTCNN(keep_all=True).to(device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Function to get face embedding
def get_embedding(img_path):
    print(f"Attempting to load image from: {img_path}")  # Debug print
    img = cv2.imread(img_path)

    if img is None:
        print(f"Error: Could not load image from {img_path}.")
        return None  # Return None if the image cannot be loaded

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (160, 160))  # Resize to expected input size
    face = mtcnn(img)  # Detect face
    if face is not None:
        emb = resnet(face.unsqueeze(0).to(device))
        return emb.detach().numpy()
    return None

# Load known faces
known_faces = {}
for filename in os.listdir(KNOWN_FACES_DIR):
    path = os.path.join(KNOWN_FACES_DIR, filename)
    known_faces[filename] = get_embedding(path)

# Log access attempts to a CSV file
def log_access(attempt_status, filepath, person_name=None):
    filename = 'access_log.csv'
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ['Date', 'Time', 'Status', 'Name', 'ImagePath']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if file is empty
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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    image_data = request.data
    if not image_data:
        return "No data provided", 400
    now = datetime.now()
    filepath = os.path.join(UPLOAD_DIR, f"{now.strftime('%d%m%Y%H%M%S')}.jpg")
    with open(filepath, 'wb') as img_file:
        img_file.write(image_data)

    unknown_face_emb = get_embedding(filepath)
    if unknown_face_emb is not None:  # Check if face embedding is not None
        for name, known_emb in known_faces.items():
            if known_emb is not None:  # Check if known embedding is not None
                dist = torch.nn.functional.cosine_similarity(torch.tensor(known_emb), torch.tensor(unknown_face_emb))
                if dist > 0.8:  # You can adjust this threshold
                    print(name)
                    log_access("unlock", filepath, name)
                    return "unlock", 222

    log_access("lock", filepath)
    return "lock", 233

@app.route('/accessLog', methods=['GET'])
def accessLog():
    entries = []
    with open('access_log.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            entries.append(row)

    return render_template('log_template.html', entries=entries)

@app.route('/enroll', methods=['GET', 'POST'])
def enroll_face():
    if request.method == 'GET':
        return render_template('enroll.html')

    if request.method == 'POST': 
        name = request.form.get('name')
        images = request.files.getlist('images')
        
        for idx, image in enumerate(images):
            filename = f"{name}{idx}.jpg"
            filepath = os.path.join(KNOWN_FACES_DIR, filename)
            image.save(filepath)
            # Save embeddings for newly enrolled faces
            known_faces[filename] = get_embedding(filepath)

        return render_template('home.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Change to "0.0.0.0" to make it accessible on your network
