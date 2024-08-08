from machine import Pin, PWM, time_pulse_us
import utime

# Define pins for distance measurement
trigger = Pin(2, Pin.OUT)  # TRIG pin
echo = Pin(3, Pin.IN)      # ECHO pin

# Define pins for Motor B
IN3 = Pin(6, Pin.OUT)  # Motor B Direction Pin 1
ENB = PWM(Pin(7))      # Motor B Speed Control

# Define pin for buzzer
buzzer = Pin(8, Pin.OUT)

# Set PWM frequency (Hz)
PWM_FREQUENCY = 5000  # Adjusted frequency for smoother control
ENB.freq(PWM_FREQUENCY)

# Define tank parameters
empty_distance = 16.0  # Distance when the tank is empty in cm
full_distance = 6.0    # Distance when the tank is full (100%) in cm

def measure_distance():
    # Ensure the trigger pin is low
    trigger.low()
    utime.sleep_us(2)
    
    # Create a 10 microsecond pulse on the trigger pin
    trigger.high()
    utime.sleep_us(10)
    trigger.low()
    
    # Measure the time for the echo to return
    duration = time_pulse_us(echo, 1, 1000000)
    
    # Calculate distance in cm
    distance_cm = (duration / 2) / 29.1
    
    return distance_cm

def set_motor_speed(speed):
    # Set the PWM duty cycle to control the motor speed
    ENB.duty_u16(speed)

def start_pump():
    IN3.high()

def stop_pump():
    IN3.low()
    set_motor_speed(0)

def beep_buzzer(pattern):
    for _ in range(pattern):
        buzzer.high()
        utime.sleep(0.1)
        buzzer.low()
        utime.sleep(0.1)
    utime.sleep(1)  # Pause between patterns

pump_started = False  # Track if the pump has been started
last_beep_time = utime.time()  # Track last beep time

try:
    while True:
        distance = measure_distance()
        print("Distance:", distance, "cm")
        
        # Calculate the percentage filled
        if distance <= full_distance:
            percentage_filled = 100
        elif distance >= empty_distance:
            percentage_filled = 0
        else:
            # Linear interpolation for percentage between full and empty distances
            percentage_filled = 100 - ((distance - full_distance) / (empty_distance - full_distance) * 100)
        
        # Print the percentage filled
        print("Water Level:", percentage_filled, "%")
        
        # Start the pump once if it hasn't been started
        if not pump_started and percentage_filled == 0:
            start_pump()
            set_motor_speed(65535)  # Full speed
            pump_started = True
            beep_buzzer(1)  # Beep once when the pump starts

        # Reduce speed or stop pump as necessary
        if pump_started:
            if percentage_filled >= 100:
                stop_pump()
                pump_started = False  # Reset to allow pump to start again if needed
                beep_buzzer(5)  # Beep rapidly when the tank is full
            else:
                # Gradually reduce speed as the tank fills
                speed = int(((100 - percentage_filled) / 100) * 65535)
                set_motor_speed(speed)
        
        # Beep patterns based on water level and pump status
        current_time = utime.time()
        if not pump_started:
            if percentage_filled == 0 and current_time - last_beep_time >= 60:
                beep_buzzer(10)  # Fast beep when the pump is not working and water level is at 0%
                last_beep_time = current_time
            elif percentage_filled >= 50 and percentage_filled < 75 and current_time - last_beep_time >= 30:
                beep_buzzer(2)  # Beep twice when water level is 50-75%
                last_beep_time = current_time
            elif percentage_filled >= 25 and percentage_filled < 50 and current_time - last_beep_time >= 15:
                beep_buzzer(3)  # Beep three times when water level is 25-50%
                last_beep_time = current_time
            elif percentage_filled >= 75 and percentage_filled < 100 and current_time - last_beep_time >= 10:
                beep_buzzer(5)  # Fast beep when the tank is almost full (75-100%)
                last_beep_time = current_time
        
        utime.sleep(1)

finally:
    # Clean up
    stop_pump()
