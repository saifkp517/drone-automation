import serial
import threading
import time

#continously read from the serial (testing)
def read_from_serial(ser):
    while True:
        response = ser.read(10)
        if response:
            print(f"Response from serial: {response.decode(errors='ignore')}")

def write_to_serial(ser):
    while True:
        command = input("Enter command: ")
        ser.write(command.encode())
        print(f"Sent '{command} to serial port")

def main():
    with serial.Serial('/dev/pts/4', baudrate=9600, timeout=1) as ser:
        time.sleep(2)

        #using seperate threads cuz we dont want to mess with the main serial function
        read_thread = threading.Thread(target=read_from_serial, args=(ser,), daemon=True)
        read_thread.start()

        write_to_serial(ser)

if __name__ == "__main__":
    main()

