from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import threading
import time
import random  # For simulating data
import keysight_ktb2900
import numpy as np # For keysight_ktb2900 arrays
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = ''
socketio = SocketIO(app)

stop_thread = False
latest_value = "ERROR"  # Placeholder for the latest value

def convert_number(number):
    units = [
        (1e24, 'Y'), (1e21, 'Z'), (1e18, 'E'), (1e15, 'P'), (1e12, 'T'),
        (1e9, 'G'), (1e6, 'M'), (1e3, 'k'), (1e0, ''), (1e-3, 'm'),
        (1e-6, 'µ'), (1e-9, 'n'), (1e-12, 'p'), (1e-15, 'f'), (1e-18, 'a'),
        (1e-21, 'z'), (1e-24, 'y')
    ]
    for factor, suffix in units:
        converted = number / factor
        if abs(converted) >= 0.01 and abs(converted) < 999:
            return f"{converted:.4f} {suffix}"
    return f"{number} (no suitable conversion found)"

def generate_list(start, end, n_step):
    if n_step <= 0:
        raise ValueError("Number of steps must be positive.")
    result = np.linspace(start, end, n_step)
    return result.tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    global stop_thread
    stop_thread = False

    data = request.json
    source_voltage = data.get('source_voltage', -1)

    thread = threading.Thread(target=generate_data, args=(source_voltage,))
    thread.start()
    return '', 204

@app.route('/stop', methods=['POST'])
def stop():
    global stop_thread
    stop_thread = True
    return '', 204

@app.route('/sweep', methods=['POST'])
def sweep():
    global stop_thread
    stop_thread = True  # Ensure the live data is stopped

    resource_name = "USB0::0x2A8D::0x9201::MY63320688::INSTR"
    id_query = True
    reset = True
    options = ""
    driver = keysight_ktb2900.KtB2900(resource_name, id_query, reset, options)
    data = request.json

    chip_name = data['chip_name']
    experiment_name = data['experiment_name']
    component_name = data['component_name']
    measurement_type = data['measurement_type']
    working_directory = data['working_directory']
    lower_limit = float(data['lower_limit'])
    upper_limit = float(data['upper_limit'])
    steps = int(data['steps'])
    
    # Generate sweep list
    sweep = generate_list(lower_limit, upper_limit, steps)

    # Simulate the driver setup and measurement
    # Replace with actual driver code
    ModelNo = "B2901A"
    set_measurement_limit = 0.01

    sweep_value = []

    for i in range(len(sweep)):
        driver.outputs[0].voltage.auto_range_enabled = False
        driver.outputs[0].voltage.level = sweep[i]
        # driver.trigger.initiate("1")
        driver.measurements.initiate("1")
        dResult = driver.measurements.fetch_array_data((keysight_ktb2900.MeasurementFetchType.CURRENT), "1")
        
        # Extract the single value from dResult, convert it to a regular float, and round it to 4 decimal places
        value = float(dResult[0])
        sweep_value.append(value)

    # Save the plot
    plt.rcParams['font.family'] = 'Lucida Console'
    title_font_size = 12
    axis_label_font_size = 10
    axis_value_font_size = 8
    marker_size = 1
    marker_opacity = 0.75
    line_thickness = 1
    dpi_value = 150

    plt.figure(figsize=(5, 5), dpi=dpi_value)
    plt.plot(sweep, sweep_value, marker='o', linestyle='-', markersize=marker_size, alpha=marker_opacity, color='b', linewidth=line_thickness)
    plt.xlabel('Sweep (Volts)', fontsize=axis_label_font_size)
    plt.ylabel('Current (Amps)', fontsize=axis_label_font_size)
    plt.title('Sweep Input vs Current', fontsize=title_font_size)
    plt.xticks(fontsize=axis_value_font_size)
    plt.yticks(fontsize=axis_value_font_size)
    plt.grid(True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_filename = f"{chip_name}_{experiment_name}_{component_name}_{measurement_type}_{timestamp}.jpg"
    plot_path = os.path.join(app.config['UPLOAD_FOLDER'], plot_filename)
    plt.savefig(plot_path)
    plt.close()

    # Save the CSV file
    csv_filename = f"{chip_name}_{experiment_name}_{component_name}_{measurement_type}_{timestamp}.csv"
    csv_path = os.path.join(working_directory, csv_filename)
    df = pd.DataFrame({'sweep': sweep, 'sweep_value': sweep_value})
    df.to_csv(csv_path, index=False)

    return jsonify(plot_url=f"/uploads/{plot_filename}")

@app.route('/uploads/<filename>')
def send_plot(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def generate_data(set_source):
    global stop_thread, latest_value

    # resource name should be extracted from NI Visa app
    resource_name = "USB0::0x2A8D::0x9201::MY63320688::INSTR"
    id_query = True
    reset = True
    options = ""
    driver = keysight_ktb2900.KtB2900(resource_name, id_query, reset, options)

    set_measurement_limit = 0.01 
    ModelNo = "B2901A"  # Example model number

    driver.outputs[0].voltage.auto_range_enabled = False
    driver.outputs[0].voltage.level = set_source
    ModelNo = driver.identity.instrument_model
    if (ModelNo == "B2901A" or ModelNo == "B2902A" or ModelNo == "B2911A" or ModelNo == "B2912A" or ModelNo == "B2901B" or ModelNo == "B2902B" or ModelNo == "B2911B" or ModelNo == "B2912B"):
        driver.measurements[0].current.auto_range_enabled = False; #Supported Models for this property: B2901A|B, B2902A|B, B2911A|B, B2912A|B
        driver.measurements[0].current.compliance_value = set_measurement_limit
        driver.outputs[0].enabled = True

    while not stop_thread:
        driver.trigger.initiate("1")
        dResult = driver.measurements.fetch_array_data((keysight_ktb2900.MeasurementFetchType.CURRENT), "1")
        converted_value = convert_number(dResult[0])
        with app.app_context():
            latest_value = converted_value
            socketio.emit('update_value', {'value': latest_value})
        time.sleep(0.1)

if __name__ == '__main__':
    socketio.run(app, debug=True)
