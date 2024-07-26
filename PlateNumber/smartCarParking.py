import cv2
import pytesseract

def image_to_text():        
    # Path to Tesseract executable (update as needed)
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

    # Load an image
    image_path = "WIN_20240711_09_28_55_Pro.jpg"
    image = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Perform OCR using Tesseract
    text = pytesseract.image_to_string(gray)

    # Print the extracted text
    print("Extracted Text:")
    print(text)

if __name__ == "__main__":
    image_to_text()