from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return 'No file part'
    
    file = request.files['document']
    
    if file.filename == '':
        return 'No selected file'
    
    filepath = os.path.join('/path/to/save/documents', file.filename)
    file.save(filepath)
    
    print(f"File path: {file}")
    
    return 'File uploaded successfully'

if __name__ == '__main__':
    app.run(debug=True)
