import os
import time
import base64
from flask import Flask, render_template, request
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = Flask(__name__)

def get_user_cipher(password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'ghost_salt_fixed',
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return Fernet(key)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form.get('message')
    pwd = request.form.get('psw')
    expiry = int(request.form.get('expiry', 1))
    if msg and pwd:
        expiry_ts = int(time.time()) + (expiry * 3600)
        data = f"{expiry_ts}|{msg}"
        cipher = get_user_cipher(pwd)
        encrypted = cipher.encrypt(data.encode()).decode()
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
            expiry_str, message = decrypted_data.split('|', 1)
            if int(time.time()) > int(expiry_str):
                res = "🚨 MESSAGGIO SCADUTO E DISTRUTTO!"
            else:
                res = message
        except:
            res = "❌ Password errata o codice corrotto."
        return render_template('index.html', decrypted=res)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
