from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import numpy as np
import pandas as pd
from scapy.all import rdpcap, IP, TCP
import xgboost as xgb

app = Flask(__name__, template_folder='.')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
CORS(app)

MODEL_PATH = './xgb_model.json'
xgb_model = xgb.XGBClassifier()
xgb_model.load_model(MODEL_PATH)

def preprocess_pcap(file_path):
    packets = rdpcap(file_path)
    features = {
        'Flow Duration': 0.0,
        'Total Fwd Packet': 0,
        'Total Bwd packets': 0,
        'Packet Length Min': np.inf,
        'Packet Length Mean': 0.0,
        'Fwd IAT Total': 0.0,
        'Flow IAT Min': np.inf,
        'Flow IAT Max': 0.0,
        'Fwd IAT Mean': 0.0,
        'Flow Packets/s': 0.0,
        'Flow Bytes/s': 0.0,
        'Idle Min': np.inf,
        'Idle Max': 0.0,
        'Idle Mean': 0.0,
        'Idle Std': 0.0,
        'FWD Init Win Bytes': 0,
        'Bwd Init Win Bytes': 0,
        'ACK Flag Count': 0
    }

    if not packets:
        return pd.DataFrame(features, index=[0])

    start_times = []
    packet_lengths = []
    iats = []
    total_bytes = 0

    for packet in packets:
        if IP in packet and TCP in packet:
            packet_length = len(packet)
            packet_lengths.append(packet_length)
            total_bytes += packet_length

            if 'S' in packet[TCP].flags:
                if features['FWD Init Win Bytes'] == 0:
                    features['FWD Init Win Bytes'] = packet[TCP].window
                else:
                    features['Bwd Init Win Bytes'] = packet[TCP].window

            if 'A' in packet[TCP].flags:
                features['ACK Flag Count'] += 1

            start_times.append(float(packet.time))

            if len(start_times) > 1:
                iat = start_times[-1] - start_times[-2]
                iats.append(iat)

    features['Flow Duration'] = max(start_times) - min(start_times)
    features['Total Fwd Packet'] = len([p for p in packets if IP in p and p[IP].src < p[IP].dst])
    features['Total Bwd packets'] = len([p for p in packets if IP in p and p[IP].src > p[IP].dst])
    features['Packet Length Min'] = min(packet_lengths)
    features['Packet Length Mean'] = np.mean(packet_lengths) if packet_lengths else 0
    features['Fwd IAT Total'] = sum(iats)
    features['Flow IAT Min'] = min(iats) if iats else 0
    features['Flow IAT Max'] = max(iats) if iats else 0
    features['Fwd IAT Mean'] = np.mean(iats) if iats else 0
    features['Flow Packets/s'] = len(packets) / features['Flow Duration'] if features['Flow Duration'] else 0
    features['Flow Bytes/s'] = total_bytes / features['Flow Duration'] if features['Flow Duration'] else 0

    df_features = pd.DataFrame([features])
    df_features.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_features.fillna(0, inplace=True)
    return df_features

def predict_darknet(file_path):
    try:
        df_features = preprocess_pcap(file_path)
        predictions = xgb_model.predict(df_features)
        return predictions.tolist()  # Convert numpy array to list for JSON serialization
    except Exception as e:
        print("Error predicting:", e)
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        predictions = predict_darknet(file_path)
        if predictions is not None:
            return jsonify({'prediction': predictions})
        else:
            return jsonify({'error': 'Failed to make predictions'}), 500
    except Exception as e:
        print("Error processing file:", e)
        return jsonify({'error': 'Failed to process the file. Please try again.'}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
