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

    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()

        # VULN 10: SQL Injection
        cursor.execute(f"INSERT INTO note (title, content, user_id) VALUES ('{title}', '{content}', {request.current_user.id})")

        # Ambil ID terakhir yang diinsert
        cursor.execute("SELECT last_insert_rowid()")
        last_id = cursor.fetchone()[0]

        # Ambil data yang baru dibuat
        cursor.execute(f"SELECT * FROM note WHERE id = {last_id}")
        row = cursor.fetchone()
        colnames = [desc[0] for desc in cursor.description]
        note_dict = dict(zip(colnames, row))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(note_dict), 201

    except Exception as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500


@note_bp.route('/notes/<int:note_id>', methods=['GET'])
@auth_required
def get_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'message': 'Note not found'}), 404
    
    # VULN 11: IDOR (Insecure Direct Object Reference) - Tidak ada cek kepemilikan
    # User A bisa lihat note User B hanya dengan mengubah ID di URL
    return jsonify(note.to_dict()), 200

@note_bp.route('/notes/view', methods=['POST'])
@auth_required
def get_note_post(note_id):
    data = request.get_json()
    id_notes = data.get('id')
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()

        # Vuln SQL Injection - ID langsung dimasukkan ke query tanpa sanitasi
        raw_query = f"SELECT * FROM note WHERE id = {id_notes}"
        cursor.execute(raw_query)

        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Note not found'}), 404

        # Ambil kolom dan buat dict dari hasil query
        colnames = [desc[0] for desc in cursor.description]
        note_dict = dict(zip(colnames, row))

        cursor.close()
        conn.close()

        return jsonify(note_dict), 200

    except Exception as e:
        return jsonify({'message': f'Query error: {str(e)}'}), 500

@note_bp.route('/notes/<int:note_id>', methods=['PUT'])
@auth_required
def update_note(note_id):
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()

        # Ambil data berdasarkan ID tanpa cek kepemilikan (VULN 11)
        cursor.execute(f"SELECT * FROM note WHERE id = {note_id}")
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Note not found'}), 404

        data = request.get_json()

        # Buat bagian SET dari query secara langsung (VULN 12 + SQL Injection)
        updates = []
        if 'title' in data:
            updates.append(f"title = '{data['title']}'")
        if 'content' in data:
            updates.append(f"content = '{data['content']}'")
        if 'user_id' in data:
            updates.append(f"user_id = {data['user_id']}")  # tidak dikutip = integer

        if not updates:
            cursor.close()
            conn.close()
            return jsonify({'message': 'No data provided'}), 400

        update_sql = f"UPDATE note SET {', '.join(updates)} WHERE id = {note_id}"
        cursor.execute(update_sql)
        conn.commit()

        # Ambil data baru
        cursor.execute(f"SELECT * FROM note WHERE id = {note_id}")
        updated_row = cursor.fetchone()
        colnames = [desc[0] for desc in cursor.description]
        note_dict = dict(zip(colnames, updated_row))

        cursor.close()
        conn.close()

        return jsonify(note_dict), 200

    except Exception as e:
        return jsonify({'message': f'Database error: {str(e)}'}), 500


@note_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@auth_required
def delete_note(note_id):
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'message': 'Note not found'}), 404
    
    # VULN 11: IDOR - Tidak ada cek kepemilikan

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
