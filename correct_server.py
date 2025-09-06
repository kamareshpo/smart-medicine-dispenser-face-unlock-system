# from flask import Flask, request,render_template
# import os
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
# import torch
# import cv2
# from facenet_pytorch import MTCNN, InceptionResnetV1
# import torch
# from datetime import datetime,date
# import csv

# app = Flask(__name__ , static_url_path='/uploads', static_folder=os.path.join(os.getcwd(), 'uploads'))

# KNOWN_FACES_DIR = "known"
# UPLOAD_DIR = "uploads"

# if not os.path.exists(UPLOAD_DIR):
#     os.makedirs(UPLOAD_DIR)

# mtcnn = MTCNN()
# resnet = InceptionResnetV1(pretrained='vggface2').eval()

# def get_embedding(img_path):
#     img = cv2.imread(img_path)
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     face = mtcnn(img)
#     if face is not None:
#         emb = resnet(face.unsqueeze(0))
#         return emb.detach().numpy()
#     return None

# known_faces = {}
# for filename in os.listdir(KNOWN_FACES_DIR):
#     path = os.path.join(KNOWN_FACES_DIR, filename)
#     known_faces[filename] = get_embedding(path)

# 4

# def log_access(attempt_status, filepath, person_name=None):
#     """Log access attempts to a CSV file."""
#     filename = 'access_log.csv'
#     with open(filename, 'a', newline='') as csvfile:
#         fieldnames = ['Date', 'Time', 'Status', 'Name', 'ImagePath']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
#         if os.stat(filename).st_size == 0:
#             writer.writeheader()

#         current_time = datetime.now()
#         writer.writerow({
#             'Date': current_time.strftime('%d/%m/%Y'),
#             'Time': current_time.strftime('%H:%M:%S'),
#             'Status': attempt_status,
#             'Name': person_name if person_name else 'Unknown',
#             'ImagePath': filepath
#         })

# @app.route('/')
# def home():
#     return render_template('home.html')

# # @app.route('/upload', methods=['POST'])
# # def upload_file():
# #     image_data = request.data
# #     if not image_data:
# #         return "No data provided", 400
# #     now = datetime.now()
# #     filepath = os.path.join(UPLOAD_DIR, f"{now.strftime('%d%m%Y%H%M%S')}.jpg")
# #     with open(filepath, 'wb') as img_file:
# #         img_file.write(image_data)

# #     unknown_face_emb = get_embedding(filepath)
# #     if unknown_face_emb is not None:
# #         for name, known_emb in known_faces.items():
# #             dist = torch.nn.functional.cosine_similarity(torch.tensor(known_emb), torch.tensor(unknown_face_emb))
# #             if dist > 0.8:  # You can adjust this threshold
# #                 print(name)
# #                 log_access("unlock",filepath,name)
# #                 return "unlock",222

# #     log_access("lock",filepath)
# #     return "lock",233

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     image_data = request.data
#     if not image_data:
#         return "No data provided", 400
#     now = datetime.now()
#     filepath = os.path.join(UPLOAD_DIR, f"{now.strftime('%d%m%Y%H%M%S')}.jpg")
#     with open(filepath, 'wb') as img_file:
#         img_file.write(image_data)

#     unknown_face_emb = get_embedding(filepath)
#     if unknown_face_emb is not None:  # Check if face embedding is not None
#         for name, known_emb in known_faces.items():
#             if known_emb is not None:  # Check if known embedding is not None
#                 dist = torch.nn.functional.cosine_similarity(torch.tensor(known_emb), torch.tensor(unknown_face_emb))
#                 if dist > 0.8:  # You can adjust this threshold
#                     print(name)
#                     log_access("unlock", filepath, name)
#                     return "unlock", 222

#     log_access("lock", filepath)
#     return "lock", 233

# @app.route('/accessLog', methods=['GET'])
# def accessLog():
#     entries = []
#     with open('access_log.csv', 'r') as csvfile:
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             entries.append(row)

