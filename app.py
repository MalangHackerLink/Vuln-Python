from flask import Flask, jsonify
from config import Config
from database import db, migrate
from models import User, Note # Impor model untuk db.create_all()
from auth_routes import auth_bp
from note_routes import note_bp

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi Flask Extensions
db.init_app(app)
migrate.init_app(app, db)

# Registrasi Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(note_bp, url_prefix='/api')

# --- ERROR HANDLING (VULN: Pesan error terlalu detail) ---
@app.errorhandler(404)
def not_found_error(error):
    # VULN 14: Pesan error mungkin tidak konsisten atau terlalu generic
    return jsonify({'error': 'Resource Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    # VULN 15: Error ini bisa membocorkan stack trace jika debug=True
    # dan jika debug=False, pesan ini tidak cukup informatif untuk logging
    return jsonify({'error': 'Internal Server Error', 'details': str(error)}), 500
# --- END ERROR HANDLING ---

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the VULNERABLE Flask API! For educational purposes only."})

if __name__ == '__main__':
    with app.app_context():
        # Membuat tabel database jika belum ada
        db.create_all()
    # VULN 16: debug=True di sini berarti informasi sensitif bisa bocor
    # Seharusnya hanya False di lingkungan produksi
    app.run(debug=True)