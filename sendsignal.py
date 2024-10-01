import serial
import time


with serial.Serial('/dev/pts/3', baudrate=9600, timeout=1) as ser:
    time.sleep(2)

    ser.write(b'm')
    print("Sent 'm' to serial port.")

    response = ser.read(10)
    print(f"Response: {response}")
