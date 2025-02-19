from machine import Pin, PWM
from time import sleep
import machine
from machine import I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# Define sensor, gate, and servo pins (modify as needed)
sensor_pins = [0, 1, 2, 3]
gate_in_sensor = 7
gate_out_sensor = 6
servo_motor = 8
MIN = 1170000
MAX = 2200000

pwm = PWM(Pin(servo_motor))
pwm.freq(50)
pwm.duty_ns(MIN)

# Initialize parking lot status (replace with a list or dictionary if needed)
parking_state = [False] * 4  # All spaces initially unoccupied

# Define the keypad layout
keypad_rows = [9, 10, 11, 12]  # GPIO pins for rows
keypad_cols = [21, 20, 19]     # GPIO pins for columns

# Initialize the GPIO pins for rows as inputs with pull-up resistors
rows = [Pin(row, Pin.IN, Pin.PULL_UP) for row in keypad_rows]

# Initialize the GPIO pins for columns as outputs
cols = [Pin(col, Pin.OUT) for col in keypad_cols]

# Define the keys on the keypad
keys = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['*', '0', '#']
]
passwords = {0: None, 1: None, 2: None, 3: None}
taken_slots = []
I2C_ADDR     = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_aROWS, I2C_NUM_COLS)    
lcd.putstr("Welcome....")
def is_sensor_triggered(ir_sensor_pin):
  sensor = Pin(ir_sensor_pin, Pin.IN)
  return sensor.value() == 0

def scan_keypad():
    for col_index, col_pin in enumerate(cols):
        col_pin.value(0)  # Activate column
        for row_index, row_pin in enumerate(rows):
            if not row_pin.value():
                return keys[row_index][col_index] # Return the pressed key directly
        col_pin.value(1)  # Deactivate column
    return None  # No button pressed
def available_lot():
    available_slots = []
    for i, space in enumerate(parking_state):
        if space:  # True means a car is parked, so check for False (empty slot)
            available_slots.append(i)
    if available_slots != None:
        return available_slots
    else:
        return "No Free Lot"
def get_taken_slots(slot_number):
  taken_slots.append(slot_number)
def get_password(lcd, slot_number):
    """Gets a password from the user using the keypad (with cancellation option)."""
    print(f"Enter password for slot {slot_number} (or '*' to cancel): ")
    digits = digit_password(lcd)
    if len(digits) < 4:
        print("Password must be greater than 4 digits.")
        return get_password(slot_number)  # Recursively call for retry
    if digits == "":
        return None
    return int(digits)

def set_password(lcd, slot_number):
    """Sets a password for a chosen parking slot."""
    get_taken_slots(slot_number)
    password = get_password(lcd, slot_number)
    if password is not None:
        passwords[slot_number] = password
        taken_slots.append(slot_number)
        sleep(1.5)
        lcd.clear()# Mark slot as occupied
        lcd.putstr(f"Password Saved")
        return
    else:
        print("Password setting canceled.")
def check_password(i, lcd, slot_number):
    i += 1
    if (i == 4):
        return False
    
    lcd.clear()
    sleep(1)
    lcd.putstr("Loading Password\nDatabase")
    sleep(2)
    password = get_password(lcd, slot_number)
    if passwords[slot_number] == password:
        return True
    else:
        lcd.clear()
        sleep(1)
        lcd.putstr("Incorrect Password Try Again")
        check_password(i, lcd, slot_number)
        
def digit_password(lcd):
    digit = ""
    lcd.clear()
    lcd.putstr("Enter Pass (* To Enter # Erase):")
    sleep(1.5)
    lcd.clear()
    lcd.putstr("Enter Password: ")
    while True:
        key = scan_keypad()
        if key == "#":
            digit = digit[:-1]
            lcd.clear()
            lcd.putstr(f"Enter Password: {digit}")
        elif key is not None and key != '*':
            if (len(digit) >= 4):
                lcd.clear()
                lcd.putstr("Only 4 Combinations")
                sleep(1)
                lcd.clear()
                lcd.putstr(f"Enter Password: {digit}")
            else:
                digit += key
            lcd.putstr(f"{key}")
            print(key)
        elif key == '*':
            if (len(digit) < 4):
                lcd.clear()
                lcd.putstr("Wrong Combination")
                sleep(1)
                lcd.clear()
                lcd.putstr("Try Again")
                sleep(1)
                digit_password(lcd)
            else:
                lcd.clear()
                lcd.putstr("Saving.....")
                sleep(1)
                break
        sleep(0.5)
    sleep(1)
    return digit
