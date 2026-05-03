import os
import time
from flask import Flask, render_template, request
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = Flask(__name__)

# Funzione per generare una chiave derivata dalla password dell'utente
def get_user_cipher(password):
    password_bytes = password.encode()
    salt = b'ghost_salt_123' # Un salt fisso per semplicità
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return Fernet(key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form.get('message')
    pwd = request.form.get('psw')
    expiry_hours = int(request.form.get('expiry', 1)) # Default 1 ora

    if msg and pwd:
        # Calcoliamo il timestamp di scadenza
        expiry_timestamp = int(time.time()) + (expiry_hours * 3600)
        # Formato interno: scadenza|messaggio
        data_to_encrypt = f"{expiry_timestamp}|{msg}"
        
        cipher = get_user_cipher(pwd)
        encrypted = cipher.encrypt(data_to_encrypt.encode()).decode()
        return render_template('index.html', encrypted=encrypted)
    return render_template('index.html')

@app.route('/decrypt', methods=['POST'])
def decrypt_msg():
    code = request.form.get('code')
    pwd = request.form.get('psw')

    if code and pwd:
        try:
            cipher = get_user_cipher(pwd)
            decrypted_data = cipher.decrypt(code.strip().encode()).decode()
            
            # Separiamo timestamp e messaggio
            expiry_str, message = decrypted_data.split('|', 1)
            
            # Controllo scadenza
            if int(time.time()) > int(expiry_str):
                res = "🚨 ERRORE: Questo messaggio è scaduto e si è autodistrutto!"
            else:
                res = message
        except:
            res = "❌ ERRORE: Password errata o codice corrotto."
        return render_template('index.html', decrypted=res)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
