from flask import Flask,render_template, redirect, request, url_for
from server.lcachat.lcachat import lca_chat

app = Flask(__name__, template_folder='client')
app.register_blueprint(lca_chat)

# Set the port number and certificate/key file paths
port = 443
cert_file = 'server/ssl-certs/fullchain.pem'
key_file = 'server/ssl-certs/privkey.pem'


@app.route("/")
def home():
    return redirect(url_for('lca_chat.fileUpload_html'))


if __name__ == '__main__':
    app.run(
        '0.0.0.0',
        ssl_context=(cert_file, key_file), 
        port=port,
        debug=True)
    