import RPi.GPIO as GPIO
import time
import telebot
import threading

# Initialize GPIO mode
GPIO.setmode(GPIO.BCM)

# Telegram Bot credentials
TELEGRAM_TOKEN = "7275308334:AAE4WrYTHL0VBWmryH8AJgX4z9On2bEeUlQ"
CHAT_ID = "6794210152"
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Constants
PWM_FREQUENCY = 5000
EMPTY_DISTANCE = 16.0  # Distance when the tank is empty in cm
FULL_DISTANCE = 6.0    # Distance when the tank is full (100%) in cm
STATUS_UPDATE_INTERVAL = 30  # Time interval for sending status updates (in seconds)
TELEGRAM_INSTRUCTION = "automatic"  # Default mode is automatic

class DistanceSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger = trigger_pin
        self.echo = echo_pin
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    def measure_distance(self):
        GPIO.output(self.trigger, GPIO.LOW)
        time.sleep(0.000002)
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)

        start_time = time.time()
        stop_time = time.time()

        while GPIO.input(self.echo) == GPIO.LOW:
            start_time = time.time()

        while GPIO.input(self.echo) == GPIO.HIGH:
            stop_time = time.time()

        duration = stop_time - start_time
        distance_cm = (duration * 34300) / 2
        return distance_cm

class MotorController:
    def __init__(self, in_pin, pwm_pin, pwm_freq):
        self.in_pin = in_pin
        self.pwm_pin = pwm_pin
        GPIO.setup(self.in_pin, GPIO.OUT)
        GPIO.setup(self.pwm_pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pwm_pin, pwm_freq)

    def start(self):
        GPIO.output(self.in_pin, GPIO.HIGH)
        self.pwm.start(100)
        bot.send_message(CHAT_ID, "Pump started.")

    def stop(self):
        GPIO.output(self.in_pin, GPIO.LOW)
        self.pwm.stop()
        bot.send_message(CHAT_ID, "Pump stopped.")

class Buzzer:
    def __init__(self, pin):
        self.buzzer = pin
        GPIO.setup(self.buzzer, GPIO.OUT)

    def beep(self, pattern):
        for _ in range(pattern):
            GPIO.output(self.buzzer, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.buzzer, GPIO.LOW)
            time.sleep(0.1)
        time.sleep(1)

class WaterTankController:
    def __init__(self, sensor, motor, buzzer):
        self.sensor = sensor
        self.motor = motor
        self.buzzer = buzzer
        self.pump_started = False
        self.last_percentage_filled = None

    def calculate_percentage_filled(self, distance):
        if distance <= FULL_DISTANCE:
            return 100
        elif distance >= EMPTY_DISTANCE:
            return 0
        else:
            return 100 - ((distance - FULL_DISTANCE) / (EMPTY_DISTANCE - FULL_DISTANCE) * 100)

    def send_status(self):
        while True:
            distance = self.sensor.measure_distance()
            percentage_filled = self.calculate_percentage_filled(distance)
            pump_status = "ON" if self.pump_started else "OFF"
            mode = TELEGRAM_INSTRUCTION

            update_message = f"Water Level: {percentage_filled}%\nPump Status: {pump_status}\nMode: {mode}"
            bot.send_message(CHAT_ID, update_message)

            time.sleep(STATUS_UPDATE_INTERVAL)

    def run(self):
        threading.Thread(target=self.send_status).start()
        try:
            while True:
                distance = self.sensor.measure_distance()
                percentage_filled = self.calculate_percentage_filled(distance)
                print("Distance:", distance, "cm")
                print("Water Level:", percentage_filled, "%")
                print("Mode:", TELEGRAM_INSTRUCTION)

                # Automatic Mode Logic
                if TELEGRAM_INSTRUCTION == "automatic":
                    if not self.pump_started and percentage_filled == 0:
                        self.motor.start()
                        self.pump_started = True
                        self.buzzer.beep(1)

                    if self.pump_started and percentage_filled >= 100:
                        self.motor.stop()
                        self.pump_started = False
                        self.buzzer.beep(5)

                time.sleep(1)

        finally:
            self.motor.stop()
            GPIO.cleanup()  # Clean up GPIO settings

# Telegram bot command handlers
@bot.message_handler(commands=['start_pump'])
def start_pump(message):
    if TELEGRAM_INSTRUCTION == "remote":
        if not controller.pump_started:
            controller.motor.start()
            controller.pump_started = True
            bot.reply_to(message, "Pump started in remote mode.")
        else:
            bot.reply_to(message, "Pump is already running.")
    else:
        bot.reply_to(message, "Cannot start pump in automatic mode.")

@bot.message_handler(commands=['stop_pump'])
def stop_pump(message):
    if controller.pump_started:
        controller.motor.stop()
        controller.pump_started = False
        bot.reply_to(message, "Pump stopped.")
    else:
        bot.reply_to(message, "Pump is already stopped.")

@bot.message_handler(commands=['status'])
def send_status(message):
    distance = controller.sensor.measure_distance()
    percentage_filled = controller.calculate_percentage_filled(distance)
    pump_status = "ON" if controller.pump_started else "OFF"
    mode = TELEGRAM_INSTRUCTION
    status_message = f"Water Level: {percentage_filled}%\nPump Status: {pump_status}\nMode: {mode}"
    bot.reply_to(message, status_message)

@bot.message_handler(commands=['mode'])
def change_mode(message):
    global TELEGRAM_INSTRUCTION
    mode = message.text.split()[1].lower()
    if mode in ["automatic", "remote"]:
        TELEGRAM_INSTRUCTION = mode
        bot.reply_to(message, f"Mode changed to {mode}.")
    else:
        bot.reply_to(message, "Invalid mode. Use '/mode automatic' or '/mode remote'.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = (
        "Here are the available commands:\n"
        "/mode automatic - Switch to Automatic Mode (sensor-controlled).\n"
        "/mode remote - Switch to Remote Mode (manual control via Telegram).\n"
        "/start_pump - Start the water pump (Remote Mode only).\n"
        "/stop_pump - Stop the water pump.\n"
        "/status - Get the current water level, pump status, and mode.\n"
        "/help - Show this help message."
    )
    bot.reply_to(message, help_message)

# Setup GPIO pins
GPIO.setmode(GPIO.BCM)

# Create instances of each class
sensor = DistanceSensor(trigger_pin=23, echo_pin=24)
motor = MotorController(in_pin=20, pwm_pin=21, pwm_freq=PWM_FREQUENCY)
buzzer = Buzzer(pin=4)
controller = WaterTankController(sensor, motor, buzzer)

# Send help message on startup
bot.send_message(CHAT_ID, "Water Pump Control Script Started. Use /help to see available commands.")

# Start the bot in a separate thread
threading.Thread(target=bot.infinity_polling).start()

# Run the water tank controller
controller.run()
