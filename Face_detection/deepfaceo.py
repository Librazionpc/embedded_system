from deepface import DeepFace
import cv2
import os
import telepot  # Use `python-telegram-bot` for Telegram bot functionality

# Initialize the Telegram bot
TOKEN = '6720585209:AAGXdL4KDE9LMrtXezpovTiFAYlDGWxyqmQ'
bot = telepot.Bot(TOKEN)

# Path to authorized faces directory
authorized_faces_dir = "authorized_faces"

def verify_face(input_image_path):
    for person_name in os.listdir(authorized_faces_dir):
        person_folder = os.path.join(authorized_faces_dir, person_name)
        
        for image_name in os.listdir(person_folder):
            person_image_path = os.path.join(person_folder, image_name)
            try:
                result = DeepFace.verify(img1_path=input_image_path, img2_path=person_image_path, enforce_detection=True, distance_metric='cosine', model_name='Facenet', threshold=0.3)

                print(f"Comparing with {person_name}: {result}")
                
                if result["verified"]:
                    print(f"Access granted: {person_name}")
                    return True
            except Exception as e:
                print(f"Error during verification: {e}")
     
    print("Access denied")
    return False

def capture_face():
    cap = cv2.VideoCapture(0)  # 0 is typically the default camera
    
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame from camera.")
        cap.release()
        return None

    input_image_path = "captured_face.jpg"
    cv2.imwrite(input_image_path, frame)
    cap.release()

    if not os.path.exists(input_image_path) or os.path.getsize(input_image_path) == 0:
        print("Error: Captured image was not saved correctly.")
        return None

    return input_image_path

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
while True:
    pass
