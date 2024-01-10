from flask import Flask, request, render_template
from flask import Blueprint

import os
import requests
import csv

# Define the path for the upload folder
UPLOAD_FOLDER = 'server/lcachat/uploads/'
SOURCE_IDS_FILE = os.path.join(UPLOAD_FOLDER, 'source_ids.csv')

lca_chat = Blueprint('lca_chat', __name__)
 

def get_file_name_from_file_id(fileId):
    with open(SOURCE_IDS_FILE, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 2:
                fileName, fileIdFromCsv = row
                if fileId.strip() == fileIdFromCsv.strip():
                    return fileName
    return None


def write_to_csv_file(col1, col2):
    with open(SOURCE_IDS_FILE, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([col1, ' ' + col2])


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


@lca_chat.route('/lcachat-upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    # Save the file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Upload the file to the server
    files = [
        ('file', ('file', open(filepath, 'rb'), 'application/octet-stream'))
    ]
    os.remove(filepath)

    headers = {
        'x-api-key': 'sec_p8RhLwo5kE14CFKTFUefCjirVdtvwiGR'
    }

    chat_pdf_response = requests.post(
        'https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)

    response = {}
    if chat_pdf_response.status_code == 200:
        response['fileId'] = chat_pdf_response.json()['sourceId']
        response['fileName'] = file.filename
        
        # Save fileId and file.filename to the CSV file
        write_to_csv_file(file.filename, ' ' + response['fileId'])

    else:
        response['error'] = chat_pdf_response.text
        return response, chat_pdf_response.status_code

    return response, 200



@lca_chat.route('/lcachat-resume', methods=['POST'])
def resume_file():
    response = {}
    
    if 'fileId' not in request.form:
        response['error'] = 'No file id'
        return response, 400

    fileId = request.form['fileId']
    file_name = get_file_name_from_file_id(fileId)
    if not file_name:
        response['error'] = 'File not found'
        return response, 404

    response['fileId'] = fileId
    response['fileName'] = file_name
    return response, 200


@lca_chat.route('/lcachat-chat', methods=['POST'])
def chat():
    response = {}
    
    if 'fileId' not in request.form or 'message' not in request.form:
        response['error'] = 'No file id or message'
        return response, 400

    fileId = request.form['fileId']
    message = request.form['message']
    file_name = get_file_name_from_file_id(fileId)
    if not file_name:
        response['error'] = 'File not found'
        return response, 404

    chat_pdf_response = send_message_to_chat_pdf(fileId, message)
    print(chat_pdf_response.text)
    print(chat_pdf_response.status_code)
    if chat_pdf_response.status_code == 200:
        return chat_pdf_response.json(), 200
    else:
        return chat_pdf_response.text, chat_pdf_response.status_code


@lca_chat.route('/lcachat/chatbot.html', methods=['GET'])
def chatbot_html():
    fileId = request.args.get('fileId')
    fileName = request.args.get('fileName')
    return render_template('lcachat/chatbot.html', fileId=fileId, fileName=fileName)