#     return render_template('log_template.html', entries=entries)

# @app.route('/enroll',methods=['GET', 'POST'])
# def enroll_face():
#     if request.method == 'GET':
#         return render_template('enroll.html')

#     if request.method == 'POST': 
#         name = request.form.get('name')
#         images = request.files.getlist('images')
        
#         for idx, image in enumerate(images):
#             filename = f"{name}{idx}.jpg"
#             filepath = os.path.join(KNOWN_FACES_DIR,filename)
#             image.save(filepath)

#         return render_template('home.html') 

# if __name__ == "__main__":
#     #app.run(host="192.168.79.97", port=5000)
#     app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, render_template
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import torch
import cv2
from facenet_pytorch import MTCNN, InceptionResnetV1


from datetime import datetime, date
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_url_path='/uploads', static_folder=os.path.join(os.getcwd(), 'uploads'))

# Email notification configuration
EMAIL_SENDER = "your-email@gmail.com"  # Your Gmail address
EMAIL_PASSWORD = "your-app-password"   # Your Gmail app password (not your regular password)
CARETAKER_EMAIL = "99220040953@klu.ac.in"  # Caretaker's email address

KNOWN_FACES_DIR = "known"
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

mtcnn = MTCNN()
resnet = InceptionResnetV1(pretrained='vggface2').eval()

def send_email_notification(subject, message):
    """Send email notification to caretaker"""
    try:
        # Create email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = CARETAKER_EMAIL
        msg['Subject'] = subject
        
        # Attach message
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        print(f"Email notification sent to {CARETAKER_EMAIL}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def get_embedding(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face = mtcnn(img)
    if face is not None:
        emb = resnet(face.unsqueeze(0))
        return emb.detach().numpy()
    return None

known_faces = {}
for filename in os.listdir(KNOWN_FACES_DIR):
    path = os.path.join(KNOWN_FACES_DIR, filename)
    known_faces[filename] = get_embedding(path)

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
                    
                    # Send success email notification
                    subject = "Medicine Dispenser Alert: Medicine Dispensed"
                    message = (f"Hello Caretaker,\n\n"
                              f"The medicine has been dispensed to {name} at {now.strftime('%I:%M %p')} on {now.strftime('%d/%m/%Y')}.\n\n"
                              f"This is an automated message from your Medicine Dispenser System.")
                    send_email_notification(subject, message)
                    
                    return "unlock", 222

    log_access("lock", filepath)
    
    # Send failed access email notification
    subject = "Medicine Dispenser Alert: Access Denied"
    message = (f"Hello Caretaker,\n\n"
              f"Someone attempted to access the medicine dispenser at {now.strftime('%I:%M %p')} on {now.strftime('%d/%m/%Y')} but was not recognized.\n\n"
              f"Please check the system and ensure the patient takes their medicine as prescribed.\n\n"
              f"This is an automated message from your Medicine Dispenser System.")
    send_email_notification(subject, message)
    
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
            
            # Update known_faces dictionary with the new face
            known_faces[filename] = get_embedding(filepath)
        
        # Send enrollment notification
        subject = "Medicine Dispenser Alert: New User Enrolled"
        message = (f"Hello Caretaker,\n\n"
                  f"A new user ({name}) has been enrolled in the medicine dispenser system at {datetime.now().strftime('%I:%M %p')} on {datetime.now().strftime('%d/%m/%Y')}.\n\n"
                  f"This is an automated message from your Medicine Dispenser System.")
        send_email_notification(subject, message)

        return render_template('home.html')

@app.route('/test_email', methods=['GET'])
def test_email():
    """Test endpoint for email notifications"""
    subject = "Medicine Dispenser Test Email"
    message = "This is a test email from your Medicine Dispenser System. If you received this, the email notification system is working correctly."
    success = send_email_notification(subject, message)
    
    if success:
        return "Test email sent successfully to " + CARETAKER_EMAIL
    else:
        return "Failed to send test email. Check server logs for details."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)