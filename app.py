from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from deep_translator import GoogleTranslator
import PyPDF2
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Updated Language List (More Indian & Global Languages)
SUPPORTED_LANGUAGES = {
    'en': 'English', 'hi': 'Hindi', 'bn': 'Bengali', 'te': 'Telugu', 'mr': 'Marathi',
    'ta': 'Tamil', 'ur': 'Urdu', 'gu': 'Gujarati', 'kn': 'Kannada', 'ml': 'Malayalam',
    'pa': 'Punjabi', 'or': 'Odia', 'as': 'Assamese', 'sa': 'Sanskrit', 'ne': 'Nepali',
    'sd': 'Sindhi', 'si': 'Sinhala', 'th': 'Thai', 'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)', 'fr': 'French', 'de': 'German', 'es': 'Spanish',
    'it': 'Italian', 'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic'
}

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:  # Accept any username and password
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Please enter both username and password.')

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Translation Page
@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    username = session.get('username', 'Guest')
    return render_template('index.html', languages=SUPPORTED_LANGUAGES, username=username)

# Text Translation
@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data.get('text')
        src_lang = data.get('src_lang')
        dest_lang = data.get('dest_lang')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        translated_text = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
        return jsonify({'translated_text': translated_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PDF Upload and Translation
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text = ''
        for page in pdf_reader.pages:
            extracted_text += page.extract_text() + '\n'

        dest_lang = request.form.get('dest_lang', 'hi')  # Default to Hindi
        translated_text = GoogleTranslator(source='en', target=dest_lang).translate(extracted_text)

        return jsonify({'extracted_text': extracted_text, 'translated_text': translated_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
