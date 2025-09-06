import requests
import cv2
SERVER_URL = r"http://127.0.0.1:5000/upload" # Adjust if your server has a different address or port
# IMAGE_PATH = r"D:\IOT\FaceUnlockSystem\uploads\temp.jpg"        # Replace with the path to your local test image
IMAGE_PATH = r"C:\Users\NAVEEN\Pictures\Camera Roll\abc.jpg"
def send_image_to_server(image_path, server_url):
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        response = requests.post(server_url, data=image_data)

    if response.status_code == 222:
        print("unlock with status code:", response.status_code)
    elif response.status_code == 232:
        print("locked with status code:", response.status_code)
    else:
        print("error occured:",response.status_code)
if __name__ == '__main__':
    send_image_to_server(IMAGE_PATH, SERVER_URL)
