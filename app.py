import os
from flask import Flask, render_template, request
from cryptography.fernet import Fernet

app = Flask(__name__)

# --- GESTIONE CHIAVE ---
KEY_FILE = "secret.key"
def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f: return f.read()
    new_key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f: f.write(new_key)
    return new_key

cipher = Fernet(load_or_create_key())

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form.get('message')
    if msg:
        encrypted = cipher.encrypt(msg.encode()).decode()
        return render_template('index.html', encrypted=encrypted)
    return render_template('index.html')

@app.route('/decrypt', methods=['POST'])
def decrypt_msg():
    code = request.form.get('code')
    if code:
        try:
            decrypted = cipher.decrypt(code.strip().encode()).decode()
        except:
            decrypted = "ERRORE: Codice non valido o corrotto."
        return render_template('index.html', decrypted=decrypted)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
