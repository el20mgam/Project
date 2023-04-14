import sqlite3
import time


def update_lft_table(qr_code, outcome, control_magenta, test_magenta):
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

    # Get the current date and time to the second
    date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # Save the outcome to the database
    cursor.execute('''INSERT INTO lft (datetime, qr_code, outcome, control_magenta, test_magenta)
                      VALUES (?, ?, ?, ?, ?)''', (date_time, qr_code, outcome, control_magenta, test_magenta))
    conn.commit()

    # Close the database connection
    conn.close()


def main():
    while True:
        # Get input from the user
        qr_code = input("Enter the QR code: ")
        if qr_code.lower() == 'q':
            break

        outcome = input("Enter the outcome (Invalid, Negative, or Positive): ")
        control_magenta = float(input("Enter the control magenta percentage: "))
        test_magenta = float(input("Enter the test magenta percentage: "))

        update_lft_table(qr_code, outcome, control_magenta, test_magenta)
        print(f"Updated lft table with: QR Code - {qr_code}, Outcome - {outcome}, Control Magenta - {control_magenta}%, Test Magenta - {test_magenta}%\n")


if __name__ == "__main__":
    main()
