import os
import base64
import hashlib
from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import io

app = Flask(__name__)

# --- CONFIGURAZIONE SISTEMA ---
key_env = os.environ.get('CHIAVE_SEGRETA', 'chiave-di-backup-molto-lunga')

def get_cipher(user_psw):
    # Uniamo la chiave di sistema alla password dell'utente per massima sicurezza
    combined = (key_env + user_psw).encode()
    hash_key = hashlib.sha256(combined).digest()
    fernet_key = base64.urlsafe_b64encode(hash_key)
    return Fernet(fernet_key)

@app.route('/')
def home():
    return render_template('index.html')

# --- CRIPTA TESTO ---
@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form.get('message', '')
    psw = request.form.get('psw', '') # Password scelta dall'utente
    if msg and psw:
        cipher = get_cipher(psw)
        encrypted = cipher.encrypt(msg.encode()).decode()
        return render_template('index.html', encrypted=encrypted)
    return render_template('index.html')

# --- CRIPTA FILE ---
@app.route('/encrypt_file', methods=['POST'])
def encrypt_file():
    file = request.files.get('file')
    psw = request.form.get('psw', '')
    if file and psw:
        cipher = get_cipher(psw)
        encrypted_data = cipher.encrypt(file.read())
        return send_file(io.BytesIO(encrypted_data), as_attachment=True, download_name="segreto.ghost")
    return render_template('index.html')

# --- DECRIPTA TUTTO ---
@app.route('/decrypt', methods=['POST'])
def decrypt_msg():
    psw = request.form.get('psw', '')
    code = request.form.get('code', '')
    file = request.files.get('file_to_decrypt')
    
    if not psw:
        return render_template('index.html', decrypted="ERRORE: Inserisci la password!")

    try:
        cipher = get_cipher(psw)
        if file and file.filename != '':
            decrypted_data = cipher.decrypt(file.read())
            return send_file(io.BytesIO(decrypted_data), as_attachment=True, download_name="sbloccato.png")
        elif code:
            decrypted_text = cipher.decrypt(code.encode()).decode()
            return render_template('index.html', decrypted=decrypted_text)
    except Exception:
        return render_template('index.html', decrypted="ERRORE: Password errata o dati corrotti!")
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
