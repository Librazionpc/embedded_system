import cv2
import imutils
import numpy as np
import os
import time
from picamera2 import Picamera2

class Camera():
    __output_dir = "../models/engine/platenumbersimage"
    __picam2 = Picamera2()

    def __init__(self):
        pass

    def __detect_and_crop(self, frame):
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
        new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1)
        new_image = cv2.bitwise_and(frame, frame, mask=mask)

        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

        return cropped, frame

    def __get_next_filename(self, base_dir, base_name, extension):
        """Create a list of image files."""
        counter = 1
        while True:
            file_name = f"{base_name}_{counter:03d}.{extension}"
            file_path = os.path.join(base_dir, file_name)
            if not os.path.exists(file_path):
                return file_path
            counter += 1

    def run(self):
        Camera.__picam2.start()  # Start the camera

        # Set the duration for capturing images
        capture_duration = 20  # Duration in seconds
        start_time = time.time()
        end_time = start_time + capture_duration

        while True:
            frame = Camera.__picam2.capture_array()
            if frame is None:
                print("Error: Failed to capture image.")
                break

            # Show the current frame
            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Check if the duration has elapsed
            if time.time() > end_time:
                break

        # Process the last captured frame
        cropped, display_frame = self.__detect_and_crop(frame)
        if cropped is not None or frame is not None:
            if cropped is None:
                cropped = frame
            if not os.path.exists(Camera.__output_dir):
                if input("Directory does not exist. Create new one? (Yes/No): ").lower() == "yes":
                    os.makedirs(Camera.__output_dir, exist_ok=True)
                    print("Admin created new image folder.")
            else:
                print("Found image folder for confirmation.")

            cropped_image_path = self.__get_next_filename(Camera.__output_dir, "cropped_image", "png")
            cv2.imwrite(cropped_image_path, cropped)
            print(f"Image saved as {cropped_image_path}")

        # Close the camera window
        Camera.__picam2.stop()  # Stop the camera
        cv2.destroyAllWindows()
        
        return cropped_image_path

