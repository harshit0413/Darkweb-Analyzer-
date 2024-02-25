# Darkweb-Analyzer

# XGBoost Prediction API

This repository contains a Flask application that serves an XGBoost model to predict outcomes based on features extracted from `.pcap` files.

## Description

The application provides a REST API endpoint to upload `.pcap` files, preprocesses them to extract relevant features, and uses a pre-trained XGBoost model to make predictions.

## Setup

To run this application, you will need Python installed on your machine, as well as the following Python libraries:

- Flask
- pandas
- numpy
- scapy
- xgboost

You can install the dependencies with:


pip install Flask pandas numpy scapy xgboost

Usage
First, clone this repository to your local machine:


git clone https://github.com/your-github-username/xgboost-prediction-api.git
cd xgboost-prediction-api
Before running the application, ensure you have placed the pre-trained XGBoost model file (xgb_model.json) in the root directory of the application or update the model_path in the Flask application to point to the correct path.


To start the server, run:


python app.py
The application will start on http://127.0.0.1:5500/index.html.


API Endpoint
The application exposes the following endpoint:


POST /predict
Allows a user to upload a .pcap file and returns the prediction results.

Parameters:
file: The .pcap file to be processed.
Example:
To upload a file and get predictions, you can use curl:


curl -X POST -F 'file=@/path/to/your/file.pcap' http://127.0.0.1:5000/predict






