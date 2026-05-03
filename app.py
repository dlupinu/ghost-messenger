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

# --- CRIPTAZIONE TESTO (Già esistente) ---
@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form.get('message', '')
    if msg:
        encrypted = cipher.encrypt(msg.encode()).decode()
        return render_template('index.html', encrypted=encrypted)
    return render_template('index.html')

# --- NOVITÀ: CRIPTAZIONE IMMAGINE ---
@app.route('/encrypt_file', methods=['POST'])
def encrypt_file():
    file = request.files.get('file')
    if file:
        file_data = file.read()
        # Criptiamo i byte dell'immagine
        encrypted_data = cipher.encrypt(file_data)
        # Trasformiamo i byte criptati in una stringa leggibile (Base64)
        encoded_text = base64.b64encode(encrypted_data).decode()
        return render_template('index.html', encrypted=encoded_text, is_file=True)
    return render_template('index.html')

@app.route('/decrypt', methods=['POST'])
def decrypt_msg():
    code = request.form.get('code', '')
    if code:
        try:
            # Decodifichiamo il Base64 e poi decriptiamo con Fernet
            decrypted_data = cipher.decrypt(base64.b64decode(code.encode()))
            
            # Se i primi byte sembrano un'immagine, la rimandiamo come file
            # Altrimenti la trattiamo come testo
            try:
                text_msg = decrypted_data.decode('utf-8')
                return render_template('index.html', decrypted=text_msg)
            except:
                # Se non è testo, è un'immagine! La mandiamo al browser
                return send_file(
                    io.BytesIO(decrypted_data),
                    mimetype='image/png',
                    as_attachment=True,
                    download_name="ghost_image.png"
                )
        except Exception as e:
            return render_template('index.html', decrypted=f"ERRORE: Codice non valido! {str(e)}")
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
