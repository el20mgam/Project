import cv2

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize QR code detector
qr_detector = cv2.QRCodeDetector()

# Initialize variable to keep track of previous QR codes
prev_qr_codes = set()

while True:
    # Capture image from webcam
    ret, frame = cap.read()

    # Detect QR codes in the image
    decoded_qr_codes, points, _ = qr_detector.detectAndDecode(frame)

    # Check if any new QR codes have been detected
    new_qr_codes = set(decoded_qr_codes) - prev_qr_codes

    # Take a photo if a new QR code is detected
    if new_qr_codes:
        # Use the decoded QR code as the filename
        cv2.imwrite(f'{str(decoded_qr_codes)}.jpg', frame)

    # Update previous QR codes
    prev_qr_codes = set(decoded_qr_codes)

    # Display the image with QR code boundaries
    if decoded_qr_codes is not None:
        if points is not None:
            for i in range(len(points)):
                if i < len(decoded_qr_codes):  # Check if i is a valid index for decoded_qr_codes
                    cv2.putText(frame, decoded_qr_codes[i], (int(points[i][0][0]), int(points[i][0][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('frame', frame)

    # Quit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
