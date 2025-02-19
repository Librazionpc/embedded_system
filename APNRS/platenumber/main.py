import time
import logging
import RPi.GPIO as GPIO
from models.engine.database import db_manager
from models.admin import Admin
from hardware import image_to_ocr
from os import path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize database and admin
DB_PATH = "smart_plate_number.db"
if not path.isfile(DB_PATH):
    logger.error("Database does not exist")
    exit(1)
else:
    logger.info("Connecting to the database")

db_manager = db_manager.DatabaseManager(DB_PATH)
admin = Admin(db_manager)
plate_number_recognition = image_to_ocr.PlateNumber()

# Setup GPIO pins for distance sensor and servo motor
TRIGGER_PIN = 23
ECHO_PIN = 24
SERVO_PIN = 18

def initialize_gpio():
    """Initialize GPIO pins."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIGGER_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    
    # Set up PWM for the servo motor
    global pwm_servo
    pwm_servo = GPIO.PWM(SERVO_PIN, 50)  # 50 Hz PWM frequency
    pwm_servo.start(0)  # Initialize servo position at 0 degrees

def set_servo_angle(angle):
    """Set the servo motor to the specified angle."""
    duty_cycle = (angle / 18) + 2
    pwm_servo.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
    pwm_servo.ChangeDutyCycle(0)  # Stop the PWM signal

def get_distance():
    """Measure the distance using the ultrasonic sensor."""
    GPIO.output(TRIGGER_PIN, False)
    time.sleep(0.5)
    
    GPIO.output(TRIGGER_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIGGER_PIN, False)
    
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
    
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2
    
    return distance

class ANCPRManager:
    def __init__(self):
        self.logged_in = False

    def verify_password(self):
        """Prompt for admin username and password and verify it."""
        username = input("Enter admin username: ").strip()
        password = input("Enter admin password: ").strip()
        if admin.verify_admin(username, password):
            self.logged_in = True
            logger.info("Login successful.")
            return True
        else:
            logger.warning("Incorrect username or password.")
            return False

    def login(self):
        """Login as admin."""
        for attempt in range(1, 4):
            logger.info(f"Attempt {attempt}/3")
            if self.verify_password():
                return True
        logger.error("Maximum login attempts reached.")
        return False

    def admin_registration(self):
        if self.logged_in:
            firstname = input("Enter Your firstname: ").strip().lower()
            lastname = input("Enter Your lastname: ").strip().lower()
            password = input("Enter Your password: ").strip().lower()
            fullname = f"{lastname} {firstname}"
            admin.add_admin(fullname, password)
            logger.info("Admin registered successfully.")
        else:
            logger.warning("Please log in first.")

    def add_user(self):
        if self.logged_in:
            choice = input("Add user manually or by OCR? (manual/ocr): ").strip().lower()
            if choice == 'manual':
                name = input("Enter the user's name: ").strip()
                plate_number = input("Enter the user's plate number: ").strip()
                if not admin.add_user(name, plate_number):
                    print(f"Failed to add user {name}")
            elif choice == 'ocr':
                detected_plate_number = plate_number_recognition.run()
                if detected_plate_number:
                    logger.info(f"Detected Plate Number: {detected_plate_number}")
                    name = input("Enter the user's name: ").strip()
                    if not admin.add_user(name, plate_number):
                        print(f"Failed to add user {name}")
                else:
                    logger.warning("Failed to detect plate number.")
            else:
                logger.warning("Invalid choice. Please select 'manual' or 'ocr'.")
        else:
            logger.warning("Please log in first.")

    def update_user(self):
        if self.logged_in:
            plate_number = input("Enter the plate number of the user to update: ").strip()
            new_plate_number = input("Enter new plate number (or leave blank to keep current): ").strip()
            new_name = input("Enter new name (or leave blank to keep current): ").strip()
            admin.update_user(plate_number, new_plate_number or None, new_name or None)
            logger.info("User updated successfully.")
        else:
            logger.warning("Please log in first.")

    def view_users(self, user):
        if self.logged_in:
            if user == 'cam':
                detected_plate_number = plate_number_recognition.run()
                if detected_plate_number:
                    logger.info(f"Detected Plate Number: {detected_plate_number}")
                    if not admin.view_users(user, value=detected_plate_number):
                        return False
                    return True
                else:
                    logger.warning('Detection failed. Please try again.')
                    return False
            else:
                if not admin.view_users(user):
                    if input("Do you want to add the new user? Yes or No: ").strip().lower() == "yes":
                        self.add_user()
        else:
            logger.warning("Please log in first.")

    def delete_user(self):
        if self.logged_in:
            plate_number = input("Enter the plate number of the user to delete: ").strip()
            admin.delete_user(plate_number)
            logger.info(f"User with plate number {plate_number} has been deleted successfully.")
        else:
            logger.warning("Please log in first.")

if __name__ == "__main__":
    initialize_gpio()
    servo_set_time = None  # Time when servo was last set to 90 degrees
    try:
        manager = ANCPRManager()
        if manager.login():
            while True:
                distance = get_distance()
                print(distance)
                logger.info(f"Measured Distance: {distance} cm")

                current_time = time.time()
                if distance <= 50:
                    manager.view_users('cam')
                    if not servo_set_time:
                        # Set the servo to 90 degrees and record the time
                        set_servo_angle(90)
                        servo_set_time = current_time

                if servo_set_time and current_time - servo_set_time >= 20:
                    # Return the servo to 0 degrees after 20 seconds
                    set_servo_angle(0)
                    servo_set_time = None  # Reset the timer
                time.sleep(1)
        else:
            logger.error("Login failed. Exiting.")
    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        pwm_servo.stop()  # Stop the PWM signal
        GPIO.cleanup()
