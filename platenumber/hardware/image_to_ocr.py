from easyocr import Reader
from .pi_camera import Camera

camera = Camera()
reader = Reader(['en'], gpu=False)

class PlateNumber:
    def __init__(self):
        pass
   
    def is_valid_license_plate(self, text):
        # Simple check for valid license plate format
        if len(text) == 8 and text[:3].isalpha() and text[4:7].isdigit() and text[7:].isalpha():
            return True
        return False

    def run(self):
        while True:
            cropped_image_path = camera.run()
            result = reader.readtext(cropped_image_path)

            if not result:
                print("Failed to detect plate number.")
                choice = input("Would you like to try again or enter manually? (try again/manual): ").strip().lower()
                if choice == "manual":
                    manual_input = input("Please enter the license plate manually: ").strip()
                    cleaned_text = manual_input.replace(" ", "").replace("-", "")
                    if self.is_valid_license_plate(cleaned_text):
                        print(f"Valid License Plate Detected: {cleaned_text}")
                        break
                    else:
                        print("Invalid license plate format. Please try again.")
                elif choice == "try again":
                    print("Retrying...")
                    continue
                else:
                    print("Invalid choice. Exiting.")
                    break
            else:
                # Print the extracted text and check for valid license plate format
                print("Extracted Text:")
                for (bbox, text, prob) in result:
                    cleaned_text = text.replace(" ", "").replace("-", "")
                    
                    if self.is_valid_license_plate(cleaned_text):
                        print(f"Valid License Plate Detected: {cleaned_text} (Probability: {prob:.2f})")
                        return cleaned_text
                    elif len(cleaned_text) > 7:
                        print(f"Detected Text: {cleaned_text} (Probability: {prob:.2f})")
                        break
                    else:
                        continue

                print("Admin please confirm Text")
                print(cleaned_text)
                if input("Yes to manually update or No to cancel operation: ").strip().lower() == "yes":
                    manual_input = input("Please enter the license plate manually: ").strip()
                    cleaned_text = manual_input.replace(" ", "").replace("-", "")
                    return cleaned_text
                else:
                    return cleaned_text
                
 