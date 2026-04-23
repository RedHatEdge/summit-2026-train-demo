#!/usr/bin/env python3

import os
import sys
import paho.mqtt.client as mqtt
from pymodbus.client import ModbusSerialClient
from pymodbus.pdu import ExceptionResponse
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# --- Configuration ---
MQTT_BROKER = os.getenv("MQTT_BROKER", "192.168.100.30")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "train/cmd")
PUSHGATEWAY_URL = os.getenv("PUSHGATEWAY_URL", "http://localhost:9091")

# Voltage Control Parameters
MAX_VOLTAGE = 10.0
MIN_VOLTAGE = 0.0

# Modbus Registers
SPEED_REG = 0x6000 # AO0
DIR_REG = 0x6001   # AO1

# --- Global State ---
current_voltage = 0.0
current_direction = "forward"

# --- Prometheus Setup ---
registry = CollectorRegistry()
metrics = {
    'voltage': Gauge('voltage', 'Voltage from analog output', ['output'], registry=registry),
    'register': Gauge('register', 'Modbus register', ['output'], registry=registry),
    'raw_value': Gauge('raw_value', 'Converted raw modbus value', ['output'], registry=registry),
    'direction': Gauge('direction', 'Motor Direction (1=Fwd, -1=Rev)', registry=registry)
}

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

    metrics['voltage'].labels(output=label).set(volts)
    metrics['register'].labels(output=label).set(register)
    metrics['raw_value'].labels(output=label).set(val)

    if not modbus_client.is_socket_open():
        modbus_client.connect()

    response = modbus_client.write_registers(register, [val], device_id=unit_id)
    if isinstance(response, ExceptionResponse) or response.isError():
        print(f"Modbus error writing to {label}")
    else:
        print(f"{label} set to {volts:.2f}V (Raw: {val})")

def update_motor_state():
    global current_voltage, current_direction
    
    # Absolute safety cap at 10.0V
    current_voltage = max(MIN_VOLTAGE, min(MAX_VOLTAGE, current_voltage))

    # 1. Write Speed
    write_modbus_ao(SPEED_REG, current_voltage, 'ao0_speed')
    
    # 2. Write Direction (0V for Forward, 10.0V for Reverse)
    dir_volts = MIN_VOLTAGE if current_direction == "forward" else MAX_VOLTAGE
    write_modbus_ao(DIR_REG, dir_volts, 'ao1_dir')
    
    # Update Direction Metric
    dir_metric_val = 1 if current_direction == "forward" else -1
    metrics['direction'].set(dir_metric_val)

    try:
        push_to_gateway(PUSHGATEWAY_URL, job='motor_controller', registry=registry)
    except Exception as e:
        pass

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to MQTT broker. Subscribed to: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)

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
        update_motor_state()
    else:
        print(f"State unchanged. Speed: {current_voltage:.2f}V, Dir: {current_direction}")

def main():
    global current_voltage, current_direction 
    
    print("Starting Motor Service...")
    # Initialize at 0V and Forward
    update_motor_state()

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
        update_motor_state()
        
        modbus_client.close()
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()