import os
import signal
from deepface import DeepFace
import cv2
import telepot
from picamera2 import Picamera2

# Initialize the Telegram bot
TOKEN = '6991600551:AAHbELDM9OPCSnSguSKpHIN4bIMd4rWWwA0'
bot = telepot.Bot(TOKEN)

# Send a startup message to notify that the bot is running
STARTUP_CHAT_ID = '6340126645'  # Replace with your chat ID
bot.sendMessage(STARTUP_CHAT_ID, "Face recognition bot is starting...")

# Path to authorized faces directory
authorized_faces_dir = "authorized_faces"

def kill_camera_processes():
    """
    Kill any processes that might be using the camera (e.g., libcamera or other scripts).
    """
    try:
        # Find processes that may use the camera
        processes = os.popen("ps aux | grep 'libcamera\|python' | grep -v grep").readlines()
        for process in processes:
            cols = process.split()
            pid = int(cols[1])  # Process ID is in the second column
            os.kill(pid, signal.SIGTERM)  # Terminate the process
            print(f"Terminated process: {cols[-1]} (PID: {pid})")
    except Exception as e:
        print(f"Error while killing camera processes: {e}")

# Call this function at the start of the program
kill_camera_processes()

def verify_face(input_image_path):
    for person_name in os.listdir(authorized_faces_dir):
        person_folder = os.path.join(authorized_faces_dir, person_name)
        
        for image_name in os.listdir(person_folder):
            person_image_path = os.path.join(person_folder, image_name)
            try:
                result = DeepFace.verify(
                    img1_path=input_image_path, 
                    img2_path=person_image_path, 
                    enforce_detection=True, 
                    distance_metric='cosine', 
                    model_name='Facenet', 
                    threshold=0.3
                )

                print(f"Comparing with {person_name}: {result}")
                
                if result["verified"]:
                    print(f"Access granted: {person_name}")
                    return True
            except Exception as e:
                print(f"Error during verification: {e}")
     
    print("Access denied")
    return False

def capture_face():
    try:
        picam = Picamera2()
        picam.start()  # Start the camera
        frame = picam.capture_array()  # Capture an image
        
        if frame is None:
            print("Error: Could not read frame from camera.")
            return None

        input_image_path = "captured_face.jpg"
        cv2.imwrite(input_image_path, frame)  # Save the image to a file
        picam.stop()  # Stop the camera
        picam.close()  # Release the camera resource

        if not os.path.exists(input_image_path) or os.path.getsize(input_image_path) == 0:
            print("Error: Captured image was not saved correctly.")
            return None

        return input_image_path
    except Exception as e:
        print(f"Error accessing the camera: {e}")
        return None

def handle_bot_message(msg):
    chat_id = msg['chat']['id']
    command = msg['text']

    if command == '/capture':
        # Start face capture
        image_path = capture_face()
        
        if image_path:
            # Verify face and update dataset
            access_granted = verify_face(image_path)
            
            if access_granted:
                bot.sendMessage(chat_id, "Access Granted")
                # Trigger door lock mechanism here
            else:
                bot.sendMessage(chat_id, "Access Denied")
                
            # Optionally send the captured image to the bot
            bot.sendPhoto(chat_id, photo=open(image_path, 'rb'))
        else:
            bot.sendMessage(chat_id, "Error capturing image")

    elif command.startswith('/addface'):
        _, person_name = command.split(maxsplit=1)
        if not person_name:
            bot.sendMessage(chat_id, "Please provide a name for the new face.")
            return
        
        # Capture and add new face to dataset
        image_path = capture_face()
        
        if image_path:
            person_folder = os.path.join(authorized_faces_dir, person_name)
            if not os.path.exists(person_folder):
                os.makedirs(person_folder)
            
            # Save new face image
            new_image_path = os.path.join(person_folder, os.path.basename(image_path))
            os.rename(image_path, new_image_path)
            
            bot.sendMessage(chat_id, f"New face added for {person_name}.")
        else:
            bot.sendMessage(chat_id, "Error capturing image")

bot.message_loop(handle_bot_message)

print("Bot is listening...")
bot.sendMessage(STARTUP_CHAT_ID, "Bot is ready and listening for commands!")  # Send confirmation message on startup
while True:
    pass
