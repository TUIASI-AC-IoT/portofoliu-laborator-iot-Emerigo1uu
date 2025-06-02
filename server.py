import os
import re
import random
import datetime
import serial.tools.list_ports
from time import sleep
from threading import Thread, Lock
from serial import Serial
from flask import Flask, jsonify, request, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import atexit

# --- Serial Setup ---
DEVICE_PORT = 'COM12'
DEVICE_BAUD = 115200
device_serial = None
use_simulation = False
sync_lock = Lock()
current_temperature = 20.0
last_read_time = datetime.datetime.now()

# List available ports
print("Available serial ports:")
for p in serial.tools.list_ports.comports():
    print(f"  {p.device}: {p.description}")

# Try connecting to serial
try:
    print(f"Connecting to {DEVICE_PORT} at {DEVICE_BAUD} baud...")
    device_serial = Serial(DEVICE_PORT, DEVICE_BAUD, timeout=1)
    print("Connection established")
    device_serial.write(b'\n')
    sleep(0.5)
    if device_serial.in_waiting:
        print(f"Buffer data: {device_serial.in_waiting} bytes")
        print("Initial read:", device_serial.readline().decode().strip())
    else:
        print("No data in buffer, enabling simulation")
        use_simulation = True
except Exception as connect_err:
    print(f"Serial error: {connect_err}\nStarting in simulation mode")
    use_simulation = True

# Ensure serial port closes on exit
def shutdown_serial():
    if device_serial and device_serial.is_open:
        print("Closing serial connection...")
        device_serial.close()
atexit.register(shutdown_serial)

# --- Flask Setup ---
app = Flask(__name__)
SWAGGER_UI_PATH = '/swagger'
SPEC_FILE_URL = '/static/swagger.json'
app.register_blueprint(get_swaggerui_blueprint(SWAGGER_UI_PATH, SPEC_FILE_URL, config={'app_name': "IoT Temperature Sensor API"}), url_prefix=SWAGGER_UI_PATH)

@app.route('/static/swagger.json')
def get_swagger_file():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'swagger.json')

# --- Sensor Reader Thread ---
def simulate_temperature():
    global current_temperature
    current_temperature = max(10, min(30, current_temperature + random.uniform(-0.5, 0.5)))
    return current_temperature

def poll_temperature():
    global current_temperature, last_read_time, use_simulation
    failure_count = 0
    FAILURE_LIMIT = 10

    while True:
        try:
            if use_simulation:
                temp_val = simulate_temperature()
            else:
                if not device_serial or not device_serial.is_open:
                    raise Exception("Serial connection missing")

                device_serial.write(b'GET\n')
                sleep(0.7)
                if device_serial.in_waiting:
                    reply = device_serial.readline().decode().strip()
                    match = re.search(r'\d+\.\d+', reply)
                    if match:
                        temp_val = float(match.group())
                        failure_count = 0
                    else:
                        raise ValueError("Invalid temperature format")
                else:
                    raise Exception("No data returned")

            with sync_lock:
                current_temperature = temp_val
                last_read_time = datetime.datetime.now()

            print(f"Temperature updated: {temp_val} °C")
        except Exception as read_err:
            print(f"Sensor polling error: {read_err}")
            failure_count += 1
            if failure_count >= FAILURE_LIMIT:
                print("Exceeded error threshold, switching to simulation mode")
                use_simulation = True

        sleep(2)

Thread(target=poll_temperature, daemon=True).start()
print("Background sensor thread started")

# --- Utility ---
def execute_device_command(cmd):
    if use_simulation:
        return "Simulation mode: command skipped"
    try:
        if device_serial.in_waiting:
            device_serial.reset_input_buffer()
        device_serial.write(f"{cmd}\n".encode())
        sleep(0.3)
        if device_serial.in_waiting:
            reply = device_serial.readline().decode().strip()
            return reply if reply else "No response"
        return "No response"
    except Exception as cmd_err:
        return f"Error: {cmd_err}"

# --- API Endpoints ---
@app.route('/temperature', methods=['GET'])
def api_get_temperature():
    with sync_lock:
        temp = current_temperature
        updated = last_read_time
    age = (datetime.datetime.now() - updated).total_seconds()
    return jsonify({
        "value": round(temp, 2),
        "unit": "°C",
        "timestamp": updated.isoformat(),
        "age_seconds": age,
        "simulation_mode": use_simulation
    })

@app.route('/control/<action_name>', methods=['POST'])
def api_control_device(action_name):
    action = action_name.upper()
    if action in ["HEATER", "COOLER", "STOP"]:
        for attempt in [action, f"SET {action}"]:
            reply = execute_device_command(attempt)
            if reply != "No response" and not reply.startswith("Error"):
                break
        return jsonify({"message": f"{action} command sent", "response": reply, "simulation_mode": use_simulation})
    return jsonify({"error": "Invalid action. Use 'heater', 'cooler', or 'stop'"}), 400

@app.route('/manual_command', methods=['POST'])
def api_manual_command():
    payload = request.get_json()
    if not payload or 'command' not in payload:
        return jsonify({"error": "Missing 'command' parameter"}), 400
    command = payload['command']
    reply = execute_device_command(command) if not use_simulation else f"Type manually: {command}"
    return jsonify({"command": command, "response": reply, "simulation_mode": use_simulation})

@app.route('/status', methods=['GET'])
def api_status():
    try:
        open_state = device_serial.is_open if device_serial else False
        waiting = device_serial.in_waiting if open_state else 0
    except:
        open_state, waiting = False, 0
    return jsonify({
        "connected": open_state,
        "port": DEVICE_PORT,
        "baudrate": DEVICE_BAUD,
        "bytes_waiting": waiting,
        "simulation_mode": use_simulation,
        "last_temperature": round(current_temperature, 2),
        "last_update": last_read_time.isoformat()
    })

@app.route('/simulation', methods=['POST'])
def api_toggle_simulation():
    global use_simulation
    payload = request.get_json()
    if not payload or 'enabled' not in payload:
        return jsonify({"error": "Missing 'enabled' parameter"}), 400
    use_simulation = bool(payload['enabled'])
    return jsonify({"message": f"Simulation mode {'enabled' if use_simulation else 'disabled'}", "simulation_mode": use_simulation})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
