from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # VULN 3: Method hashing default 'pbkdf2:sha256' sudah cukup baik,
    # tapi kita akan simulasikan brute-force tanpa rate-limit
    password_hash = db.Column(db.String(128), nullable=False)
    
    # VULN 4: Mass Assignment - Kolom 'is_admin' yang bisa diubah via API
    is_admin = db.Column(db.Boolean, default=False)

    notes = db.relationship('Note', backref='author', lazy=True)

    def set_password(self, password):
        # Werkzeug.security sudah pakai salt dan iterasi default.
        # Untuk simulasi vuln, kita bisa abaikan rate-limit di login
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_password=False):
        data = {
            'id': self.id,
            'username': self.username,
            'is_admin': self.is_admin # VULN 4: Mengungkap is_admin
        }
        if include_password:
            data['password_hash'] = self.password_hash # VULN 5: Bocorkan hash password
        return data

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'author_username': self.author.username
        }