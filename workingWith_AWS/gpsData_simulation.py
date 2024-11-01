import pynmea2
import sys
import argparse
import time
import keyboard
import json

delay = 0.005

# file path directly
file_path = "D:/WorkSpaces/pyCharm/workingwith_AWS/files/trip.nmea"


def gpsRead(file_path, debug=False):
    count = 1
    group = 1
    data = {}
    trip = open(file_path, 'r')

    for line in trip:
        if debug:
            print(f"Reading line: {line.strip()}")

        try:
            info = pynmea2.parse(line.strip())
            if line.startswith('$GPGGA'):
                # Extracting the relevant data (timestamp, latitude, longitude)
                data = {'count': count, 'app': 'group31', 'timestamp': int(time.time()), 'latitude': info.latitude, 'longitude': info.longitude}
               # gpsData.append(data)
                print(data)
                time.sleep(5)
                count += 1
        except pynmea2.ParseError:
            if debug:
                print("Error parsing line, skipping line...")

        group += 1

    return data

# function to create a JSON payload from the GPS data
def jsonPayload(gpsData, debug=False):
    if debug:
        time.sleep(delay)
        print("\n\nCreating JSON Payload...")

    # Convert list of GPS data to a JSON formatted string
    jsonData = json.dumps(gpsData, indent=4)
    print(jsonData)


# function to ask the user if they want to enable debug mode and version or not
def get_user_options():
    # if the user wants to enable debug messages
    debug_option = input("Do you want to enable debug messages? (yes/no): ").lower()
    debug = True if debug_option == 'yes' else False

    # if the user wants the version
    version_option = input("Do you want to display the version number? (yes/no): ").lower()
    if version_option == 'yes':
        print("\n\nProgram Version: 1.0\nAuthor: Bishal Kafle\n")

    return debug

def quit():
    print('Exiting the program.')
    sys.exit(0)

# Main function
def main():
    # Get user options for debug and version
    debug = get_user_options()

    # Read the GPS data from the specified file
    gpsData = gpsRead(file_path, debug)  # Pass the debug flag to gpsRead

    # Convert and display JSON payload
    jsonPayload(gpsData, debug)

    # Wait for the user to press 'q' to exit
    print("Press 'q' to quit.")
    while True:
        keyboard.add_hotkey('q', lambda : quit())



# Ensure this script runs as the main program
if __name__ == '__main__':
    main()
