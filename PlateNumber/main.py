import cv2
import imutils
import numpy as np
import easyocr
import os
import time

# Ensure the directory exists
output_dir = "platenumbersimage"
os.makedirs(output_dir, exist_ok=True)

# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'])

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

def detect_and_crop(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to gray scale
    gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Blur to reduce noise
    edged = cv2.Canny(gray, 30, 200)  # Perform edge detection

    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
    screenCnt = None

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        detected = 0
        print("No contour detected")
        return None, None
    else:
        detected = 1

    if detected == 1:
        cv2.drawContours(frame, [screenCnt], -1, (0, 255, 0), 3)

    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1,)
    new_image = cv2.bitwise_and(frame, frame, mask=mask)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

    return cropped, frame

def is_valid_license_plate(text):
    if len(text) == 8 and text[:3].isalpha() and text[4:7].isdigit() and text[7:].isalpha():
        return True
    return False
def get_next_filename(base_dir, base_name, extension):
    counter = 1
    while True:
        file_name = f"{base_name}_{counter:03d}.{extension}"
        file_path = os.path.join(base_dir, file_name)
        if not os.path.exists(file_path):
            return file_path
        counter += 1

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture image.")
        break

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        start_time = time.time()
        while time.time() - start_time < 40:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture image.")
                break

            remaining_time = 40 - int(time.time() - start_time)
            cv2.putText(frame, f"Time remaining: {remaining_time}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cropped, display_frame = detect_and_crop(frame)
        if cropped is not None:
            cropped_image_path = get_next_filename(output_dir, "cropped_image", "png")
            cv2.imwrite(cropped_image_path, cropped)
            print(f"Image saved as {cropped_image_path}")

            # Close the camera window
            cap.release()
            cv2.destroyAllWindows()

            # Perform OCR using EasyOCR
            result = reader.readtext(cropped_image_path)

            # Print the extracted text and check for valid license plate format
            print("Extracted Text:")
            for (bbox, text, prob) in result:
                cleaned_text = text.replace(" ", "").replace("-", "")
                if is_valid_license_plate(cleaned_text):
                    print(f"Valid License Plate Detected: {cleaned_text} (Probability: {prob:.2f})")
                else:
                    print(f"Detected Text: {cleaned_text} (Probability: {prob:.2f})")

        break

cap.release()
cv2.destroyAllWindows()
