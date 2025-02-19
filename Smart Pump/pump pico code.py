from machine import Pin, PWM, I2C
from time import sleep
import time
import uasyncio as asyncio
import network
import urequests
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# WiFi Credentials
SSID = "your_wifi_ssid"
PASSWORD = "your_wifi_password"

# Telegram Bot credentials
TELEGRAM_TOKEN = "your telegram bot token"
CHAT_ID = "your chat id"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# I2C LCD Setup
# I2C_ADDR = 0x27
# I2C_NUM_ROWS = 2
# I2C_NUM_COLS = 16
# i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
# lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Constants
PWM_FREQUENCY = 5000
EMPTY_DISTANCE = 16.0  # cm
FULL_DISTANCE = 6.0    # cm
STATUS_UPDATE_INTERVAL = 30  # Seconds
TELEGRAM_INSTRUCTION = "automatic"  # Default mode

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to WiFi...")

    while not wlan.isconnected():
        pass

    print("Connected!")
    print("IP Address:", wlan.ifconfig()[0])

connect_wifi()

def send_telegram_message(message):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = urequests.post(url, json=payload)
        response.close()
    except Exception as e:
        print("Failed to send Telegram message:", e)

class DistanceSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

    def measure_distance(self):
        self.trigger.low()
        sleep(0.000002)
        self.trigger.high()
        sleep(0.00001)
        self.trigger.low()

        start_time = time.ticks_us()
        while self.echo.value() == 0:
            start_time = time.ticks_us()

        stop_time = time.ticks_us()
        while self.echo.value() == 1:
            stop_time = time.ticks_us()

        duration = stop_time - start_time
        distance_cm = (duration * 0.0343) / 2
        return distance_cm

class MotorController:
    def __init__(self, in_pin, pwm_pin, pwm_freq):
        self.in_pin = Pin(in_pin, Pin.OUT)
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(pwm_freq)
        self.pwm.duty_u16(0)

    def start(self):
        self.in_pin.high()
        self.pwm.duty_u16(65535)
        send_telegram_message("Pump started.")

    def stop(self):
        self.in_pin.low()
        self.pwm.duty_u16(0)
        send_telegram_message("Pump stopped.")

class Buzzer:
    def __init__(self, pin):
        self.buzzer = Pin(pin, Pin.OUT)

    def beep(self, pattern):
        for _ in range(pattern):
            self.buzzer.high()
            sleep(0.1)
            self.buzzer.low()
            sleep(0.1)
        sleep(1)

class WaterTankController:
    def __init__(self, sensor, motor, buzzer):
        self.sensor = sensor
        self.motor = motor
        self.buzzer = buzzer
        self.pump_started = False
        self.last_water_level = -1  # To avoid unnecessary updates

    def calculate_percentage_filled(self, distance):
        if distance <= FULL_DISTANCE:
            return 100
        elif distance >= EMPTY_DISTANCE:
            return 0
        else:
            return 100 - ((distance - FULL_DISTANCE) / (EMPTY_DISTANCE - FULL_DISTANCE) * 100)

    async def send_status(self):
        while True:
            distance = self.sensor.measure_distance()
            percentage_filled = self.calculate_percentage_filled(distance)

            # Only update if water level has changed
            if percentage_filled != self.last_water_level:
                self.last_water_level = percentage_filled
                pump_status = "ON" if self.pump_started else "OFF"
                mode = TELEGRAM_INSTRUCTION

                update_message = f"Water Level: {percentage_filled}%\nPump Status: {pump_status}\nMode: {mode}"
                send_telegram_message(update_message)

                lcd.clear()
                lcd.putstr(f"Water: {percentage_filled}%\nPump: {pump_status}")

            await asyncio.sleep(STATUS_UPDATE_INTERVAL)

    async def run(self):
        asyncio.create_task(self.send_status())
        try:
            while True:
                distance = self.sensor.measure_distance()
                percentage_filled = self.calculate_percentage_filled(distance)

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

                await asyncio.sleep(1)

        finally:
            self.motor.stop()

async def check_telegram_updates():
    global TELEGRAM_INSTRUCTION
    last_update_id = 0

    while True:
        try:
            url = f"{TELEGRAM_API_URL}/getUpdates?offset={last_update_id + 1}"
            response = urequests.get(url)
            updates = response.json()
            response.close()

            for update in updates.get("result", []):
                last_update_id = update["update_id"]
                message_text = update["message"]["text"].strip().lower()

                if message_text == "/start_pump":
                    if TELEGRAM_INSTRUCTION == "remote" and not controller.pump_started:
                        controller.motor.start()
                        controller.pump_started = True
                        send_telegram_message("Pump started in remote mode.")

                elif message_text == "/stop_pump":
                    if controller.pump_started:
                        controller.motor.stop()
                        controller.pump_started = False
                        send_telegram_message("Pump stopped.")

                elif message_text == "/status":
                    distance = controller.sensor.measure_distance()
                    percentage_filled = controller.calculate_percentage_filled(distance)
                    pump_status = "ON" if controller.pump_started else "OFF"
                    mode = TELEGRAM_INSTRUCTION
                    send_telegram_message(f"Water Level: {percentage_filled}%\nPump Status: {pump_status}\nMode: {mode}")

                elif message_text.startswith("/mode"):
                    parts = message_text.split()
                    if len(parts) > 1 and parts[1] in ["automatic", "remote"]:
                        TELEGRAM_INSTRUCTION = parts[1]
                        send_telegram_message(f"Mode changed to {TELEGRAM_INSTRUCTION}.")
                    else:
                        send_telegram_message("Invalid mode. Use '/mode automatic' or '/mode remote'.")

                elif message_text == "/help":
                    send_telegram_message(
                        "Commands:\n"
                        "/mode automatic - Sensor-controlled mode.\n"
                        "/mode remote - Manual mode via Telegram.\n"
                        "/start_pump - Start the pump (Remote Mode only).\n"
                        "/stop_pump - Stop the pump.\n"
                        "/status - Get the current status.\n"
                        "/help - Show this help message."
                    )

        except Exception as e:
            print("Telegram API Error:", e)

        await asyncio.sleep(5)

sensor = DistanceSensor(trigger_pin=6, echo_pin=7)
motor = MotorController(in_pin=8, pwm_pin=9, pwm_freq=PWM_FREQUENCY)
buzzer = Buzzer(pin=10)
controller = WaterTankController(sensor, motor, buzzer)

asyncio.create_task(check_telegram_updates())
asyncio.run(controller.run())