def digit_slots(lcd):
    digit = ""
    lcd.clear()
    lcd.putstr("Enter Slot No (* To Cancel):")
    while True:
        key = scan_keypad()
        if key == "#":
            digit = digit[:-1]
            lcd.clear()
            lcd.putstr(f"Enter Slot No: {digit}")
        elif key is not None and key != '*':
            if (len(digit) < 1):
                digit += key
                lcd.putstr(f" {key}")
            else:
                lcd.clear()
                lcd.putstr("Sorry Choose One Slot Only")
                sleep(1)
                lcd.clear()
                lcd.putstr("Try Again")
                sleep(1)
                digit_slots(lcd)
            print(key)
        elif key == '*':
            lcd.clear()
            if (digit == ""):
                sleep(1)
                lcd.putstr("See You Soon")
                return False
            else:
                lcd.putstr("Checking For Availability")
                break
            sleep(1)
        sleep(0.5)
    return digit

def display(available_slots):
    sleep(1)
    I2C_ADDR     = 0x27
    I2C_NUM_ROWS = 2
    I2C_NUM_COLS = 16
    i2c = I2C(0, sda=machine.Pin(4), scl=machine.Pin(5), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS) 
    lcd.putstr("Loading.....\nPlease Wait")
    sleep(2)
    lcd.clear()
    sleep(0.5)
    lcd.putstr("Available Slots\n")
    for i in available_slots:
        sleep(1)
        lcd.putstr(f"{i} ")
def digit(lcd):
    lcd.clear()
    sleep(1)
    lcd.putstr("Enter Your Choice:")
    while True:
        key = scan_keypad()
        if key is not None:
            lcd.putstr(f" {key}")
            sleep(1)
            if key == "*" or key == "#":
                sleep(1)
                return key
            else:  
                lcd.putstr("Enter * for Yes Or # For No")
                sleep(1)
                digit(lcd)

while True:
  for i, sensor_pin in enumerate(sensor_pins):
    triggered = is_sensor_triggered(sensor_pin)
    parking_state[i] = not triggered
  available_spaces = parking_state.count(True)
  if is_sensor_triggered(gate_out_sensor):
    if (available_lot() != []):
        available_slots = available_lot()
        print(available_slots)
        display(available_slots)
        sleep(1)
        lcd.clear()
        lcd.putstr("Enter Slots No: ")
        lcd.blink_cursor_on()
        chosen_lot = digit_slots(lcd)
        print(chosen_lot)
        if (chosen_lot == False):
            lcd.clear()
            lcd.putstr("Please Park Your Car Here")
            continue
        else:
            chosen_lot = int(chosen_lot)
        sleep(1)
        print(chosen_lot)
        print(passwords)
        if (chosen_lot in available_slots):
            sleep(1)
            if (passwords[chosen_lot] == None):
                sleep(0.5)
                set_password(lcd, chosen_lot)
                lcd.clear()
                print("Done")
                lcd.putstr("Welcome Once Again")
                pwm.duty_ns(MAX)
                sleep(3)
                pwm.duty_ns(MIN)
            elif (chosen_lot in taken_slots):
              i = 0
              if check_password(i, lcd, chosen_lot):
                print("ok")
                pwm.duty_ns(MAX)
                sleep(3)
                pwm.duty_ns(MIN)
              else:
                sleep(1)
                lcd.clear()
                sleep(1)
                lcd.putstr("Invalid Password For Slot", chosen_lot)
                sleep(1)  
        else:
            sleep(1)
            lcd.clear()
            lcd.putstr("No Available Lot")
            sleep(1)
            lcd.clear()
            lcd.blink_cursor_off()
            lcd.hide_cursor()
  elif (is_sensor_triggered(gate_in_sensor)):
    print(taken_slots)
    lcd.clear()
    sleep(1)
    lcd.putstr("Enter The Lot:")
    lcd.blink_cursor_on()
    chosen = digit_slots(lcd)
    print(chosen)
    if (chosen == False):
        lcd.clear()
        lcd.putstr("Please Park Your Car Here")
        continue
    else:
        chosen = int(chosen)
        sleep(1)
    if (chosen in taken_slots):
        i = 0
        if check_password(i, lcd, chosen):
            lcd.clear()
            lcd.putstr("Are You Coming Back Or Staying: ")
            sleep(2)
            lcd.clear()
            lcd.putstr("Press(* For Yes And # For No)")
            sleep(1)
            leaving_or_comingBack = digit(lcd)
            if (leaving_or_comingBack == "*"):
                pwm.duty_ns(MAX)
                sleep(3)
                pwm.duty_ns(MIN)
                sleep(0.5)
                lcd.clear()
                lcd.putstr("Ok Boss")
                sleep(1)
            else:
                pwm.duty_ns(MAX)
                sleep(3)
                pwm.duty_ns(MIN)
                sleep(0.5)
                lcd.clear()
                lcd.putstr("See You Soon")
                sleep(1)
    else:
        lcd.clear()
        lcd.putstr("Lot Is Not Assigned To You Boss")
        sleep(2)
    sleep(1)
    lcd.clear()
    sleep(1)
    lcd.putstr("Please Park Here")
    sleep(1)
