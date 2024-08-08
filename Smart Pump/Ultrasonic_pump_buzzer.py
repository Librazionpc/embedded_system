from machine import Pin, PWM, time_pulse_us, I2C
import utime
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# Constants
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
PWM_FREQUENCY = 5000
EMPTY_DISTANCE = 16.0  # Distance when the tank is empty in cm
FULL_DISTANCE = 6.0    # Distance when the tank is full (100%) in cm

class DistanceSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger = Pin(trigger_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

    def measure_distance(self):
        self.trigger.low()
        utime.sleep_us(2)
        self.trigger.high()
        utime.sleep_us(10)
        self.trigger.low()
        duration = time_pulse_us(self.echo, 1, 1000000)
        distance_cm = (duration / 2) / 29.1
        return distance_cm

class MotorController:
    def __init__(self, in_pin, pwm_pin, pwm_freq):
        self.in_pin = Pin(in_pin, Pin.OUT)
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(pwm_freq)

    def start(self):
        self.in_pin.high()
        self.pwm.duty_u16(65535)  # Full speed

    def stop(self):
        self.in_pin.low()
        self.pwm.duty_u16(0)

class Buzzer:
    def __init__(self, pin):
        self.buzzer = Pin(pin, Pin.OUT)

    def beep(self, pattern):
        for _ in range(pattern):
            self.buzzer.high()
            utime.sleep(0.1)
            self.buzzer.low()
            utime.sleep(0.1)
        utime.sleep(1)

class LcdDisplay:
    def __init__(self, i2c_addr, num_rows, num_cols, sda_pin, scl_pin, freq):
        self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)
        self.lcd = I2cLcd(self.i2c, i2c_addr, num_rows, num_cols)

    def display_message(self, message):
        self.lcd.clear()
        self.lcd.putstr(message)

class WaterTankController:
    def __init__(self, sensor, motor, buzzer, lcd):
        self.sensor = sensor
        self.motor = motor
        self.buzzer = buzzer
        self.lcd = lcd
        self.pump_started = False
        self.last_beep_time = utime.time()
        self.last_percentage_filled = None

    def calculate_percentage_filled(self, distance):
        if distance <= FULL_DISTANCE:
            return 100
        elif distance >= EMPTY_DISTANCE:
            return 0
        else:
            return 100 - ((distance - FULL_DISTANCE) / (EMPTY_DISTANCE - FULL_DISTANCE) * 100)

    def run(self):
        try:
            while True:
                distance = self.sensor.measure_distance()
                print("Distance:", distance, "cm")
                percentage_filled = self.calculate_percentage_filled(distance)
                print("Water Level:", percentage_filled, "%")
                
                if percentage_filled != self.last_percentage_filled:
                    level_str = "Level: {:3d}%".format(int(percentage_filled))
                    self.lcd.display_message(level_str)
                    self.last_percentage_filled = percentage_filled
                
                if not self.pump_started and percentage_filled == 0:
                    self.motor.start()
                    self.pump_started = True
                    self.buzzer.beep(1)  # Beep once when the pump starts
                    self.lcd.display_message("Pump Starting...")
                
                if self.pump_started and percentage_filled >= 100:
                    self.motor.stop()
                    self.pump_started = False
                    self.buzzer.beep(5)  # Beep rapidly when the tank is full
                    self.lcd.display_message("Pump Stopping...")

                current_time = utime.time()
                if not self.pump_started:
                    if percentage_filled == 0 and current_time - self.last_beep_time >= 60:
                        self.buzzer.beep(10)  # Fast beep when the pump is not working and water level is at 0%
                        self.last_beep_time = current_time
                    elif 50 <= percentage_filled < 75 and current_time - self.last_beep_time >= 30:
                        self.buzzer.beep(2)  # Beep twice when water level is 50-75%
                        self.last_beep_time = current_time
                    elif 25 <= percentage_filled < 50 and current_time - self.last_beep_time >= 15:
                        self.buzzer.beep(3)  # Beep three times when water level is 25-50%
                        self.last_beep_time = current_time
                    elif 75 <= percentage_filled < 100 and current_time - self.last_beep_time >= 10:
                        self.buzzer.beep(5)  # Fast beep when the tank is almost full (75-100%)
                        self.last_beep_time = current_time
                
                utime.sleep(1)

        finally:
            self.motor.stop()

# Create instances of each class
sensor = DistanceSensor(trigger_pin=2, echo_pin=3)
motor = MotorController(in_pin=6, pwm_pin=7, pwm_freq=PWM_FREQUENCY)
buzzer = Buzzer(pin=8)
lcd = LcdDisplay(i2c_addr=I2C_ADDR, num_rows=I2C_NUM_ROWS, num_cols=I2C_NUM_COLS, sda_pin=4, scl_pin=5, freq=400000)
controller = WaterTankController(sensor, motor, buzzer, lcd)

# Run the controller
controller.run()
