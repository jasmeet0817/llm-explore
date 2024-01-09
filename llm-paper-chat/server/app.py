from flask import Flask, request
from flask_cors import CORS
from http.server import HTTPServer, SimpleHTTPRequestHandler

import ssl
import os
import requests
import csv

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://[2401:4900:1c74:2a2a:90c6:b158:a154:f734]"}})

# Define the path for the upload folder
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SOURCE_IDS_FILE'] = os.path.join(app.config['UPLOAD_FOLDER'], 'source_ids.csv')

# Set the port number and certificate/key file paths
port = 5000
cert_file = 'ssl-certs/fullchain.pem'
key_file = 'ssl-certs/privkey.pem'


def is_file_id_in_csv(fileId):
    with open(app.config['SOURCE_IDS_FILE'], 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                _, fileIdFromCsv = row
                if fileId.strip() == fileIdFromCsv.strip():
                    return True
    return False


def write_to_csv_file(col1, col2):
    with open(app.config['SOURCE_IDS_FILE'], 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([col1, ' ' + col2])


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    # Save the file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Upload the file to the server
    files = [
        ('file', ('file', open(filepath, 'rb'), 'application/octet-stream'))
    ]
    headers = {
        'x-api-key': 'sec_p8RhLwo5kE14CFKTFUefCjirVdtvwiGR'
    }

    chat_pdf_response = requests.post(
        'https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)

    response = {}
    if chat_pdf_response.status_code == 200:
        response['fileId'] = chat_pdf_response.json()['sourceId']
        
        # Save fileId and file.filename to the CSV file
        write_to_csv_file(file.filename, ' ' + response['fileId'])

    else:
        response['error'] = chat_pdf_response.text
        return response, chat_pdf_response.status_code

    return response, 200



@app.route('/resume', methods=['POST'])
def resume_file():
    response = {}
    
    if 'fileId' not in request.form:
        response['error'] = 'No file id'
        return response, 400

    fileId = request.form['fileId']
    if not is_file_id_in_csv(fileId):
        response['error'] = 'File not found'
        return response, 404

    response['fileId'] = fileId
    return response, 200


def send_message_to_chat_pdf(fileId, message):
    headers = {
    'x-api-key': 'sec_p8RhLwo5kE14CFKTFUefCjirVdtvwiGR',
    "Content-Type": "application/json",
    }

    data = {
        'sourceId': fileId,
        'messages': [
            {
                'role': 'user',
                'content': message,
            }
        ]
    }
    print(data)
    return requests.post(
        'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)


@app.route('/chat', methods=['POST'])
def chat():
    response = {}
    
    if 'fileId' not in request.form or 'message' not in request.form:
        response['error'] = 'No file id or message'
        return response, 400

    fileId = request.form['fileId']
    message = request.form['message']
    if not is_file_id_in_csv(fileId):
        response['error'] = 'File not found'
        return response, 404

    chat_pdf_response = send_message_to_chat_pdf(fileId, message)
    print(chat_pdf_response.text)
    print(chat_pdf_response.status_code)
    if chat_pdf_response.status_code == 200:
        return chat_pdf_response.json(), 200
    else:
        return chat_pdf_response.text, chat_pdf_response.status_code


if __name__ == '__main__':
    app.run(ssl_context=(cert_file, key_file), port=port)
