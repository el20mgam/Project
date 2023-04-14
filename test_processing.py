import time
import cv2
from PIL import Image
import sqlite3


def contains_magenta(pil_image, region):
    cmyk_image = pil_image.convert('CMYK')
    max_magenta_percentage = 0
    for x in range(region[0], region[0] + region[2]):
        for y in range(region[1], region[1] + region[3]):
            c, m, y, k = cmyk_image.getpixel((x, y))
            magenta_percentage = m / 255 * 100
            max_magenta_percentage = max(max_magenta_percentage, magenta_percentage)
            if magenta_percentage > 50:
                return True, max_magenta_percentage
    return False, max_magenta_percentage


# Connect to the SQLite database
conn = sqlite3.connect('co2_measurements_IOM.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS lft (
                    datetime TEXT,
                    qr_code TEXT,
                    outcome TEXT,
                    control_magenta REAL,
                    test_magenta REAL
                )''')

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize QR code detector
qr_detector = cv2.QRCodeDetector()

# Initialize variable to keep track of previous QR codes
prev_qr_codes = set()

# Define your two regions as (x, y, width, height)
control = (1414, 733, 39, 13)
test = (1424, 788, 30, 8)

while True:
    ret, frame = cap.read()

    # Check if the frame is not None before processing
    if frame is not None:

        decoded_qr_codes, points, _ = qr_detector.detectAndDecode(frame)
        new_qr_codes = set(decoded_qr_codes) - prev_qr_codes

        if new_qr_codes:
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            magenta_in_control, control_max_magenta = contains_magenta(pil_image, control)
            magenta_in_test, test_max_magenta = contains_magenta(pil_image, test)

            outcome = ""
            if not magenta_in_control and not magenta_in_test:
                outcome = "Invalid"
            elif not magenta_in_test and magenta_in_control:
                outcome = "Negative"
            elif magenta_in_test and magenta_in_control:
                outcome = "Positive"

            print(f"QR Code: {decoded_qr_codes}")
            print(f"Outcome: {outcome}")
            print(f"Control magenta percentage: {control_max_magenta:.2f}%")
            print(f"Test magenta percentage: {test_max_magenta:.2f}%")

            # Get the current date and time to the second
            date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            # Save the outcome to the database
            cursor.execute('''INSERT INTO lft (qr_code, outcome, control_magenta, test_magenta)
                              VALUES (?, ?, ?, ?, ?)''', (date_time, decoded_qr_codes, outcome, control_max_magenta, test_max_magenta))
            conn.commit()

            cv2.imwrite(f'{str(decoded_qr_codes)}.jpg', frame)

        prev_qr_codes = set(decoded_qr_codes)

    if decoded_qr_codes is not None:
        if points is not None:
            for i in range(len(points)):
                if i < len(decoded_qr_codes):
                    cv2.putText(frame, decoded_qr_codes[i], (int(points[i][0][0]), int(points[i][0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('frame', frame)

    # Quit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Close the database connection
conn.close()
