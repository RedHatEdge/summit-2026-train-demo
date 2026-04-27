#!/usr/bin/env python3

import os
import sys
import paho.mqtt.client as mqtt
from pymodbus.client import ModbusSerialClient
from pymodbus.pdu import ExceptionResponse

# --- Configuration ---
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.100.30")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "train/cmd")
MQTT_VOLTAGE_TOPIC = os.getenv("MQTT_VOLTAGE_TOPIC", "train/voltage")

# Voltage Control Parameters
MAX_VOLTAGE = 10.0
MIN_VOLTAGE = 0.0

# Modbus Registers
SPEED_REG = 0x6000 # AO0
DIR_REG = 0x6001   # AO1

# --- Global State ---
current_voltage = 0.0
current_direction = "forward"

# --- Modbus Setup ---
modbus_client = ModbusSerialClient(
    port="/dev/mtx_tty_mb",
    baudrate=115200,
    parity="N",
    stopbits=1,
    bytesize=8,
    timeout=1
)

def write_modbus_ao(register, volts, label):
    val = int((volts / 10.3) * 32767) 
    unit_id = 188

    if not modbus_client.is_socket_open():
        modbus_client.connect()

    response = modbus_client.write_registers(register, [val], device_id=unit_id)
    if isinstance(response, ExceptionResponse) or response.isError():
        print(f"Modbus error writing to {label}")
    else:
        print(f"{label} set to {volts:.2f}V (Raw: {val})")

def update_motor_state(client=None):
    global current_voltage, current_direction
    
    # Absolute safety cap at 10.0V
    current_voltage = max(MIN_VOLTAGE, min(MAX_VOLTAGE, current_voltage))

    # 1. Write Speed
    write_modbus_ao(SPEED_REG, current_voltage, 'ao0_speed')
    
    # 2. Write Direction (0V for Forward, 10.0V for Reverse)
    dir_volts = MIN_VOLTAGE if current_direction == "forward" else MAX_VOLTAGE
    write_modbus_ao(DIR_REG, dir_volts, 'ao1_dir')
    
    # 3. Publish Voltage to MQTT
    if client is not None:
        client.publish(MQTT_VOLTAGE_TOPIC, str(current_voltage))
        print(f"Published voltage {current_voltage}V to '{MQTT_VOLTAGE_TOPIC}'")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to MQTT broker. Subscribed to: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
        update_motor_state(client)

def on_message(client, userdata, msg):
    global current_voltage, current_direction
    command = msg.payload.decode('utf-8').strip().lower()
    print(f"Command received: '{command}'")

    state_changed = False

    if command == "start":
        if current_voltage != 10.0:
            current_voltage = 10.0
            state_changed = True
    elif command == "stop":
        if current_voltage != 0.0:
            current_voltage = 0.0
            state_changed = True
    elif command == "slow":
        if current_voltage != 4.0:
            current_voltage = 4.0
            state_changed = True
    elif command == "reverse":
        # Flip the current direction
        current_direction = "reverse" if current_direction == "forward" else "forward"
        state_changed = True
    else:
        print(f"Ignored unknown command: {command}")
        return

    if state_changed:
        update_motor_state(client)
    else:
        print(f"State unchanged. Speed: {current_voltage:.2f}V, Dir: {current_direction}")

def main():
    global current_voltage, current_direction 
    
    print("Starting Motor Service...")

    try:
        mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except AttributeError:
        mqtt_client = mqtt.Client()

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"Cannot connect to MQTT broker: {e}")
        sys.exit(1)

    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        current_voltage = MIN_VOLTAGE
        current_direction = "forward"
        update_motor_state(mqtt_client)
        
        modbus_client.close()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()