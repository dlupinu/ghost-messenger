import os
from flask import Flask, render_template, request
from cryptography.fernet import Fernet

app = Flask(__name__)

# --- GESTIONE CHIAVE SEGRETA PRO ---
# Legge la chiave dalle impostazioni di Render (Environment Variables)
key_env = os.environ.get('CHIAVE_SEGRETA')

if key_env:
    # Se siamo su Render e abbiamo impostato la variabile
    key = key_env.encode()
else:
    # Se sei sul tuo PC e la variabile non c'è, ne crea una temporanea
    # NOTA: Sul PC i messaggi vecchi non funzioneranno al riavvio, ma su Render sì!
    key = Fernet.generate_key()

cipher = Fernet(key)
# -------------------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form.get('message', '')
    if msg:
        encrypted = cipher.encrypt(msg.encode()).decode()
        return render_template('index.html', encrypted=encrypted)
    return render_template('index.html')

@app.route('/decrypt', methods=['POST'])
def decrypt_msg():
    code = request.form.get('code', '')
    if code:
        try:
            decrypted = cipher.decrypt(code.encode()).decode()
        except Exception:
            decrypted = "ERRORE: Il codice è corrotto o la chiave è cambiata!"
        return render_template('index.html', decrypted=decrypted)
    return render_template('index.html')

if __name__ == '__main__':
    # Usiamo la porta corretta per Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
