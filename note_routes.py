from flask import Blueprint, request, jsonify
from models import Note, User
from database import db
from auth_routes import auth_required, admin_required # Import decorator

note_bp = Blueprint('notes', __name__)

@note_bp.route('/notes', methods=['GET'])
@auth_required
def get_notes():
    # VULN 9: Tidak ada filter berdasarkan user_id, user bisa lihat semua notes
    notes = Note.query.all() 
    return jsonify([note.to_dict() for note in notes]), 200

@note_bp.route('/notes', methods=['POST'])
@auth_required
def create_note():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        return jsonify({'message': 'Title and content are required'}), 400

    # VULN 10: SQL Injection - JIKA kita menggunakan raw SQL tanpa parameterized query
    # Ini adalah contoh raw SQL yang VULN jika langsung pakai f-string
    # try:
    #     conn = db.engine.raw_connection()
    #     cursor = conn.cursor()
    #     cursor.execute(f"INSERT INTO note (title, content, user_id) VALUES ('{title}', '{content}', {request.current_user.id})")
    #     conn.commit()
    #     cursor.close()
    #     conn.close()
    # except Exception as e:
    #     return jsonify({'message': f'Database error: {str(e)}'}), 500
    # SOLUSI AMAN: Menggunakan ORM SQLAlchemy secara default mencegah ini
    
    new_note = Note(title=title, content=content, user_id=request.current_user.id)
    db.session.add(new_note)
    db.session.commit()

    return jsonify(new_note.to_dict()), 201

@note_bp.route('/notes/<int:note_id>', methods=['GET'])
@auth_required
def get_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'message': 'Note not found'}), 404
    
    # VULN 11: IDOR (Insecure Direct Object Reference) - Tidak ada cek kepemilikan
    # User A bisa lihat note User B hanya dengan mengubah ID di URL
    return jsonify(note.to_dict()), 200

@note_bp.route('/notes/<int:note_id>', methods=['PUT'])
@auth_required
def update_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'message': 'Note not found'}), 404
    
    # VULN 11: IDOR - Tidak ada cek kepemilikan
    # if note.user_id != request.current_user.id: # Solusi untuk IDOR
    #     return jsonify({'message': 'Forbidden'}), 403

    data = request.get_json()
    # VULN 12: Mass Assignment - Menerima semua field dari request.json
    # Jika ada field 'user_id' di data, bisa diubah!
    if 'title' in data:
        note.title = data['title']
    if 'content' in data:
        note.content = data['content']
    # if 'user_id' in data: # VULN 12: Jika ini diizinkan
    #     note.user_id = data['user_id'] 

    db.session.commit()
    return jsonify(note.to_dict()), 200

@note_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@auth_required
def delete_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'message': 'Note not found'}), 404
    
    # VULN 11: IDOR - Tidak ada cek kepemilikan
    # if note.user_id != request.current_user.id: # Solusi untuk IDOR
    #     return jsonify({'message': 'Forbidden'}), 403

    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Note deleted successfully'}), 200

# VULN 13: Admin endpoint tanpa validasi is_admin dari DB
@note_bp.route('/admin/users', methods=['GET'])
@admin_required # Mengandalkan is_admin dari JWT payload (VULN 4)
def get_all_users_for_admin():
    users = User.query.all()
    # VULN 5: to_dict(include_password=True) akan bocorkan hash password
    return jsonify([user.to_dict(include_password=True) for user in users]), 200