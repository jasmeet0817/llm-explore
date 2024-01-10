from flask import Flask,render_template, request
from server.lcachat.lcachat import lca_chat

app = Flask(__name__, template_folder='client')
app.register_blueprint(lca_chat)

# Set the port number and certificate/key file paths
port = 5000
# cert_file = 'ssl-certs/fullchain.pem'
# key_file = 'ssl-certs/privkey.pem'


@app.route("/")
def home():
    return render_template('lcachat/fileUpload.html')


if __name__ == '__main__':
    app.run(
        # ssl_context=(cert_file, key_file), 
        port=port,
        debug=True)
    