import os
from flask import Flask, render_template, request
from cryptography.fernet import Fernet

app = Flask(__name__)

# --- GESTIONE CHIAVE SEGRETA ---
KEY_FILE = "secret.key"

def load_or_create_key():
    # Se il file della chiave esiste, lo legge
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        # Se non esiste, ne crea una nuova e la salva
        new_key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(new_key)
        return new_key

# Carichiamo la chiave definitiva
key = load_or_create_key()
cipher = Fernet(key)
# ------------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form['message']
    encrypted = cipher.encrypt(msg.encode()).decode()
    return render_template('index.html', encrypted=encrypted)

@app.route('/decrypt', methods=['POST'])
def decrypt_msg():
    code = request.form['code']
    try:
        decrypted = cipher.decrypt(code.encode()).decode()
    except Exception:
        decrypted = "ERRORE: Il codice è corrotto o la chiave è sbagliata!"
    return render_template('index.html', decrypted=decrypted)

if __name__ == '__main__':
    app.run(debug=True)