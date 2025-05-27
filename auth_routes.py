from flask import Blueprint, request, jsonify
from models import User
from database import db
import jwt
from datetime import datetime, timedelta
from functools import wraps
from config import Config

auth_bp = Blueprint('auth', __name__)

# --- Helper JWT (VULN: Algoritma None, Secret Key Lemah) ---
def create_jwt_token(user_id, username, is_admin):
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    try:
        # VULN 7: Ini akan tetap menjadi titik untuk demonstrasi,
        # tapi pastikan 'algorithms=['HS256']' ada untuk fungsi normal
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        # SOLUSI: Mengembalikan 2 nilai bahkan saat berhasil
        return payload, 200 # Mengembalikan payload dan status code 200 OK
    except jwt.ExpiredSignatureError:
        return {'message': 'Token has expired'}, 401
    except jwt.InvalidTokenError:
        return {'message': 'Invalid token'}, 401

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1] # Bearer <token>
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        # Panggilan yang sekarang akan selalu menerima 2 nilai
        current_user_data, status_code = verify_jwt_token(token)
        
        # Logika sekarang akan lebih jelas karena status_code selalu tersedia
        if status_code == 200: # Jika verifikasi berhasil (status 200 OK)
            # VULN 8: Langsung percaya payload dari JWT tanpa verifikasi ulang di DB
            request.current_user = User.query.get(current_user_data['user_id'])
            if not request.current_user:
                return jsonify({'message': 'User not found!'}), 401
            # VULN 4: Langsung pakai is_admin dari JWT, bisa dipalsukan
            request.current_user.is_admin = current_user_data.get('is_admin', False) 
        else: # Jika ada error dari verify_jwt_token (status 401)
            return jsonify(current_user_data), status_code # Mengembalikan error dari verify_jwt_token
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    @auth_required
    def decorated_function(*args, **kwargs):
        if not request.current_user.is_admin: # VULN 4: Mengandalkan is_admin dari JWT
            return jsonify({'message': 'Admin privilege required!'}), 403
        return f(*args, **kwargs)
    return decorated_function
# --- END Helper JWT ---


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # VULN 4: Mengizinkan 'is_admin' diset saat registrasi (Mass Assignment)
    is_admin = data.get('is_admin', False) 

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': 'Username already exists'}), 409

    new_user = User(username=username, is_admin=is_admin) # VULN 4: is_admin bisa diset
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    # VULN 3: Tidak ada Rate Limiting untuk percobaan login
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = create_jwt_token(user.id, user.username, user.is_admin)
    return jsonify({'token': token}), 200

@auth_bp.route('/profile', methods=['GET'])
@auth_required
def get_profile():
    # VULN 5: Mengungkap hash password jika disetel di to_dict
    return jsonify(request.current_user.to_dict(include_password=True)), 200

@auth_bp.route('/logout', methods=['POST'])
@auth_required
def logout():
    # Untuk token-based, logout biasanya hanya menghapus token di sisi klien.
    # Namun, untuk demo, kita bisa pura-pura melakukan 'revoke' token.
    # VULN: Tidak ada sistem blacklist token yang sebenarnya.
    return jsonify({'message': 'Logged out successfully (token needs to be discarded by client)'}), 200