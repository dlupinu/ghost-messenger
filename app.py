import os
import io
from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
from PIL import Image
import stepic

app = Flask(__name__)

# --- CHIAVE PER I TESTI ---
KEY_FILE = "secret.key"
def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f: return f.read()
    new_key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f: f.write(new_key)
    return new_key

cipher = Fernet(load_key())

@app.route('/')
def home():
    return render_template('index.html')

# --- SEZIONE TESTO ---
@app.route('/text_encrypt', methods=['POST'])
def text_encrypt():
    msg = request.form.get('message')
    if msg:
        encrypted = cipher.encrypt(msg.encode()).decode()
        return render_template('index.html', encrypted_text=encrypted)
    return render_template('index.html')

@app.route('/text_decrypt', methods=['POST'])
def text_decrypt():
    code = request.form.get('code')
    try:
        decrypted = cipher.decrypt(code.encode()).decode()
    except:
        decrypted = "Codice errato o corrotto."
    return render_template('index.html', decrypted_text=decrypted)

# --- SEZIONE IMMAGINI ---
@app.route('/img_hide', methods=['POST'])
def img_hide():
    file = request.files.get('cover_img')
    msg = request.form.get('hidden_msg')
    pwd = request.form.get('psw')
    if file and msg and pwd:
        img = Image.open(file.stream).convert('RGB')
        data = f"{pwd}::{msg}".encode('utf-8')
        encoded_img = stepic.encode(img, data)
        img_io = io.BytesIO()
        encoded_img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name='ghost.png')
    return "Mancano dati!"

@app.route('/img_reveal', methods=['POST'])
def img_reveal():
    file = request.files.get('ghost_img')
    pwd = request.form.get('psw')
    if file and pwd:
        try:
            img = Image.open(file.stream)
            decoded = stepic.decode(img).decode('utf-8')
            if "::" in decoded:
                stored_pwd, msg = decoded.split("::", 1)
                if stored_pwd == pwd:
                    return render_template('index.html', decrypted_img=msg)
            return render_template('index.html', decrypted_img="Password errata o nessun messaggio.")
        except:
            return render_template('index.html', decrypted_img="File non valido.")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
