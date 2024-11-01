
import sys

import argparse
from awscrt import mqtt
from awsiot import mqtt_connection_builder
import json
import time
import pynmea2
import keyboard

# File path for GPS data
file_path = "/files/trip.nmea"

# Global terminate flag
terminate = False


# Function to handle GPS data reading and publishing to AWS IoT
def gpsRead(mqtt_connection, topic, pub_period):
    global terminate  # Access the global terminate flag
    count = 1
    group = 1
    data ={}
    trip = open(file_path, 'r')

    for line in trip:
        # Check if termination is requested
        if terminate:
            print("Termination requested. Exiting gpsRead loop...")
            break


        try:
            info = pynmea2.parse(line.strip())
            if line.startswith('$GPGGA'):
                # Extracting the relevant data (timestamp, latitude, longitude)
                data = {'count': count, 'app': 'group31', 'timestamp': int(time.time()), 'latitude': info.latitude,
                        'longitude': info.longitude}
                # gpsData.append(data)
                #print(data)

                # Publish to AWS IoT
                jsonPayload(data, mqtt_connection, topic)
                time.sleep(pub_period)
                count += 1
        except pynmea2.ParseError:
            print("Error parsing line, skipping line...")

        group += 1

    return data


# Function to create JSON payload and publish to MQTT
def jsonPayload(gps_data, mqtt_connection, topic):

    # Convert GPS data to JSON and publish
    try:
        json_data = json.dumps(gps_data, indent=4)
        mqtt_connection.publish(topic=topic, payload=json_data, qos=mqtt.QoS.AT_LEAST_ONCE)
        print(json_data)
    except Exception as e:
        print("Failed to publish data:", e)
    time.sleep(1)

# Argument parser function
def parse_arguments():
    parser = argparse.ArgumentParser(description="GPS data publisher to AWS IoT")
    parser.add_argument("--pub_period", type=int, default=5, help="publish period")
    parser.add_argument("--debug", type=int, default=0, help="Enable debug messages")
    parser.add_argument("--version", action="store_true", help="version number")
    return parser.parse_args()

# Main function to handle MQTT connection and data sending
def mqtt_send_data():
    # Parse arguments
    args = parse_arguments()
    pub_period = args.pub_period

    global terminate  # Access the global terminate flag

    # AWS IoT connection details
    serial_number = "beesaal"
    endpoint = "a2zriqmzklk5bf-ats.iot.ca-central-1.amazonaws.com"
    keep_alive_secs = 60
    topic = f"dt/conestoga/esd/lab/{serial_number}"

    ca_filepath = "../certificates/AmazonRootCA1.pem"
    cert_filepath = "../certificates/certificate.pem.crt"
    key_filepath = "../certificates/private.pem.key"

    # Setup MQTT connection
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        cert_filepath=cert_filepath,
        pri_key_filepath=key_filepath,
        ca_filepath=ca_filepath,
        client_id=serial_number,
        clean_session=False,
        keep_alive_secs=keep_alive_secs
    )

    # Connect to AWS IoT
    print("Connecting...")
    try:
        connect_future = mqtt_connection.connect()
        connect_future.result()
        print("Connected!")
    except Exception as e:
        print(f"Failed to connect to AWS IoT: {e}")
        return


    # Notify user about the quit option
    print("Press 'q' at any time to terminate the program.")

    # Start hotkey listener to set terminate flag
    keyboard.add_hotkey('q', lambda: set_terminate())

    # Read GPS data and publish each line to AWS IoT
    gpsRead(mqtt_connection, topic, pub_period)


    # Disconnect from AWS IoT if not already terminated
    if not terminate:
        print("Disconnecting...")
        try:
            disconnect_future = mqtt_connection.disconnect()
            disconnect_future.result()
            print("Disconnected!")
        except Exception as e:
            print(f"Error during disconnect: {e}")


# Helper function to set the terminate flag
def set_terminate():
    global terminate
    print("Termination requested with 'q'.")
    terminate = True
    sys.exit()  # Ensure the program fully exits when 'q' is pressed


if __name__ == '__main__':
    args = parse_arguments()
    mqtt_send_data()
