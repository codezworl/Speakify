from flask import Flask, render_template, request, send_file, flash, Response
from gtts import gTTS
import os
import io
from werkzeug.utils import secure_filename
from deep_translator import GoogleTranslator
import uuid  # To generate unique file names
from langdetect import detect, LangDetectException, DetectorFactory

DetectorFactory.seed = 0  # To ensure reproducibility in language detection

# Define the Flask application
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Set the UPLOAD_FOLDER to a directory relative to the script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage for Vercel deployment
MEMORY_STORAGE = {}

# Language mapping for deep-translator
LANGUAGES = {
    'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian',
    'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian',
    'bg': 'bulgarian', 'ca': 'catalan', 'ceb': 'cebuano', 'zh': 'chinese', 'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish',
    'nl': 'dutch', 'en': 'english', 'eo': 'esperanto', 'et': 'estonian', 'fi': 'finnish', 'fr': 'french',
    'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian', 'de': 'german', 'el': 'greek', 'gu': 'gujarati',
    'ht': 'haitian creole', 'ha': 'hausa', 'haw': 'hawaiian', 'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong',
    'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish', 'it': 'italian',
    'ja': 'japanese', 'jv': 'javanese', 'kn': 'kannada', 'kk': 'kazakh', 'km': 'khmer', 'ko': 'korean',
    'ku': 'kurdish', 'ky': 'kyrgyz', 'lo': 'lao', 'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian',
    'lb': 'luxembourgish', 'mk': 'macedonian', 'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam',
    'mt': 'maltese', 'mi': 'maori', 'mr': 'marathi', 'mn': 'mongolian', 'my': 'myanmar (burmese)',
    'ne': 'nepali', 'no': 'norwegian', 'ny': 'nyanja (chichewa)', 'or': 'odia (oriya)', 'ps': 'pashto',
    'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi', 'ro': 'romanian', 'ru': 'russian',
    'sm': 'samoan', 'gd': 'scots gaelic', 'sr': 'serbian', 'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi',
    'si': 'sinhala (sinhalese)', 'sk': 'slovak', 'sl': 'slovenian', 'so': 'somali', 'es': 'spanish',
    'su': 'sundanese', 'sw': 'swahili', 'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'tt': 'tatar',
    'te': 'telugu', 'th': 'thai', 'tr': 'turkish', 'tk': 'turkmen', 'uk': 'ukrainian', 'ur': 'urdu',
    'ug': 'uyghur', 'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish',
    'yo': 'yoruba', 'zu': 'zulu'
}

def generate_unique_filename():
    return str(uuid.uuid4()) + ".mp3"

@app.route("/", methods=["GET", "POST"])
def index():
    detected_language_name = None  # Variable to store full language name

    if request.method == "POST":
        text = request.form.get("text")
        language = request.form.get("language")
        file = request.files.get("file")

        if file and file.filename.endswith('.txt'):
            filename = secure_filename(file.filename)
            # For local development
            if not os.environ.get('VERCEL_ENV'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                with open(file_path, 'r') as f:
                    text = f.read()
            else:
                # For Vercel deployment - read directly from memory
                text = file.read().decode('utf-8')

            # Detect language of the uploaded file
            try:
                detected_language = detect(text)
                detected_language_name = LANGUAGES.get(detected_language)  # Get full language name
                flash(f"Detected language: {detected_language_name} ({detected_language})", "info")
            except LangDetectException:
                flash("Could not detect language. Please provide more text or choose a language manually.", "error")
                return render_template("index.html", detected_language=None, detected_language_name=None)

        if text and language and language != "auto":
            # Check if the selected language is valid
            if language not in LANGUAGES:
                flash("Invalid destination language selected.", "error")
                return render_template("index.html", detected_language_name=detected_language_name)

            # Translate text to the selected language
            try:
                translator = GoogleTranslator(source='auto', target=language)
                translated_text = translator.translate(text)
            except Exception as e:
                flash(f"Translation failed: {e}", "error")
                return render_template("index.html", detected_language_name=detected_language_name)

            # Convert translated text to speech
            tts = gTTS(translated_text, lang=language)
            output_filename = generate_unique_filename()
            
            # For local development
            if not os.environ.get('VERCEL_ENV'):
                output_file = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
                tts.save(output_file)
            else:
                # For Vercel deployment - store in memory
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                MEMORY_STORAGE[output_filename] = mp3_fp.read()

            return render_template("index.html", message="Conversion successful.", audio=output_filename, detected_language_name=detected_language_name)
        else:
            flash("Please provide text or upload a file and select a language.", "error")
    
    return render_template("index.html", detected_language_name=detected_language_name)

@app.route("/download/<filename>")
def download(filename):
    # For local development
    if not os.environ.get('VERCEL_ENV'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
    else:
        # For Vercel deployment - serve from memory
        if filename in MEMORY_STORAGE:
            return Response(
                MEMORY_STORAGE[filename],
                mimetype="audio/mpeg",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    
    flash("File not found.", "error")
    return render_template("index.html")

@app.route("/play/<filename>")
def play(filename):
    # For local development
    if not os.environ.get('VERCEL_ENV'):
        audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(audio_file_path):
            return send_file(audio_file_path, mimetype="audio/mpeg")
    else:
        # For Vercel deployment - serve from memory
        if filename in MEMORY_STORAGE:
            return Response(MEMORY_STORAGE[filename], mimetype="audio/mpeg")
    
    flash("File not found.", "error")
    return render_template("index.html")

# For local development
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

# This is needed for Vercel deployment
# The WSGI application should be named 'app' for Vercel to detect it correctly
