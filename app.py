import os
import io
from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
from PIL import Image
import stepic

app = Flask(__name__)

# --- GESTIONE CHIAVE SEGRETA (Testo) ---
KEY_FILE = "secret.key"

def load_or_create_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        new_key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(new_key)
        return new_key

key = load_or_create_key()
cipher = Fernet(key)
# ------------------------------

@app.route('/')
def home():
    return render_template('index.html')

# --- 1. CRIPTAZIONE TESTO (BOX 1) ---
@app.route('/encrypt', methods=['POST'])
def encrypt_msg():
    msg = request.form.get('message')
    # Nota: La password qui viene usata come "sale" aggiuntivo o semplicemente ignorata 
    # se vuoi usare solo la chiave fissa. Per ora manteniamo la tua logica Fernet.
    if msg:
        encrypted = cipher.encrypt(msg.encode()).decode()
        return render_template('index.html', encrypted=encrypted)
    return render_template('index.html')

# --- 2. STEGANOGRAFIA: NASCONDI (BOX 2) ---
@app.route('/stego_hide', methods=['POST'])
def stego_hide():
    file = request.files.get('cover_img')
    message = request.form.get('hidden_msg')
    password = request.form.get('psw')

    if file and message and password:
        try:
            # Apri l'immagine e convertila in RGB
            img = Image.open(file.stream).convert('RGB')
            
            # Formato segreto: password::messaggio
            secret_string = f"{password}::{message}"
            
            # Nascondi i dati nei pixel
            encoded_img = stepic.encode(img, secret_string.encode('utf-8'))
            
            # Salva in un buffer come PNG (il JPEG distruggerebbe il messaggio)
            img_io = io.BytesIO()
            encoded_img.save(img_io, 'PNG')
            img_io.seek(0)
            
            return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='ghost_image.png')
        except Exception as e:
            return f"Errore durante la steganografia: {e}"
    return "Campi mancanti!"

# --- 3. DECRIPTA TUTTO (BOX 3) ---
@app.route('/decrypt_all', methods=['POST'])
def decrypt_all():
    code = request.form.get('code') # Testo rosa
    file = request.files.get('file_to_decrypt') # Immagine .png
    password = request.form.get('psw')

    # CASO A: Decriptazione Immagine
    if file and file.filename != '':
        try:
            img = Image.open(file.stream)
            decoded_bytes = stepic.decode(img)
            decoded_str = decoded_bytes.decode('utf-8')

            if "::" in decoded_str:
                stored_pwd, hidden_msg = decoded_str.split("::", 1)
                if stored_pwd == password:
                    res = f"IMMAGINE SBLOCCATA: {hidden_msg}"
                else:
                    res = "ERRORE: Password immagine errata!"
            else:
                res = "ERRORE: Nessun messaggio trovato in questa immagine."
        except Exception:
            res = "ERRORE: Immagine non valida o corrotta."
        return render_template('index.html', decrypted=res)

    # CASO B: Decriptazione Codice Rosa (Fernet)
    if code:
        try:
            decrypted = cipher.decrypt(code.encode()).decode()
            # Se vuoi aggiungere un controllo password anche qui, dovresti implementarlo nella logica Fernet
            res = f"MESSAGGIO SBLOCCATO: {decrypted}"
        except Exception:
            res = "ERRORE: Codice corrotto o chiave non valida!"
        return render_template('index.html', decrypted=res)

    return render_template('index.html', decrypted="Inserisci un codice o un file.")

# Vecchia rotta mantenuta per compatibilità o rimovibile
@app.route('/decrypt', methods=['POST'])
def decrypt_msg():
    return decrypt_all()

if __name__ == '__main__':
    app.run(debug=True)
