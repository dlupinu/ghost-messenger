import os
import base64
from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import io

app = Flask(__name__)

# --- CONFIGURAZIONE CHIAVE ---
key_env = os.environ.get('CHIAVE_SEGRETA')
key = key_env.encode() if key_env else Fernet.generate_key()
cipher = Fernet(key)

@app.route('/')
def home():
    return render_template('index.html')

# --- 1. GESTIONE TESTO (Copia/Incolla) ---
@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form.get('message', '')
    if msg:
        encrypted = cipher.encrypt(msg.encode()).decode()
        return render_template('index.html', encrypted=encrypted)
    return render_template('index.html')

# --- 2. GESTIONE FILE (Download .ghost) ---
@app.route('/encrypt_file', methods=['POST'])
def encrypt_file():
    file = request.files.get('file')
    if file:
        file_data = file.read()
        # Criptiamo i byte originali
        encrypted_data = cipher.encrypt(file_data)
        
        # Inviamo il file criptato come download
        return send_file(
            io.BytesIO(encrypted_data),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name="messaggio_segreto.ghost"
        )
    return render_template('index.html')

# --- 3. DECRIPTA TUTTO (Testo o File) ---
@app.route('/decrypt', methods=['POST'])
def decrypt_msg():
    # Prova prima a vedere se l'utente ha caricato un file .ghost
    file = request.files.get('file_to_decrypt')
    code = request.form.get('code', '')

    try:
        if file and file.filename != '':
            # Decripta il FILE
            encrypted_data = file.read()
            decrypted_data = cipher.decrypt(encrypted_data)
            return send_file(
                io.BytesIO(decrypted_data),
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name="file_sbloccato.png" # Puoi rinominarlo dopo
            )
        
        elif code:
            # Decripta il TESTO (Base64)
            decrypted_data = cipher.decrypt(code.encode()).decode()
            return render_template('index.html', decrypted=decrypted_data)
            
    except Exception as e:
        return render_template('index.html', decrypted="ERRORE: Chiave errata o file corrotto!")
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
